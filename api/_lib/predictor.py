"""
ML predictor logic — shared by all Vercel serverless functions.
Loads best_model.pkl once and serves predictions.

The model lives at:  /models/best_model.pkl  (relative to project root)
"""
from pathlib import Path
from typing import Any
import json
import joblib
import pandas as pd

# Resolve model paths robustly regardless of how Vercel mounts the filesystem.
# api/_lib/predictor.py  →  ../../models/
_HERE = Path(__file__).resolve()
# Try two common layouts:
#   Layout A: api/_lib/predictor.py  →  ../../models/
#   Layout B: api/predictor.py       →  ../models/
_CANDIDATES = [
    _HERE.parent.parent.parent / "models",  # Layout A
    _HERE.parent.parent / "models",          # Layout B
]
MODEL_DIR = next((p for p in _CANDIDATES if (p / "best_model.pkl").exists()), _CANDIDATES[0])
MODEL_PATH = MODEL_DIR / "best_model.pkl"
METRICS_PATH = MODEL_DIR / "model_metrics.json"

FEATURES = [
    "founded_year", "country", "region", "industry", "funding_round",
    "funding_amount_usd", "lead_investor", "co_investors", "employee_count",
    "estimated_revenue_usd", "estimated_valuation_usd", "tags",
    "funding_year", "funding_month",
]

_model = None


def get_model():
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. "
                "Make sure models/best_model.pkl is committed to the repository."
            )
        _model = joblib.load(MODEL_PATH)
    return _model


# ---------------------------------------------------------------------------
# Explanations
# ---------------------------------------------------------------------------

def _explanations(row: pd.DataFrame, model) -> list[dict[str, Any]]:
    importances = getattr(model, "feature_importances_", None)
    if importances is None:
        coefs = getattr(model, "coef_", None)
        if coefs is not None:
            importances = [abs(c) for c in coefs[0]]
    if importances is None:
        return []
    total = sum(importances) or 1
    importances = [i / total for i in importances] # normalize
    names = list(getattr(model, "feature_names_in_", FEATURES))
    values = row.iloc[0].to_dict()
    items = [
        {
            "feature": str(n),
            "importance": float(v),
            "value": float(values.get(n, 0)),
        }
        for n, v in zip(names, importances)
    ]
    return sorted(items, key=lambda x: x["importance"], reverse=True)[:6]


# ---------------------------------------------------------------------------
# Improvement suggestions (deterministic, based on raw field values)
# ---------------------------------------------------------------------------

def _improvements(x: dict[str, Any], success: float, explanations: list[dict[str, Any]]) -> list[str]:
    actions = []
    revenue = float(x.get("estimated_revenue_usd", 0) or 0)
    funding = float(x.get("funding_amount_usd", 0) or 0)
    employees = float(x.get("employee_count", 0) or 0)
    valuation = float(x.get("estimated_valuation_usd", 0) or 0)
    rounds = float(x.get("funding_round", 0) or 0)

    if revenue <= 0:
        actions.append(
            "Validate a measurable revenue path and run a small paid-user or pilot experiment."
        )
    elif revenue < 100_000:
        actions.append(
            "Strengthen early revenue validation: track conversion, retention and repeat usage before scaling."
        )
    if employees < 5:
        actions.append(
            "Check whether the current team can deliver the MVP; assign clear ownership for product and engineering."
        )
    if funding <= 0:
        actions.append(
            "Build a lean financing plan and validate the MVP before committing to a large funding requirement."
        )
    elif funding > 0 and revenue == 0:
        actions.append(
            "Tie future funding to measurable milestones so capital is connected to product and customer validation."
        )
    if valuation > 0 and revenue > 0 and valuation / revenue > 30:
        actions.append(
            "Validate the valuation assumption against revenue, growth and comparable companies rather than relying on a headline valuation."
        )
    if rounds <= 1:
        actions.append(
            "Focus on proving the core product and customer demand before adding complexity or pursuing additional rounds."
        )
    if success < 0.5:
        actions.append(
            "Prioritize the lowest-confidence business assumptions first and rerun the prediction after collecting stronger operating data."
        )
    else:
        actions.append(
            "Keep validating customer demand and unit economics; a model probability is not a guarantee of future success."
        )
    # Deduplicate, keep first 5
    out: list[str] = []
    for a in actions:
        if a not in out:
            out.append(a)
    return out[:5]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def predict_startup(x: dict[str, Any]) -> dict[str, Any]:
    """
    Run the ML model and return a structured prediction dict.

    x must contain all 14 numeric features listed in FEATURES.
    Missing features default to 0.0 rather than raising a KeyError.
    """
    model = get_model()
    # Build the feature row – use 0.0 as a safe default for missing fields
    row = {f: float(x.get(f, 0) or 0) for f in FEATURES}
    frame = pd.DataFrame([row], columns=FEATURES)

    probabilities = model.predict_proba(frame)[0]
    classes = list(model.classes_)
    probs = {int(c): float(p) for c, p in zip(classes, probabilities)}

    success = probs.get(1, 0.0)
    failure = probs.get(0, 0.0)
    prediction = 1 if success >= 0.5 else 0
    explanations = _explanations(frame, model)

    return {
        "prediction": prediction,
        "outcome": "Success" if prediction else "Failure",
        "success_probability": round(success, 4),
        "failure_probability": round(failure, 4),
        "confidence": round(max(success, failure), 4),
        "explanations": explanations,
        "improvements": _improvements(x, success, explanations),
        "disclaimer": (
            "These percentages are model estimates from the training data, not guarantees "
            "of startup success or failure. Suggested improvements are validation actions, "
            "not causal guarantees."
        ),
    }


def get_feature_importance() -> list[dict[str, Any]]:
    model = get_model()
    imps = getattr(model, "feature_importances_", None)
    if imps is None:
        coefs = getattr(model, "coef_", None)
        if coefs is not None:
            imps = [abs(c) for c in coefs[0]]
    if imps is None:
        return []
    total = sum(imps) or 1
    imps = [i / total for i in imps]
    names = list(getattr(model, "feature_names_in_", FEATURES))
    items = [{"feature": str(n), "importance": float(v)} for n, v in zip(names, imps)]
    return sorted(items, key=lambda x: x["importance"], reverse=True)


def get_metrics() -> dict[str, Any]:
    if METRICS_PATH.exists():
        return json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    return {
        "model": "RandomForestClassifier",
        "model_version": "7.0.0",
        "leakage_safe": True,
    }
