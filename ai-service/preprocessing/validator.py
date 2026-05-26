"""
=============================================================================
InsightFlow AI  —  Phase 2: DataValidationService
=============================================================================
Runs 10 validation checks in strict order and returns a single structured
ValidationReport JSON.  Called by main.py via Kafka "dataset-upload" topic.
=============================================================================
"""

import re
import io
import logging
from dataclasses import dataclass, field, asdict
from typing import Any, Optional

import pandas as pd
import numpy as np
from scipy import stats as scipy_stats
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from database import db

logger = logging.getLogger(__name__)


# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class Finding:
    """Single validation finding produced by any of the 10 checks."""
    level:   str            # "ERROR" | "WARNING" | "INFO"
    code:    str            # snake_case unique identifier
    message: str            # human-readable plain English description
    column:  Optional[str]  # affected column name, or None for dataset-level
    action:  str            # instruction string for Phase 3 to consume


@dataclass
class ValidationReport:
    """Top-level report returned by DataValidationService.validate()."""
    dataset_id:         str
    total_rows:         int  = 0
    total_columns:      int  = 0
    status:             str  = "PASSED"     # PASSED | WARNING | FAILED
    findings:           list = field(default_factory=list)
    schema_map:         dict = field(default_factory=dict)
    problem_type_hint:  Optional[str] = None   # REGRESSION | CLASSIFICATION
    stats_summary:      dict = field(default_factory=dict)
    class_distribution: Optional[dict] = None


# =============================================================================
# Internal helpers
# =============================================================================

def _col_contains(col_name: str, keywords: list) -> bool:
    low = col_name.lower()
    return any(kw in low for kw in keywords)


def _compute_status(findings: list) -> str:
    levels = {f.level for f in findings}
    if "ERROR"   in levels: return "FAILED"
    if "WARNING" in levels: return "WARNING"
    return "PASSED"


def _report_to_dict(report: ValidationReport) -> dict:
    d = asdict(report)
    d["findings"] = [asdict(f) for f in report.findings]
    return d


# =============================================================================
# DataValidationService  —  10 checks in strict order
# =============================================================================

