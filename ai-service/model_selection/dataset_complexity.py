import logging

logger = logging.getLogger(__name__)

def analyze_complexity(dataset_stats: dict) -> dict:
    """
    Analyzes the dataset physical footprint.
    """
    rows = dataset_stats.get('total_rows', 0)
    cols = dataset_stats.get('total_columns', 0)
    
    # Categorize dataset size
    size_category = "tiny"
    if rows >= 1000000:
        size_category = "very_large"
    elif rows >= 100000:
        size_category = "large"
    elif rows >= 10000:
        size_category = "medium"
    elif rows >= 1000:
        size_category = "small"
        
    is_high_dimensional = cols > (rows / 10) if rows > 0 else False
    estimated_memory_mb = (rows * cols * 8) / (1024 * 1024)
    
    report = {
        "sizeCategory": size_category,
        "isHighDimensional": is_high_dimensional,
        "estimatedMemoryMB": estimated_memory_mb
    }
    
    logger.info(f"Complexity Analyzer: {report}")
    return report
