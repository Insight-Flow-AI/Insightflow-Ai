def evaluate_training_feasibility(target_analysis: dict, complexity: dict, health_score: float, problem_type: str) -> dict:
    reasons = []
    is_trainable = True
    confidence = 100

    # 1. Minimum Rows (Temporarily lowered to 10 for testing)
    if complexity.get("rows", 0) < 10:
        is_trainable = False
        reasons.append("Dataset has fewer than 10 rows.")
        confidence -= 50

    # 2. Minimum Features
    if complexity.get("columns", 0) < 2:
        is_trainable = False
        reasons.append("Dataset has fewer than 2 columns (needs at least 1 feature + 1 target).")
        confidence -= 50

    # 3. Target Validity
    if not target_analysis.get("exists", False):
        if problem_type != "CLUSTERING":
            is_trainable = False
            reasons.append("No target column found for supervised learning.")
            confidence -= 50
    else:
        unique_vals = target_analysis.get("uniqueValues", 0)
        if unique_vals < 2 and problem_type != "CLUSTERING":
            is_trainable = False
            reasons.append("Target column has less than 2 unique values (constant target).")
            confidence -= 100

    # 4. Health Score Impact
    if health_score < 40:
        confidence -= 30
        reasons.append("Overall dataset health score is critically low.")

    return {
        "isTrainable": is_trainable,
        "confidenceScore": max(0, confidence),
        "failureReasons": reasons
    }