class DataValidationService:
    """
    Usage:
        service = DataValidationService()
        report_dict = service.validate(df, target_column="Churn")
    """

    # keyword lists used across checks
    NUMERIC_KEYWORDS  = ["age", "year", "salary", "price", "revenue",
                         "quantity", "count", "score", "rate", "amount"]
    DATETIME_KEYWORDS = ["date", "time", "dob", "created", "updated"]
    STRING_KEYWORDS   = ["email", "phone", "name", "description", "address"]

    # business-rule numeric ranges  (keyword_list, lo, hi)
    _NUMERIC_RULES = [
        (["age", "years_old"],          0,          120),
        (["salary", "income"],          0,   10_000_000),
        (["price", "cost", "fee"],      0,    1_000_000),
        (["percentage", "rate"],        0,          100),
        (["quantity", "count"],         0,  float("inf")),   # no negatives
    ]
    _EMAIL_RE = re.compile(r'^[\w.+\-]+@[\w\-]+\.[a-zA-Z]{2,}$')

    # -------------------------------------------------------------------------
    def __init__(self):
        self._reset()

    def _reset(self):
        self.findings:           list           = []
        self.df:                 Optional[pd.DataFrame] = None
        self.target_column:      Optional[str]  = None
        self.schema_map:         dict           = {}
        self.stats_summary:      dict           = {}
        self.problem_type_hint:  Optional[str]  = None
        self.class_distribution: Optional[dict] = None

    # =========================================================================
    # Public entry point
    # =========================================================================

    def validate(self, df: pd.DataFrame,
                 target_column: Optional[str] = None) -> dict:
        """Execute all 10 checks and return ValidationReport as dict."""
        self._reset()
        self.df            = df
        self.target_column = target_column

        report = ValidationReport(
            dataset_id    = "",
            total_rows    = int(df.shape[0]),
            total_columns = int(df.shape[1]),
        )

        # ── CONDITION 1  (abort if empty) ─────────────────────────────────────
        if self._check_1_empty_dataset():
            report.status   = "FAILED"
            report.findings = self.findings
            return _report_to_dict(report)

        # ── CONDITIONS 2 – 10 ─────────────────────────────────────────────────
        self._check_2_duplicate_columns()
        self._check_3_missing_headers()
        self._check_4_data_types()
        self._check_5_null_values()
        self._check_6_unique_variance()
        self._check_7_schema_map()          # populates self.schema_map
        self._check_8_statistics()
        self._check_9_class_imbalance()
        self._check_10_business_rules()

        report.findings           = self.findings
        report.status             = _compute_status(self.findings)
        report.schema_map         = self.schema_map
        report.problem_type_hint  = self.problem_type_hint
        report.stats_summary      = self.stats_summary
        report.class_distribution = self.class_distribution
        return _report_to_dict(report)

    # =========================================================================
    # CONDITION 1 — Empty Dataset Check
    # =========================================================================

    def _check_1_empty_dataset(self) -> bool:
        """Return True if ANY sub-check triggers → caller must abort."""
        abort = False
        df = self.df

        if df.empty:
            self.findings.append(Finding(
                level="ERROR", code="EMPTY_DATASET",
                message="The dataset is completely empty (df.empty is True).",
                column=None, action="ABORT_PIPELINE"
            ))
            abort = True

        if df.shape[0] == 0:
            self.findings.append(Finding(
                level="ERROR", code="ZERO_ROWS",
                message="Dataset has zero rows. Nothing to process.",
                column=None, action="ABORT_PIPELINE"
            ))
            abort = True

        if df.shape[1] == 0:
            self.findings.append(Finding(
                level="ERROR", code="ZERO_COLUMNS",
                message="Dataset has zero columns. Nothing to process.",
                column=None, action="ABORT_PIPELINE"
            ))
            abort = True

        return abort

    # =========================================================================
    # CONDITION 2 — Duplicate Column Names
    # =========================================================================

    def _check_2_duplicate_columns(self):
        cols = list(self.df.columns)
        seen, duplicates = set(), []
        for c in cols:
            if c in seen and c not in duplicates:
                duplicates.append(c)
            seen.add(c)

        if duplicates:
            rename_hint = ", ".join(
                f"{d}_1, {d}_2" for d in duplicates
            )
            self.findings.append(Finding(
                level="WARNING", code="DUPLICATE_COLUMNS",
                message=(
                    f"Duplicate column names found: {duplicates}. "
                    f"Phase 3 will rename to {rename_hint}."
                ),
                column=None, action="RENAME_DUPLICATE_COLUMNS"
            ))

    # =========================================================================
    # CONDITION 3 — Missing / Unnamed Headers
    # =========================================================================

    def _check_3_missing_headers(self):
        unnamed_cols, blank_cols = [], []
        for c in self.df.columns:
            c_str = str(c)
            if c_str.startswith("Unnamed"):
                unnamed_cols.append(c_str)
            elif c_str.strip() == "":
                blank_cols.append(c_str)

        for c in unnamed_cols:
            self.findings.append(Finding(
                level="WARNING", code="UNNAMED_HEADERS",
                message=(
                    f"Column '{c}' detected. "
                    "Likely an exported index column."
                ),
                column=c, action="DROP_UNNAMED_COLUMNS"
            ))

        if blank_cols:
            n = len(blank_cols)
            self.findings.append(Finding(
                level="ERROR", code="BLANK_HEADERS",
                message=(
                    f"{n} blank column header(s) found. "
                    "Cannot process without names."
                ),
                column=None, action="ABORT_PIPELINE"
            ))

    # =========================================================================
    # CONDITION 4 — Data Type Validation
    # =========================================================================

    def _check_4_data_types(self):
        df = self.df
        for col in df.columns:
            col_str = str(col)

            # ── Numeric expected ─────────────────────────────────────────────
            if _col_contains(col_str, self.NUMERIC_KEYWORDS):
                orig_nulls  = int(df[col].isnull().sum())
                coerced     = pd.to_numeric(df[col], errors="coerce")
                new_nulls   = int(coerced.isnull().sum())
                corrupted   = new_nulls - orig_nulls
                if corrupted > 0:
                    examples = (
                        df[col][coerced.isnull() & df[col].notnull()]
                        .astype(str).unique()[:3].tolist()
                    )
                    self.findings.append(Finding(
                        level="WARNING", code="DTYPE_MISMATCH",
                        message=(
                            f"Column '{col_str}' expected NUMERIC but found "
                            f"{corrupted} non-numeric value(s) "
                            f"(e.g. {examples})."
                        ),
                        column=col_str,
                        action="COERCE_TO_NUMERIC_AND_FLAG"
                    ))

            # ── Datetime expected ────────────────────────────────────────────
            elif _col_contains(col_str, self.DATETIME_KEYWORDS):
                orig_nulls = int(df[col].isnull().sum())
                coerced    = pd.to_datetime(df[col], errors="coerce")
                new_nulls  = int(coerced.isnull().sum())
                failed     = new_nulls - orig_nulls
                if failed > 0:
                    self.findings.append(Finding(
                        level="WARNING", code="DATETIME_PARSE_FAILED",
                        message=(
                            f"Column '{col_str}' expected DATETIME but "
                            f"{failed} value(s) could not be parsed."
                        ),
                        column=col_str,
                        action="PARSE_DATETIME_WITH_MULTIPLE_FORMATS"
                    ))

    # =========================================================================
    # CONDITION 5 — Null Value Analysis
    # =========================================================================

    def _check_5_null_values(self):
        df         = self.df
        total_rows = len(df)
        if total_rows == 0:
            return

        # ── Per-column thresholds ────────────────────────────────────────────
        for col in df.columns:
            col_str    = str(col)
            null_count = int(df[col].isnull().sum())
            if null_count == 0:
                continue
            null_pct = (null_count / total_rows) * 100

            if null_pct == 100:
                self.findings.append(Finding(
                    level="ERROR", code="COLUMN_FULLY_NULL",
                    message=(
                        f"Column '{col_str}' is 100% null "
                        f"({null_count}/{total_rows} rows). Entirely empty."
                    ),
                    column=col_str, action="DROP_COLUMN"
                ))
            elif null_pct > 60:
                self.findings.append(Finding(
                    level="WARNING", code="HIGH_NULL_RATE",
                    message=(
                        f"Column '{col_str}' has {null_pct:.1f}% null values "
                        f"({null_count}/{total_rows} rows)."
                    ),
                    column=col_str, action="IMPUTE_WITH_MEDIAN_OR_DROP"
                ))
            elif null_pct > 20:
                self.findings.append(Finding(
                    level="WARNING", code="MODERATE_NULL_RATE",
                    message=(
                        f"Column '{col_str}' has {null_pct:.1f}% null values "
                        f"({null_count}/{total_rows} rows)."
                    ),
                    column=col_str, action="IMPUTE_WITH_MEAN_OR_MEDIAN"
                ))
            else:
                self.findings.append(Finding(
                    level="INFO", code="LOW_NULL_RATE",
                    message=(
                        f"Column '{col_str}' has {null_pct:.1f}% null values "
                        f"({null_count}/{total_rows} rows)."
                    ),
                    column=col_str, action="IMPUTE_WITH_MEAN"
                ))

        # ── Overall dataset null % ───────────────────────────────────────────
        total_cells  = int(df.size)
        total_nulls  = int(df.isnull().sum().sum())
        overall_pct  = (total_nulls / total_cells * 100) if total_cells else 0

        if overall_pct > 50:
            self.findings.append(Finding(
                level="ERROR", code="DATASET_MOSTLY_NULL",
                message=(
                    f"Overall dataset is {overall_pct:.1f}% null "
                    f"({total_nulls}/{total_cells} cells). "
                    "Quality too poor to process reliably."
                ),
                column=None, action="ABORT_PIPELINE"
            ))

        # ── Target column null check ─────────────────────────────────────────
        if self.target_column and self.target_column in df.columns:
            tgt_nulls = int(df[self.target_column].isnull().sum())
            if tgt_nulls > 0:
                self.findings.append(Finding(
                    level="ERROR", code="TARGET_COLUMN_HAS_NULLS",
                    message=(
                        f"Target column '{self.target_column}' has "
                        f"{tgt_nulls} null value(s). "
                        "Model cannot train with missing labels."
                    ),
                    column=self.target_column,
                    action="DROP_NULL_TARGET_ROWS"
                ))

    # =========================================================================
    # CONDITION 6 — Unique Value (Variance) Analysis
    # =========================================================================

    _KNOWN_BINARY_VALUES = {
        0, 1, True, False,
        "0", "1", "Yes", "No", "yes", "no",
        "True", "False", "true", "false"
    }
    _BINARY_NAME_HINTS = [
        "flag", "is_", "has_", "bool", "active",
        "enabled", "gender", "sex", "binary"
    ]

    def _check_6_unique_variance(self):
        df = self.df
        for col in df.columns:
            col_str      = str(col)
            unique_count = int(df[col].nunique())

            # Sub-check A — Zero variance
            if unique_count == 1:
                sample_val = (
                    df[col].dropna().iloc[0]
                    if not df[col].dropna().empty else "N/A"
                )
                self.findings.append(Finding(
                    level="WARNING", code="ZERO_VARIANCE",
                    message=(
                        f"Column '{col_str}' has only 1 unique value "
                        f"('{sample_val}'). Zero variance. "
                        "Useless for ML — will be dropped."
                    ),
                    column=col_str, action="DROP_ZERO_VARIANCE_COLUMN"
                ))
                continue   # no further checks for this col

            # Sub-check B — Near-zero variance (2 unique, non-binary)
            if unique_count == 2:
                is_known_binary = (
                    df[col].dtype == bool
                    or any(kw in col_str.lower()
                           for kw in self._BINARY_NAME_HINTS)
                    or set(df[col].dropna().unique()).issubset(
                        self._KNOWN_BINARY_VALUES)
                )
                if not is_known_binary:
                    self.findings.append(Finding(
                        level="INFO", code="NEAR_ZERO_VARIANCE",
                        message=(
                            f"Column '{col_str}' has only 2 unique values. "
                            "Verify this is intentional."
                        ),
                        column=col_str, action="REVIEW_COLUMN"
                    ))

            # Sub-check C — High cardinality (object/string columns)
            if df[col].dtype == object and unique_count > 50:
                self.findings.append(Finding(
                    level="INFO", code="HIGH_CARDINALITY",
                    message=(
                        f"Column '{col_str}' has {unique_count} unique values. "
                        "Likely an ID column — not suitable as a feature."
                    ),
                    column=col_str,
                    action="FLAG_AS_ID_COLUMN_AND_EXCLUDE"
                ))

    # =========================================================================
    # CONDITION 7 — Schema Detection & Type Mapping
    # =========================================================================

    def _check_7_schema_map(self):
        df         = self.df
        total_rows = len(df)
        schema: dict[str, dict] = {}

        for col in df.columns:
            col_str      = str(col)
            unique_count = int(df[col].nunique())
            nullable     = bool(df[col].isnull().any())
            dtype        = df[col].dtype

            # Determine detected_type
            if total_rows > 0 and unique_count == total_rows:
                detected = "ID"

            elif (dtype == bool
                  or (unique_count == 2
                      and set(df[col].dropna().unique()).issubset(
                          self._KNOWN_BINARY_VALUES))):
                detected = "BOOLEAN"

            elif pd.api.types.is_numeric_dtype(dtype):
                detected = "NUMERIC"

            elif pd.api.types.is_datetime64_any_dtype(dtype):
                detected = "DATETIME"

            elif dtype == object:
                if _col_contains(col_str, self.DATETIME_KEYWORDS):
                    sample = df[col].dropna().head(50)
                    parsed = pd.to_datetime(sample, errors="coerce")
                    if len(parsed) > 0 and parsed.notna().mean() > 0.8:
                        detected = "DATETIME"
                    elif unique_count >= 50:
                        detected = "TEXT"
                    else:
                        detected = "CATEGORICAL"
                elif unique_count >= 50:
                    detected = "TEXT"
                else:
                    detected = "CATEGORICAL"
            else:
                detected = "UNKNOWN"

            entry: dict = {"detected_type": detected, "nullable": nullable}
            if detected == "CATEGORICAL":
                entry["unique_values"] = unique_count
            schema[col_str] = entry

        self.schema_map = schema

        # ── problem_type_hint ────────────────────────────────────────────────
        if self.target_column and self.target_column in schema:
            tgt_type = schema[self.target_column]["detected_type"]
            if tgt_type == "NUMERIC":
                self.problem_type_hint = "REGRESSION"
            elif tgt_type in ("CATEGORICAL", "BOOLEAN"):
                self.problem_type_hint = "CLASSIFICATION"

    # =========================================================================
    # CONDITION 8 — Statistical Distribution Check
    # =========================================================================

    def _check_8_statistics(self):
        df         = self.df
        total_rows = len(df)
        if total_rows == 0:
            return
        stats_out: dict = {}

        for col in df.columns:
            col_str = str(col)
            if not pd.api.types.is_numeric_dtype(df[col].dtype):
                continue

            series = df[col].dropna()
            if len(series) < 3:
                continue

            mean   = float(series.mean())
            median = float(series.median())
            std    = float(series.std())
            mn     = float(series.min())
            mx     = float(series.max())
            skew   = float(scipy_stats.skew(series))
            kurt   = float(scipy_stats.kurtosis(series))

            stats_out[col_str] = {
                "mean":     round(mean,   4),
                "median":   round(median, 4),
                "std":      round(std,    4),
                "min":      round(mn,     4),
                "max":      round(mx,     4),
                "skewness": round(skew,   4),
                "kurtosis": round(kurt,   4),
            }

            # ── Skewness findings ────────────────────────────────────────────
            abs_skew = abs(skew)
            if abs_skew > 3:
                self.findings.append(Finding(
                    level="INFO", code="HIGH_SKEWNESS",
                    message=(
                        f"Column '{col_str}' has skewness={skew:.2f}. "
                        "Heavy tail detected. "
                        "Log transform recommended in Phase 3."
                    ),
                    column=col_str, action="APPLY_LOG_TRANSFORM"
                ))
            elif abs_skew > 1:
                self.findings.append(Finding(
                    level="INFO", code="MODERATE_SKEWNESS",
                    message=(
                        f"Column '{col_str}' has skewness={skew:.2f}. "
                        "Moderate skew. Sqrt transform may help."
                    ),
                    column=col_str, action="CONSIDER_SQRT_TRANSFORM"
                ))

            # ── IQR outlier detection ────────────────────────────────────────
            q1  = float(series.quantile(0.25))
            q3  = float(series.quantile(0.75))
            iqr = q3 - q1
            if iqr == 0:
                continue

            lower         = q1 - 1.5 * iqr
            upper         = q3 + 1.5 * iqr
            outlier_count = int(((series < lower) | (series > upper)).sum())
            outlier_pct   = (outlier_count / total_rows) * 100

            stats_out[col_str].update({
                "outlier_count": outlier_count,
                "outlier_pct":   round(outlier_pct, 2),
                "iqr_bounds":    {
                    "lower": round(lower, 4),
                    "upper": round(upper, 4),
                },
            })

            if outlier_pct > 10:
                self.findings.append(Finding(
                    level="WARNING", code="HIGH_OUTLIER_DENSITY",
                    message=(
                        f"Column '{col_str}' has {outlier_pct:.1f}% outliers "
                        f"({outlier_count} values outside IQR bounds "
                        f"[{lower:.2f}, {upper:.2f}])."
                    ),
                    column=col_str,
                    action="APPLY_IQR_CAPPING_OR_ISOLATION_FOREST"
                ))
            elif outlier_pct > 5:
                self.findings.append(Finding(
                    level="INFO", code="MODERATE_OUTLIER_DENSITY",
                    message=(
                        f"Column '{col_str}' has {outlier_pct:.1f}% outliers "
                        f"({outlier_count} values outside IQR bounds "
                        f"[{lower:.2f}, {upper:.2f}])."
                    ),
                    column=col_str,
                    action="APPLY_IQR_CAPPING_OR_ISOLATION_FOREST"
                ))

        self.stats_summary = stats_out

    # =========================================================================
    # CONDITION 9 — Class Imbalance Check  (Classification only)
    # =========================================================================

    def _check_9_class_imbalance(self):
        if self.problem_type_hint != "CLASSIFICATION":
            return
        if not self.target_column or self.target_column not in self.df.columns:
            return

        tgt = self.df[self.target_column].dropna()
        if len(tgt) == 0:
            return

        vc_norm              = tgt.value_counts(normalize=True) * 100
        self.class_distribution = {
            str(k): round(float(v), 2) for k, v in vc_norm.items()
        }

        dominant_pct   = float(vc_norm.iloc[0])
        dominant_class = str(vc_norm.index[0])

        if dominant_pct > 90:
            self.findings.append(Finding(
                level="WARNING", code="SEVERE_CLASS_IMBALANCE",
                message=(
                    f"Target '{self.target_column}' is {dominant_pct:.1f}% "
                    f"class '{dominant_class}'. Model will always predict "
                    "majority class. SMOTE required."
                ),
                column=self.target_column,
                action="APPLY_SMOTE_OVERSAMPLING"
            ))
        elif dominant_pct > 75:
            self.findings.append(Finding(
                level="INFO", code="MODERATE_CLASS_IMBALANCE",
                message=(
                    f"Target '{self.target_column}' is {dominant_pct:.1f}% "
                    f"class '{dominant_class}'. Moderate class imbalance."
                ),
                column=self.target_column,
                action="APPLY_CLASS_WEIGHT_BALANCING"
            ))
        else:
            self.findings.append(Finding(
                level="INFO", code="CLASS_DISTRIBUTION_HEALTHY",
                message=(
                    f"Target '{self.target_column}' class distribution "
                    f"is healthy (dominant class: {dominant_pct:.1f}%)."
                ),
                column=self.target_column,
                action="NO_RESAMPLING_NEEDED"
            ))

    # =========================================================================
    # CONDITION 10 — Business Rule Validation
    # =========================================================================

    def _check_10_business_rules(self):
        df = self.df
        for col in df.columns:
            col_str = str(col)
            col_low = col_str.lower()

            # ── Numeric range rules ──────────────────────────────────────────
            for keywords, lo, hi in self._NUMERIC_RULES:
                if not any(kw in col_low for kw in keywords):
                    continue
                # coerce to numeric if needed
                if pd.api.types.is_numeric_dtype(df[col].dtype):
                    numeric_series = df[col]
                else:
                    numeric_series = pd.to_numeric(df[col], errors="coerce")

                valid_vals = numeric_series.dropna()
                if hi == float("inf"):
                    violating   = valid_vals[valid_vals < lo]
                    range_label = f">= {lo}"
                else:
                    violating   = valid_vals[(valid_vals < lo) | (valid_vals > hi)]
                    range_label = f"[{lo}–{hi}]"

                v_count = int(len(violating))
                if v_count > 0:
                    examples = violating.head(3).tolist()
                    self.findings.append(Finding(
                        level="WARNING",
                        code="BUSINESS_RULE_VIOLATION",
                        message=(
                            f"Column '{col_str}': {v_count} value(s) outside "
                            f"valid range {range_label}. "
                            f"Examples: {examples}."
                        ),
                        column=col_str,
                        action="CLIP_TO_VALID_RANGE"
                    ))
                break   # only first matching rule per column

            # ── Email format ─────────────────────────────────────────────────
            if "email" in col_low and df[col].dtype == object:
                bad_count = int(
                    df[col].dropna()
                    .apply(lambda v: not bool(self._EMAIL_RE.match(str(v))))
                    .sum()
                )
                if bad_count > 0:
                    self.findings.append(Finding(
                        level="INFO", code="FORMAT_VIOLATION",
                        message=(
                            f"Column '{col_str}': {bad_count} value(s) do not "
                            "match valid email format."
                        ),
                        column=col_str,
                        action="FLAG_INVALID_FORMAT_ROWS"
                    ))

            # ── Phone digit length ───────────────────────────────────────────
            if "phone" in col_low and df[col].dtype == object:
                def _phone_bad(v: str) -> bool:
                    return not (7 <= len(re.sub(r'\D', '', str(v))) <= 15)

                bad_count = int(df[col].dropna().apply(_phone_bad).sum())
                if bad_count > 0:
                    self.findings.append(Finding(
                        level="INFO", code="FORMAT_VIOLATION",
                        message=(
                            f"Column '{col_str}': {bad_count} value(s) have "
                            "invalid phone digit length (expected 7–15 digits)."
                        ),
                        column=col_str,
                        action="FLAG_INVALID_FORMAT_ROWS"
                    ))


