import logging

logger = logging.getLogger(__name__)

def generate_validation_strategy(problem_type: str, class_imbalance: bool) -> dict:
    """
    Determines Cross-Validation strategy.
    """
    problem_type = problem_type.upper()
    strategy = "KFold"
    metric = "accuracy"
    
    if problem_type == "CLASSIFICATION":
        strategy = "StratifiedKFold"
        metric = "f1_score" if class_imbalance else "accuracy"
    elif problem_type == "REGRESSION":
        strategy = "KFold"
        metric = "rmse"
    elif problem_type == "CLUSTERING":
        strategy = "None"
        metric = "silhouette_score"
        
    return {
        "strategy": strategy,
        "k_folds": 5 if strategy != "None" else 0,
        "primaryMetric": metric
    }
