from pathlib import Path
from typing import Any
import json
import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "best_model.pkl"
METRICS_PATH = BASE_DIR / "models" / "model_metrics.json"
FEATURES = ["founded_year","country","region","industry","funding_round","funding_amount_usd","lead_investor","co_investors","employee_count","estimated_revenue_usd","estimated_valuation_usd","tags","funding_year","funding_month"]
_model = None

def get_model():
    global _model
    if _model is None:
        if not MODEL_PATH.exists(): raise FileNotFoundError(f"Model not found: {MODEL_PATH}")
        _model = joblib.load(MODEL_PATH)
    return _model

def _explanations(row: pd.DataFrame, model):
    importances = getattr(model, "feature_importances_", None)
    if importances is None:
        return []
    names = list(getattr(model, "feature_names_in_", FEATURES)); values=row.iloc[0].to_dict()
    return sorted([{"feature":str(n),"importance":float(v),"value":float(values.get(n,0))} for n,v in zip(names,importances)],key=lambda x:x["importance"],reverse=True)[:6]

def _improvements(x: dict[str, Any], success: float, explanations: list[dict[str, Any]]):
    actions=[]
    revenue=float(x.get("estimated_revenue_usd",0) or 0)
    funding=float(x.get("funding_amount_usd",0) or 0)
    employees=float(x.get("employee_count",0) or 0)
    valuation=float(x.get("estimated_valuation_usd",0) or 0)
    rounds=float(x.get("funding_round",0) or 0)
    if revenue <= 0:
        actions.append("Validate a measurable revenue path and run a small paid-user or pilot experiment.")
    elif revenue < 100000:
        actions.append("Strengthen early revenue validation: track conversion, retention and repeat usage before scaling.")
    if employees < 5:
        actions.append("Check whether the current team can deliver the MVP; assign clear ownership for product and engineering.")
    if funding <= 0:
        actions.append("Build a lean financing plan and validate the MVP before committing to a large funding requirement.")
    elif funding > 0 and revenue == 0:
        actions.append("Tie future funding to measurable milestones so capital is connected to product and customer validation.")
    if valuation > 0 and revenue > 0 and valuation / revenue > 30:
        actions.append("Validate the valuation assumption against revenue, growth and comparable companies rather than relying on a headline valuation.")
    if rounds <= 1:
        actions.append("Focus on proving the core product and customer demand before adding complexity or pursuing additional rounds.")
    if success < 0.5:
        actions.append("Prioritize the lowest-confidence business assumptions first and rerun the prediction after collecting stronger operating data.")
    else:
        actions.append("Keep validating customer demand and unit economics; a model probability is not a guarantee of future success.")
    # Remove duplicates while keeping the first four actionable items.
    out=[]
    for a in actions:
        if a not in out: out.append(a)
    return out[:5]

def predict_startup(x: dict[str,Any]):
    model=get_model(); row={f:float(x[f]) for f in FEATURES}; frame=pd.DataFrame([row],columns=FEATURES)
    probabilities=model.predict_proba(frame)[0]; classes=list(model.classes_); probs={int(c):float(p) for c,p in zip(classes,probabilities)}
    success=probs.get(1,0.0); failure=probs.get(0,0.0); prediction=1 if success>=0.5 else 0
    explanations=_explanations(frame,model)
    return {
        "prediction":prediction,
        "outcome":"Success" if prediction else "Failure",
        "success_probability":success,
        "failure_probability":failure,
        "confidence":max(success,failure),
        "explanations":explanations,
        "improvements":_improvements(x,success,explanations),
        "disclaimer":"These percentages are model estimates from the training data, not guarantees of startup success or failure. Suggested improvements are validation actions, not causal guarantees.",
    }

def get_feature_importance():
    model=get_model(); imps=getattr(model,"feature_importances_",None)
    if imps is None:return []
    names=list(getattr(model,"feature_names_in_",FEATURES)); return sorted([{"feature":str(n),"importance":float(v)} for n,v in zip(names,imps)],key=lambda x:x["importance"],reverse=True)

def get_metrics():
    return json.loads(METRICS_PATH.read_text(encoding="utf-8")) if METRICS_PATH.exists() else {"model":"RandomForestClassifier","model_version":"6.0.0","leakage_safe":True}