# =============================================================================
# Async entry point — called by main.py Kafka consumer
# =============================================================================

async def validate_dataset(dataset_id: str,
                           target_column: Optional[str] = None):
    """
    Fetch dataset from GridFS, run DataValidationService,
    persist ValidationReport to MongoDB.
    """
    logger.info(f"[Phase 2] Validation started for dataset: {dataset_id}")

    # 1. Fetch dataset metadata
    try:
        dataset_oid = ObjectId(dataset_id)
    except Exception:
        logger.error(f"[Phase 2] Invalid dataset_id: {dataset_id}")
        return

    dataset = await db.datasets.find_one({"_id": dataset_oid})
    if not dataset:
        logger.error(f"[Phase 2] Dataset not found: {dataset_id}")
        return

    file_id = dataset.get("fileId")
    if not file_id:
        logger.error(f"[Phase 2] Dataset has no fileId: {dataset_id}")
        return

    # Prefer target_column from dataset metadata if not passed explicitly
    if target_column is None:
        target_column = dataset.get("targetColumn")

    # 2. Download raw file from GridFS
    fs = AsyncIOMotorGridFSBucket(db)
    try:
        grid_out  = await fs.open_download_stream(ObjectId(file_id))
        file_data = await grid_out.read()
    except Exception as e:
        logger.error(f"[Phase 2] GridFS read failed: {e}")
        await db.datasets.update_one(
            {"_id": dataset_oid},
            {"$set": {"status": "failed", "validationError": str(e)}}
        )
        return

    # 3. Parse CSV with Pandas
    try:
        df = pd.read_csv(io.BytesIO(file_data))
    except Exception as e:
        logger.error(f"[Phase 2] CSV parse failed: {e}")
        await db.datasets.update_one(
            {"_id": dataset_oid},
            {"$set": {"status": "failed", "validationError": "Invalid CSV format"}}
        )
        return

    # 4. Run all 10 validation checks
    service = DataValidationService()
    report  = service.validate(df, target_column=target_column)
    report["dataset_id"] = dataset_id

    # 5. Persist report back to MongoDB
    overall_status = report.get("status", "PASSED")
    mongo_status   = "validated" if overall_status != "FAILED" else "validation_failed"
    finding_count  = len(report.get("findings", []))

    await db.datasets.update_one(
        {"_id": dataset_oid},
        {"$set": {
            "status":           mongo_status,
            "currentStep":      3,
            "validationReport": report,
        }}
    )

    logger.info(
        f"[Phase 2] Done — dataset={dataset_id} | "
        f"status={overall_status} | findings={finding_count}"
    )
