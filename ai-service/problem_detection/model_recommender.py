def recommend_models(problem_type: str, complexity: dict) -> list:
    candidates = []

    if problem_type == "CLASSIFICATION":
        candidates.append("LogisticRegression")
        candidates.append("RandomForestClassifier")
        
        # If the dataset is large enough, append boosting models
        if complexity.get("rows", 0) > 500:
            candidates.append("XGBoostClassifier")
            candidates.append("LightGBMClassifier")

    elif problem_type == "REGRESSION":
        candidates.append("LinearRegression")
        candidates.append("RidgeRegression")
        candidates.append("RandomForestRegressor")
        
        if complexity.get("rows", 0) > 500:
            candidates.append("XGBoostRegressor")
            
    elif problem_type == "CLUSTERING":
        candidates.append("KMeans")
        candidates.append("DBSCAN")
        
    return candidates
