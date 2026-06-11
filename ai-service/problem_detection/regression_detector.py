def detect_regression(target_analysis: dict) -> bool:
    if not target_analysis.get("exists", False):
        return False

    unique_vals = target_analysis.get("uniqueValues", 0)
    datatype = target_analysis.get("datatype", "UNKNOWN")
    variance = target_analysis.get("variance")

    # If it's highly continuous numeric data
    if datatype == "NUMERIC" and unique_vals > 20:
        # Prevent 0 variance targets
        if variance is not None and variance > 0:
            return True

    return False
