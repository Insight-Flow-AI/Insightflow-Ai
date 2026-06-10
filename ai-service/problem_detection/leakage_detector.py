def detect_leakage(correlation_report: dict, target_column: str) -> list:
    """
    Analyzes the correlation matrix (if provided) to find perfect correlations.
    Returns a list of leaked features.
    """
    leaked_features = []
    
    if not correlation_report or target_column not in correlation_report:
        return leaked_features

    # Assuming correlation_report structure is a nested dict: {col1: {col2: score}}
    target_corrs = correlation_report.get(target_column, {})
    
    for feature, score in target_corrs.items():
        if feature == target_column:
            continue
            
        # If absolute correlation > 0.99, flag as leakage
        if abs(score) >= 0.99:
            leaked_features.append(feature)
            
    return leaked_features
