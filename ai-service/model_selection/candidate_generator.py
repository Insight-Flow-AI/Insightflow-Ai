import logging

logger = logging.getLogger(__name__)

def generate_candidates(survivors: list) -> list:
    """
    Selects top 3 models.
    """
    # For MVP, just return the top 3 surviving models.
    candidates = survivors[:3]
    
    final_list = []
    for i, model in enumerate(candidates):
        model["priorityRank"] = i + 1
        model["reason"] = "Passed all architectural safety constraints."
        final_list.append(model)
        
    logger.info(f"Candidate Generator selected {len(final_list)} models.")
    return final_list
