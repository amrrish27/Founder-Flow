from typing import Any
import math
import re

STOPWORDS = {
    "the","and","for","with","that","this","from","into","your","you","are","will",
    "can","our","their","they","them","then","than","have","has","using","use","based",
    "app","platform","system","product","service","users","user","make","made","get","gets",
}

def _clamp(v, lo=0, hi=100):
    return max(lo, min(hi, float(v)))

def _words(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-zA-Z0-9]+", text.lower()) if len(w) > 2 and w not in STOPWORDS]

def _component(label: str, score: float, weight: int, note: str) -> dict[str, Any]:
    return {"label": label, "score": round(_clamp(score)), "weight": weight, "note": note}

def analyze_idea(data: dict[str, Any]) -> dict[str, Any]:
    """Deterministic, explainable validation score. Industry is contextual only and never changes the score."""
    idea = str(data.get("idea", "")).strip()
    customer = str(data.get("customer", "")).strip()
    budget = float(data.get("budget", 0) or 0)
    problem = str(data.get("problem", "")).strip()
    solution = str(data.get("solution", "")).strip()

    iw, cw, pw, sw = map(_words, [idea, customer, problem, solution])
    idea_score = min(100, 25 + len(iw) * 5) if iw else 0
    customer_score = 100 if len(cw) >= 5 else 75 if len(cw) >= 3 else 45 if len(cw) >= 1 else 0
    problem_score = min(100, 25 + len(pw) * 5) if pw else 0
    solution_score = min(100, 25 + len(sw) * 5) if sw else 0

    if budget <= 0:
        budget_score = 0
    elif budget < 1000:
        budget_score = 45
    elif budget <= 100000:
        budget_score = 100
    else:
        budget_score = 75

    meaningful_overlap = len((set(pw) & set(sw)) - {"problem", "solution"})
    alignment_score = min(100, meaningful_overlap * 20 + (20 if pw and sw else 0))

    components = [
        _component("Idea clarity", idea_score, 25, "Specific product, user and outcome details increase clarity."),
        _component("Customer specificity", customer_score, 15, "A narrow first customer segment is easier to validate."),
        _component("Problem definition", problem_score, 20, "Describe the current pain, frequency and consequence."),
        _component("Solution definition", solution_score, 20, "Explain what the product actually does to solve the problem."),
        _component("MVP budget", budget_score, 10, "A concrete validation budget makes the plan testable."),
        _component("Problem–solution alignment", alignment_score, 10, "Shared meaningful terms provide a basic consistency check; they do not prove product-market fit."),
    ]
    score = round(sum(c["score"] * c["weight"] for c in components) / 100)

    strengths, weaknesses, next_steps = [], [], []
    if idea_score >= 70: strengths.append("The idea contains enough detail to form a testable product hypothesis.")
    else: weaknesses.append("Make the idea more specific: who uses it, what it does and what measurable outcome it creates.")
    if customer_score >= 75: strengths.append("The target customer is specific enough to define an initial segment.")
    else:
        weaknesses.append("Narrow the customer to a specific user group, role or company type.")
        next_steps.append("Interview 10–15 people from the exact target segment.")
    if problem_score >= 70: strengths.append("The problem is described with enough detail for validation.")
    else:
        weaknesses.append("Describe the current pain, how often it occurs and what it costs the user.")
        next_steps.append("Write down the current workflow users follow without your product.")
    if solution_score >= 70: strengths.append("The solution describes concrete product behavior.")
    else:
        weaknesses.append("Describe the smallest feature set that directly solves the stated problem.")
        next_steps.append("Define a one-feature MVP that tests the core assumption.")
    if budget_score >= 70: strengths.append("A usable MVP budget has been provided.")
    else:
        weaknesses.append("Add a realistic MVP validation budget.")
        next_steps.append("Estimate the first 3 months of build and operating costs.")
    if alignment_score < 40 and problem and solution:
        weaknesses.append("The problem and solution descriptions do not clearly connect yet.")
        next_steps.append("Rewrite the solution as: 'We solve [problem] for [customer] by [mechanism].'")

    if not next_steps:
        next_steps = [
            "Interview at least 10 target customers",
            "Define one measurable MVP success metric",
            "Test willingness to pay before scaling development",
            "Use the Financial Planner to map the first 3 months of cash usage",
        ]
    elif "Interview at least 10 target customers" not in next_steps:
        next_steps.insert(0, "Interview at least 10 target customers")

    label = "Strong validation base" if score >= 75 else "Promising — validate key assumptions" if score >= 55 else "Early-stage hypothesis"
    return {
        "feasibility_score": score,
        "score_label": label,
        "score_components": components,
        "strengths": strengths or ["The concept is ready for structured validation."],
        "weaknesses": weaknesses or ["No major completeness gaps were detected in the submitted fields."],
        "risks": [],
        "next_steps": next_steps[:5],
        "disclaimer": "This is an explainable completeness/validation score, not an ML prediction of commercial success. The same inputs always produce the same score.",
    }

