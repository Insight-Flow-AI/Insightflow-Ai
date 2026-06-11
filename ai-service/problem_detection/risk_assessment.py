def assess_risks(complexity: dict, imbalance_report: dict, leaked_features: list) -> dict:
    risks = []
    overall_severity = "LOW"

    # Overfitting Risk
    if complexity.get("featureToSampleRatio", 0) > 0.5:
        risks.append({"type": "OVERFITTING", "severity": "HIGH", "description": "Too many features compared to rows."})
        overall_severity = "HIGH"

    # Leakage Risk
    if leaked_features:
        risks.append({"type": "TARGET_LEAKAGE", "severity": "CRITICAL", "description": f"Features {leaked_features} show perfect correlation."})
        overall_severity = "CRITICAL"

    # Imbalance Risk
    if imbalance_report.get("imbalanceClass") == "EXTREME_IMBALANCE":
        risks.append({"type": "CLASS_IMBALANCE", "severity": "HIGH", "description": "Extreme minority class detected (<5%)."})
        if overall_severity != "CRITICAL":
            overall_severity = "HIGH"

    # Sparse Matrix Risk
    if complexity.get("sparsityClass") == "Sparse" and complexity.get("columns", 0) > 1000:
        risks.append({"type": "SPARSE_MATRIX_EXPLOSION", "severity": "MEDIUM", "description": "High number of sparse features."})
        if overall_severity not in ["CRITICAL", "HIGH"]:
            overall_severity = "MEDIUM"

    return {
        "overallSeverity": overall_severity,
        "risks": risks
    }
