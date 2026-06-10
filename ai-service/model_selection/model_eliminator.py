import logging

logger = logging.getLogger(__name__)

def eliminate_models(candidate_families: list, complexity: dict) -> list:
    """
    Violently removes unsuitable models.
    """
    survivors = []
    size_cat = complexity.get("sizeCategory", "medium")
    
    for model in candidate_families:
        name = model["name"]
        
        # Rule 1: Drop SVM if large
        if name == "SupportVectorMachine" and size_cat in ["large", "very_large"]:
            logger.info(f"Eliminating {name} due to row count limitations.")
            continue
            
        # Rule 2: Drop heavy ensembles if tiny
        if name in ["XGBoostClassifier", "LightGBMClassifier"] and size_cat == "tiny":
            logger.info(f"Eliminating {name} due to severe overfitting risk on tiny data.")
            continue
            
        survivors.append(model)
        
    logger.info(f"Eliminated {len(candidate_families) - len(survivors)} models.")
    return survivors