def financial_plan(data: dict[str, Any]) -> dict[str, Any]:
    cash=float(data.get("initial_investment",0))
    revenue=float(data.get("monthly_revenue",0))
    expenses=float(data.get("monthly_expenses",0))
    growth=float(data.get("monthly_revenue_growth",5))/100
    expense_growth=float(data.get("monthly_expense_growth",3))/100
    price=float(data.get("price_per_unit",0))
    variable=float(data.get("variable_cost_per_unit",0))
    fixed = float(data.get("fixed_monthly_costs", 0))
    if "fixed_monthly_costs" not in data or data["fixed_monthly_costs"] is None:
        fixed = expenses
    contribution=price-variable
    break_even_units=math.ceil(fixed/contribution) if contribution>0 else None
    months=[]; balance=cash
    for i in range(1,13):
        rev=revenue*((1+growth)**(i-1)); exp=expenses*((1+expense_growth)**(i-1)); net=rev-exp; balance += net
        months.append({"month":i,"revenue":round(rev,2),"expenses":round(exp,2),"net":round(net,2),"cash_balance":round(balance,2)})
    burn=max(expenses-revenue,0)
    runway=cash/burn if burn>0 else None
    return {"burn_rate":round(burn,2),"runway_months":round(runway,1) if runway is not None else None,"break_even_units":break_even_units,"projection":months,"ending_cash":months[-1]["cash_balance"] if months else cash}


def _words(text: str) -> set[str]:
    import re
    return {w for w in re.findall(r"[a-zA-Z0-9]+", (text or "").lower()) if len(w) > 2}

def compare_competitor(data: dict[str, Any]) -> dict[str, Any]:
    """Explainable competitor benchmark. It is a structured comparison, not a market-claim engine."""
    sp = str(data.get("startup_product", "")).strip()
    sc = str(data.get("startup_customer", "")).strip()
    sa = str(data.get("startup_advantage", "")).strip()
    cp = str(data.get("competitor_product", "")).strip()
    cc = str(data.get("competitor_customer", "")).strip()
    cs = str(data.get("competitor_strengths", "")).strip()
    cw = str(data.get("competitor_weaknesses", "")).strip()
    spr = float(data.get("startup_price", 0) or 0)
    cpr = float(data.get("competitor_price", 0) or 0)

    overlap_product = len(_words(sp) & _words(cp))
    overlap_customer = len(_words(sc) & _words(cc))
    dimensions = []

    product_score = 70 if sp and len(sp.split()) >= 8 else 45 if sp else 20
    if overlap_product >= 4: product_score -= 15
    elif overlap_product == 0 and sp and cp: product_score += 10
    dimensions.append(("Product differentiation", max(0,min(100,product_score)), "Describe a clear capability or workflow the competitor does not emphasize."))

    customer_score = 80 if sc and len(sc.split()) >= 3 else 45 if sc else 20
    if overlap_customer >= 3: customer_score -= 10
    dimensions.append(("Customer focus", max(0,min(100,customer_score)), "Choose a specific segment where you can learn and distribute faster."))

    if spr > 0 and cpr > 0:
        ratio=spr/cpr
        price_score=75 if 0.7 <= ratio <= 1.15 else 65 if ratio < 0.7 else 50
        price_note="Compare price with the value delivered, not price alone."
    else:
        price_score=40
        price_note="Add comparable pricing or packaging before making a pricing decision."
    dimensions.append(("Pricing position", price_score, price_note))

    advantage_score=85 if len(sa.split())>=6 else 55 if sa else 25
    dimensions.append(("Differentiation strength", advantage_score, "Turn one meaningful advantage into a measurable customer outcome."))

    response_score=80 if cw else 45
    dimensions.append(("Competitive gap evidence", response_score, "Record a concrete competitor weakness only when you can verify it."))

    overall=round(sum(x[1] for x in dimensions)/len(dimensions))
    actions=[]
    if product_score < 65: actions.append("Choose one core workflow where your product is meaningfully different, then make that the MVP headline.")
    if customer_score < 65: actions.append("Narrow the first customer segment and build messaging around one urgent use case.")
    if price_score < 65: actions.append("Test 2–3 pricing packages with real users and compare willingness to pay against the competitor's offer.")
    if advantage_score < 65: actions.append("Define one measurable advantage such as faster completion, lower cost, better automation or stronger support.")
    if not cw: actions.append("Research and verify 2–3 competitor limitations using product documentation, reviews or customer interviews.")
    if not actions: actions.append("Run customer interviews focused on why users would switch from the competitor, then turn the strongest reason into an MVP differentiator.")
    actions.append("Track competitor changes monthly and update your comparison instead of relying on a one-time snapshot.")

    return {
        "competitor_name": data.get("competitor_name", "Competitor"),
        "benchmark_score": overall,
        "dimensions":[{"label":a,"score":b,"note":c} for a,b,c in dimensions],
        "comparison": {
            "customer_overlap": overlap_customer > 0,
            "product_overlap": overlap_product > 0,
            "startup_price": spr, "competitor_price": cpr
        },
        "how_to_compete": actions[:6],
        "disclaimer":"This is a structured comparison of the information you supplied. It does not establish market share, product superiority or a guaranteed competitive outcome. Verify competitor claims with current evidence."
    }
