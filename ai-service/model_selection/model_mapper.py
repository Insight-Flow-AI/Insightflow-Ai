import logging

logger = logging.getLogger(__name__)

def map_model_families(problem_type: str, sub_type: str) -> list:
    """
    Maps problem type to algorithmic families.
    """
    problem_type = problem_type.upper()
    sub_type = sub_type.upper() if sub_type else ""
    
    candidate_families = []
    
    if problem_type == "CLASSIFICATION":
        if sub_type == "BINARY":
            candidate_families = [
                {"name": "LogisticRegression", "type": "baseline"},
                {"name": "RandomForestClassifier", "type": "ensemble"},
                {"name": "XGBoostClassifier", "type": "boosting"},
                {"name": "SupportVectorMachine", "type": "distance"}
            ]
        else:
            candidate_families = [
                {"name": "RandomForestClassifier", "type": "ensemble"},
                {"name": "XGBoostClassifier", "type": "boosting"},
                {"name": "LightGBMClassifier", "type": "boosting"}
            ]
            
    elif problem_type == "REGRESSION":
        candidate_families = [
            {"name": "RidgeRegression", "type": "baseline"},
            {"name": "RandomForestRegressor", "type": "ensemble"},
            {"name": "XGBoostRegressor", "type": "boosting"}
        ]
        
    elif problem_type == "CLUSTERING":
        candidate_families = [
            {"name": "KMeans", "type": "distance"},
            {"name": "DBSCAN", "type": "density"}
        ]
    else:
        logger.warning(f"Unknown problem type {problem_type}, falling back to defaults.")
        candidate_families = [
            {"name": "RandomForest", "type": "ensemble"}
        ]

    logger.info(f"Model Mapper generated {len(candidate_families)} families for {problem_type}")
    return candidate_families
