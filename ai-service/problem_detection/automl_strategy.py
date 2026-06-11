def generate_automl_strategy(problem_type: str, imbalance_report: dict, leaked_features: list) -> dict:
    strategy = {
        "validationStrategy": "KFold",
        "preprocessingStrategy": [],
        "recommendedMetric": "accuracy"
    }

    if problem_type == "CLASSIFICATION":
        strategy["validationStrategy"] = "StratifiedKFold"
        
        imbalance_class = imbalance_report.get("imbalanceClass", "BALANCED")
        
        if imbalance_class in ["SEVERE_IMBALANCE", "EXTREME_IMBALANCE"]:
            strategy["preprocessingStrategy"].append("SMOTE")
            strategy["recommendedMetric"] = "f1_score"
        elif imbalance_class == "MILD_IMBALANCE":
            strategy["preprocessingStrategy"].append("CLASS_WEIGHTING")
            strategy["recommendedMetric"] = "f1_score"
            
    elif problem_type == "REGRESSION":
        strategy["recommendedMetric"] = "rmse"

    if leaked_features:
        strategy["preprocessingStrategy"].append("DROP_LEAKAGE_FEATURES")

    return strategy
