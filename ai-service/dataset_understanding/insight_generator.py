import logging

logger = logging.getLogger(__name__)

def generate_insights(correlations: dict, distributions: dict, target_analysis: dict) -> list:
    """
    Translates mathematical findings into human-readable business rules and insights.
    """
    insights = []
    
    # 1. Target Insights
    if target_analysis.get("is_imbalanced", False):
        if target_analysis.get("type") == "CLASSIFICATION":
            min_ratio = target_analysis.get("minority_class_ratio", 0) * 100
            insights.append(f"The target variable is highly imbalanced (minority class is only {min_ratio:.1f}%). Consider using SMOTE or class weighting during model training.")
        else:
            insights.append("The target variable is highly skewed, which may affect regression model performance. Consider log-transforming the target.")
            
    # 2. Correlation Insights
    strong_pos = correlations.get("strong_positive", [])
    if strong_pos:
        # Take the top 3 strongest
        sorted_pos = sorted(strong_pos, key=lambda x: x['score'], reverse=True)[:3]
        for c in sorted_pos:
            insights.append(f"'{c['feature_1']}' strongly increases as '{c['feature_2']}' increases (Score: {c['score']}).")
            
    strong_neg = correlations.get("strong_negative", [])
    if strong_neg:
        sorted_neg = sorted(strong_neg, key=lambda x: x['score'])[:3]
        for c in sorted_neg:
            insights.append(f"'{c['feature_1']}' strongly decreases as '{c['feature_2']}' increases (Score: {c['score']}).")
            
    # 3. Distribution Insights
    highly_skewed = []
    for col, dist in distributions.items():
        if abs(dist.get("skewness", 0)) > 2.0:
            highly_skewed.append(col)
            
    if highly_skewed:
        if len(highly_skewed) > 3:
            insights.append(f"Found {len(highly_skewed)} highly skewed features (including {', '.join(highly_skewed[:3])}). Linear models may struggle with these unless transformed.")
        else:
            insights.append(f"The following features are highly skewed: {', '.join(highly_skewed)}.")
            
    if not insights:
        insights.append("The dataset appears healthy, balanced, and free of extreme correlations or skewness.")
        
    return insights
