def calculate_health_score(distributions: dict, correlations: dict, target_analysis: dict) -> int:
    """
    Computes a 0-100 dataset health score based on skewness, multicollinearity, and target imbalance.
    """
    score = 100
    
    # 1. Penalty for extreme skewness
    high_skew_count = 0
    for col, dist in distributions.items():
        if abs(dist.get("skewness", 0)) > 3.0:
            high_skew_count += 1
            
    # Deduct 2 points for every highly skewed feature, max penalty 20
    score -= min(high_skew_count * 2, 20)
    
    # 2. Penalty for multicollinearity (strong correlations among features)
    strong_pos = len(correlations.get("strong_positive", []))
    strong_neg = len(correlations.get("strong_negative", []))
    total_strong_corrs = strong_pos + strong_neg
    
    # Deduct 1 point for every highly correlated pair, max penalty 30
    score -= min(total_strong_corrs, 30)
    
    # 3. Penalty for Target Imbalance
    if target_analysis.get("is_imbalanced", False):
        score -= 20
        
    # Ensure score stays within 0-100 bounds
    return max(0, score)
