import logging

logger = logging.getLogger(__name__)

def estimate_resources(candidates_count: int, complexity: dict) -> dict:
    """
    Estimates CPU and Time.
    """
    mem = complexity.get("estimatedMemoryMB", 100)
    
    return {
        "estimatedTimeSeconds": candidates_count * 60, # Naive 1 min per candidate MVP
        "parallelJobs": -1, # Use all cores
        "memoryRequirementMB": mem * 3
    }
