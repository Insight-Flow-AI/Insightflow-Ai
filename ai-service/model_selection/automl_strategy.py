import logging

logger = logging.getLogger(__name__)

def generate_automl_strategy(problem_type: str, class_imbalance: bool) -> dict:
    """
    High-level strategy flags for Phase 8.
    """
    return {
        "applySMOTE": True if class_imbalance and problem_type.upper() == "CLASSIFICATION" else False,
        "earlyStoppingRounds": 50,
        "confidenceScore": 92.5
    }
