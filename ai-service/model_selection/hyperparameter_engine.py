import logging

logger = logging.getLogger(__name__)

def generate_hyperparameter_grids(candidates: list) -> dict:
    """
    Generates RandomizedSearchCV grids for models.
    """
    grids = {}
    
    for model in candidates:
        name = model["name"]
        
        if "RandomForest" in name:
            grids[name] = {
                "n_estimators": [100, 200, 300],
                "max_depth": [5, 10, 20, None],
                "min_samples_split": [2, 5, 10]
            }
        elif "XGBoost" in name:
            grids[name] = {
                "learning_rate": [0.01, 0.05, 0.1, 0.2],
                "max_depth": [3, 5, 7],
                "n_estimators": [100, 200]
            }
        elif "LogisticRegression" in name:
            grids[name] = {
                "C": [0.01, 0.1, 1.0, 10.0],
                "penalty": ["l2"]
            }
        elif "Ridge" in name:
            grids[name] = {
                "alpha": [0.1, 1.0, 10.0]
            }
        elif "KMeans" in name:
            grids[name] = {
                "n_clusters": [2, 3, 4, 5, 6, 7]
            }
        elif "DBSCAN" in name:
            grids[name] = {
                "eps": [0.1, 0.5, 1.0],
                "min_samples": [5, 10]
            }
        else:
            grids[name] = {}
            
    return grids
