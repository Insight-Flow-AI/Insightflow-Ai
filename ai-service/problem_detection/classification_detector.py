def detect_classification(target_analysis: dict) -> tuple:
    if not target_analysis.get("exists", False):
        return False, None

    unique_vals = target_analysis.get("uniqueValues", 0)
    datatype = target_analysis.get("datatype", "UNKNOWN")

    if unique_vals == 2:
        return True, "BINARY"
    elif 3 <= unique_vals <= 20 and datatype in ["CATEGORICAL", "NUMERIC", "INTEGER"]:
        return True, "MULTI_CLASS"

    # Edge cases for high cardinality classification can be added here
    return False, None
