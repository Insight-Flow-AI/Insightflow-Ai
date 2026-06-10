import pandas as pd

def analyze_complexity(df: pd.DataFrame) -> dict:
    rows, cols = df.shape
    total_elements = rows * cols
    
    if total_elements > 0:
        zeros_count = (df == 0).sum().sum() + df.isnull().sum().sum()
        sparsity = zeros_count / total_elements
    else:
        sparsity = 0.0

    feature_to_sample_ratio = cols / rows if rows > 0 else float('inf')

    # Size classification
    if rows < 1000:
        size_class = "Small"
    elif rows <= 100000:
        size_class = "Medium"
    else:
        size_class = "Large"

    # Sparsity classification
    sparsity_class = "Sparse" if sparsity > 0.8 else "Dense"

    # High dimensional classification
    is_high_dimensional = cols > rows or cols > 1000

    return {
        "rows": int(rows),
        "columns": int(cols),
        "sparsity": float(sparsity),
        "featureToSampleRatio": float(feature_to_sample_ratio),
        "sizeClass": size_class,
        "sparsityClass": sparsity_class,
        "isHighDimensional": is_high_dimensional
    }
