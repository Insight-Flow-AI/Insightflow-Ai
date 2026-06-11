import pandas as pd

def analyze_class_imbalance(df: pd.DataFrame, target_column: str, problem_type: str) -> dict:
    if problem_type != "CLASSIFICATION" or target_column not in df.columns:
        return {"imbalanceClass": "NOT_APPLICABLE"}

    target_series = df[target_column].dropna()
    if target_series.empty:
        return {"imbalanceClass": "UNKNOWN"}

    value_counts = target_series.value_counts(normalize=True) * 100
    
    minority_pct = float(value_counts.min())
    majority_pct = float(value_counts.max())
    
    imbalance_ratio = majority_pct / minority_pct if minority_pct > 0 else float('inf')

    if minority_pct >= 40:
        imbalance_class = "BALANCED"
    elif minority_pct >= 20:
        imbalance_class = "MILD_IMBALANCE"
    elif minority_pct >= 5:
        imbalance_class = "SEVERE_IMBALANCE"
    else:
        imbalance_class = "EXTREME_IMBALANCE"

    return {
        "minorityClassPercentage": round(minority_pct, 2),
        "majorityClassPercentage": round(majority_pct, 2),
        "imbalanceRatio": round(imbalance_ratio, 2),
        "imbalanceClass": imbalance_class
    }
