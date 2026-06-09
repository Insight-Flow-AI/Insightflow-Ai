def generate_feature_report(
    original_columns: int,
    encoded_columns: int,
    scaled_columns: int,
    removed_columns: int,
    final_columns: int,
    encoder_metadata: dict,
    scaler_metadata: dict
) -> dict:
    """
    Generates a structured JSON report summarizing the Feature Engineering process.
    """
    return {
        "original_columns": original_columns,
        "encoded_columns": encoded_columns,
        "scaled_columns": scaled_columns,
        "removed_columns": removed_columns,
        "final_columns": final_columns,
        "details": {
            "encoders": encoder_metadata,
            "scaler": scaler_metadata
        }
    }
