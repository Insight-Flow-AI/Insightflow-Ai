# PHASE 5 — DATASET UNDERSTANDING SERVICE
**Enterprise Architecture & Implementation Document**

**Project:** InsightFlow AI
**Version:** 1.0
**Status:** Architecture Approved

---

## SECTION 1 — EXECUTIVE SUMMARY

### What is Dataset Understanding?
Dataset Understanding is the critical bridge between raw data manipulation and machine learning model training. It involves automatically scanning a processed, mathematically engineered dataset to extract deep statistical insights, identify hidden patterns, and summarize the data’s overall behavior.

### What is Automated EDA?
Exploratory Data Analysis (EDA) is traditionally a manual process where data scientists write code (e.g., Pandas profiling, Matplotlib) to visualize distributions and correlations. Automated EDA performs these steps autonomously, generating machine-readable JSON metadata representing the visual and statistical state of the dataset.

### Why EDA is important before ML training?
Machine Learning algorithms are highly sensitive to data distributions, outliers, and multicollinearity. EDA uncovers whether the dataset is highly imbalanced, heavily skewed, or mathematically noisy, giving the AI pipeline (and the user) the necessary context to select the correct algorithms.

### Why users need Dataset Understanding?
Business users and analysts need to trust the data. Automated EDA provides them with a clear, code-free snapshot of their dataset. Instead of looking at millions of rows of numbers, they receive natural language insights and dynamic visualizations explaining their data.

### Role of Dataset Understanding inside InsightFlow AI
In InsightFlow AI, Phase 5 consumes the engineered matrix from Phase 4 and generates the intellectual metadata required for Phase 6 (Problem Type Detection) and the frontend dashboard visualization.

---

## SECTION 2 — OBJECTIVES

### Business Objectives
- Automate the manual, time-consuming process of exploratory data analysis.
- Provide non-technical users with actionable business insights derived from their raw data.
- Establish trust in the AI pipeline by making the data's characteristics transparent.

### Technical Objectives
- Build a highly scalable, stateless microservice capable of processing large datasets.
- Decouple the analysis engine using Apache Kafka to prevent blocking the main API gateway.
- Standardize the output format into a unified JSON schema for frontend consumption.

### Machine Learning Objectives
- Identify target variable imbalances that require SMOTE or class weighting.
- Identify skewness that might impact linear models.
- Map the correlation matrix to prevent multicollinearity in predictive models.

### User Experience Objectives
- Provide instant, beautiful statistical summaries on the React frontend.
- Translate complex statistics (e.g., Pearson coefficients) into simple human language.

---

## SECTION 3 — POSITION IN PIPELINE

**Pipeline Flow:**
Upload → Validation → Cleaning → Feature Engineering → **Dataset Understanding** → Problem Type Detection

### Input Sources
- Consumes the `feature-engineered` Kafka topic.
- Downloads the engineered CSV matrix from MongoDB GridFS using the `engineeredFileId`.

### MongoDB Integration
- Reads existing metadata from the `datasets` collection.
- Updates the document with massive JSON reports (profiles, stats, correlations).

### Kafka Integration
- **Consumes:** `feature-engineered`
- **Produces:** `dataset-understood` (triggering Phase 6)

### Output Destinations
- MongoDB `datasets` document updates.
- Kafka Event Stream.

---

## SECTION 4 — INPUT DESIGN

**Input Trigger:** Kafka Event on `feature-engineered`
**Data Source:** Engineered dataset stored in GridFS.

### Sample Kafka Message (Input)
```json
{
  "dataset_id": "64a2f8b9e4b0d8c1a2f3e4d5",
  "status": "FEATURE_ENGINEERED",
  "timestamp": "2026-06-09T10:00:00Z"
}
```

### Sample MongoDB Input State
```json
{
  "_id": ObjectId("64a2f8b9e4b0d8c1a2f3e4d5"),
  "status": "feature_engineered",
  "engineeredFileId": "64a2f8b9e4b0d8c1a2f3e4d6",
  "targetColumn": "Churn"
}
```

---

## SECTION 5 — OUTPUT DESIGN

Phase 5 will generate 7 distinct reports grouped under a master `understandingReport` JSON object.

1. **Dataset Profile:** Basic shape and memory footprints.
2. **Statistical Summary:** Mean, median, variance.
3. **Distribution Report:** Skewness and kurtosis.
4. **Correlation Report:** Feature relationships.
5. **Target Analysis Report:** Imbalance metrics.
6. **Dataset Health Report:** Overall quality score (0-100).
7. **Business Insights Report:** Human-readable text.

---

## SECTION 6 — DATASET PROFILER MODULE

This module provides a macro-level view of the engineered dataset.

### Metrics Calculated
- **Rows:** Total observations.
- **Columns:** Total features after Phase 4.
- **Memory Usage:** RAM footprint in MB.
- **Feature Counts:** By data type (Numeric, Categorical, Boolean, Date).
- **Target Column:** Name of the target (if provided).
- **Unique Value Counts:** Cardinality per column.

### Output Format
```json
"profile": {
  "rows": 10500,
  "columns": 38,
  "memory_usage_mb": 4.2,
  "feature_types": { "numeric": 35, "boolean": 3 },
  "target_column": "Churn"
}
```

---

## SECTION 7 — DESCRIPTIVE STATISTICS ENGINE

Calculates standard mathematical statistics for every numeric feature.

### Metrics & Formulas
- **Mean (μ):** Sum of values / N. Average representation.
- **Median:** 50th percentile. Robust to outliers.
- **Mode:** Most frequent value.
- **Minimum/Maximum:** Range boundaries.
- **Variance (σ²):** Average squared deviation from mean.
- **Standard Deviation (σ):** Square root of variance. Spread of data.
- **Percentiles:** 25th (Q1), 50th (Q2), 75th (Q3).

### Business Interpretation
Standard deviation indicates volatility (e.g., highly volatile customer spending). Percentiles indicate distribution clusters.

---

## SECTION 8 — DISTRIBUTION ANALYSIS ENGINE

Determines the mathematical shape of the data.

### Detectable Shapes
- **Normal Distribution:** Bell curve (Skewness ≈ 0).
- **Left Skew:** Tail trails to the left (Negative Skewness).
- **Right Skew:** Tail trails to the right (Positive Skewness).
- **Uniform:** Flat distribution.

### Core Metrics
- **Skewness:** Measure of asymmetry.
  - *Formula:* `E[(X - μ)³] / σ³`
- **Kurtosis:** Measure of tailedness (outlier density).
  - *Formula:* `E[(X - μ)⁴] / σ⁴`

---

## SECTION 9 — CORRELATION ANALYSIS ENGINE

Analyzes how features move in relation to one another.

### Pearson Correlation
Measures linear relationships between -1 and 1.
- *Formula:* `cov(X,Y) / (σX * σY)`

### Correlation Strength Categories
- **Strong Positive:** 0.7 to 1.0 (As X goes up, Y goes up).
- **Strong Negative:** -1.0 to -0.7 (As X goes up, Y goes down).
- **Weak:** -0.3 to 0.3.
- **No Correlation:** ≈ 0.

### Interpretation Logic
If "Tenure" and "Total Charges" have a 0.85 correlation, they are Strongly Positive. The engine flags this for the Insight Generator.

---

## SECTION 10 — TARGET ANALYSIS ENGINE

Provides dedicated focus on the variable we intend to predict.

### For Classification (Categorical Target)
- **Class Balance:** Ratio of classes.
- **Imbalance Detection:** If minority class is < 20% of the dataset, flag as heavily imbalanced.

### For Regression (Numeric Target)
- **Target Distribution:** Skewness of the target.
- **Target Variance:** Spread of the prediction space.

---

## SECTION 11 — DATASET HEALTH ENGINE

Generates a unified `Dataset Health Score` from 0 to 100.

### Score Components
1. **Completeness (20%):** Nulls remaining (should be 0 after Phase 3).
2. **Distribution Quality (30%):** Penalty for extreme skewness > |3|.
3. **Feature Quality (30%):** Penalty for high multicollinearity (>0.90 pairs).
4. **Target Quality (20%):** Penalty for extreme class imbalance (< 10% minority).

---

## SECTION 12 — AUTOMATED INSIGHT GENERATION

Translates raw mathematics into human-readable business rules.

### Rule Engine Examples
- *Rule 1 (Correlation):* If `corr(A, B) > 0.8`, generate: "Feature A strongly influences Feature B."
- *Rule 2 (Imbalance):* If `minority_class < 0.15`, generate: "The Target variable is highly imbalanced, which may affect predictive accuracy."
- *Rule 3 (Skewness):* If `skewness(A) > 2.0`, generate: "Feature A is heavily right-skewed, indicating most values are concentrated on the lower end."

---

## SECTION 13 — EDA VISUALIZATION GENERATOR

Instead of generating images (which are heavy), the engine generates JSON metadata that the React frontend (using Recharts or Chart.js) renders.

### Output Structure Example (Histogram Metadata)
```json
"visualizations": {
  "histograms": [
    {
      "column": "Age",
      "bins": [
        {"range": "0-10", "count": 150},
        {"range": "11-20", "count": 450}
      ]
    }
  ]
}
```

---

## SECTION 14 — MONGODB DESIGN

The `datasets` collection document will be appended with an `understandingReport` object.

```json
{
  "understandingReport": {
    "profile": {...},
    "statistics": {...},
    "distributions": {...},
    "correlations": {...},
    "targetAnalysis": {...},
    "healthScore": 85,
    "insights": ["...", "..."],
    "visualizations": {...}
  }
}
```

---

## SECTION 15 — KAFKA DESIGN

### Workflow
1. Consume `feature-engineered`.
2. Process Phase 5.
3. Produce `dataset-understood`.

### Output Message Example
```json
{
  "dataset_id": "64a2f8b9e4b0d8c1a2f3e4d5",
  "status": "DATASET_UNDERSTOOD",
  "health_score": 85
}
```

---

## SECTION 16 — FASTAPI DESIGN

**Module Layout (`ai-service/dataset_understanding/`):**
- `orchestrator.py`: Main coordinator.
- `profiler.py`: Row/col/memory stats.
- `statistics.py`: Mean, median, percentiles.
- `distribution.py`: Skewness, kurtosis.
- `correlation.py`: Pearson matrix.
- `target_analysis.py`: Class imbalance logic.
- `health_score.py`: 0-100 scoring engine.
- `insight_generator.py`: NLP text rules.
- `viz_metadata.py`: Histogram/Scatter binning.

---

## SECTION 17 — COMPLETE INTERNAL WORKFLOW

1. **Receive Event:** Consume Kafka `feature-engineered`.
2. **Load:** Stream engineered CSV from GridFS into Pandas DataFrame.
3. **Profile:** Count rows, columns, memory.
4. **Stats:** Vectorized calculations for descriptive stats.
5. **Distribution:** Scipy kurtosis/skewness calculations.
6. **Correlation:** Pandas `.corr()`.
7. **Target Analysis:** Value counts on target.
8. **Health:** Weighted average calculation.
9. **Insights:** If/Else rule engine matching thresholds.
10. **Viz Metadata:** `np.histogram()` for binning data.
11. **Save:** Update MongoDB.
12. **Publish:** Produce Kafka `dataset-understood` event.

---

## SECTION 18 — SPECIAL CASE HANDLING

- **No Target Column:** Skip Target Analysis.
- **Extremely Wide Datasets (>1000 cols):** Limit correlation matrix to top 50 highly varying features to prevent OOM errors.
- **Empty Dataset:** Throw Kafka error event `understanding_failed`.
- **All Features Categorical:** Skip Pearson correlation, use Cramér's V (Future).

---

## SECTION 19 — SCALABILITY DESIGN

- **Sampling Strategy:** If Rows > 500,000, perform correlation and distribution analysis on a random 10% sample to save CPU cycles. Descriptive statistics are cheap and run on the full dataset.
- **Memory Optimization:** Downcast float64 to float32 before math operations.
- **Future Dask Support:** The orchestrator can easily swap `pandas.read_csv` for `dask.dataframe.read_csv`.

---

## SECTION 20 — LOGGING & MONITORING

- **Structured Logs:** Every module logs execution time. Example: `[Phase 5] Correlation Matrix generated in 1.2s`.
- **Error Tracking:** Wrapped in broad try-except blocks. Failure in visualization metadata generation will not fail the whole pipeline; it will just return empty viz blocks.

---

## SECTION 21 — REAL WORLD EXAMPLE

**Input:** Customer Churn Matrix.
**Output:**
- *Profile:* 10,000 rows, 45 cols.
- *Health Score:* 88/100 (Slight imbalance).
- *Insights:* "MonthlyCharges strongly influences Churn."
- *Target:* Churn (Yes: 20%, No: 80% — Imbalanced flagged).

---

## SECTION 22 — ALL POSSIBLE OUTCOMES

1. **Success:** All modules run, score 80-100.
2. **Weak Dataset:** Correlation fails due to zero variance left. Score < 50.
3. **Imbalanced Dataset:** Target analysis triggers imbalance flag. Score 60-70.
4. **Dataset Failure:** GridFS stream breaks. Catch and log `UNDERSTANDING_FAILED`.

---

## SECTION 23 — MVP SCOPE

**Implement for MVP:**
- Basic Profiling
- Descriptive Stats
- Pearson Correlation
- Target Analysis (Imbalance)
- Rule-based Insights
- Health Score Math
- Histogram Metadata Generation

**Skip for MVP:**
- Drift Detection
- Causal Inference
- Automated Hypothesis Testing (p-values)

---

## SECTION 24 — ADVANTAGES
- **Transparency:** The user mathematically understands what the AI sees.
- **Speed:** Replaces 2 hours of manual Jupyter Notebook EDA with 5 seconds of backend processing.
- **Safety:** Prevents deploying models trained on severely skewed/imbalanced data.

## SECTION 25 — LIMITATIONS
- Pearson correlation only detects linear relationships, missing non-linear dependencies.
- Very large datasets without sampling will spike FastAPI RAM usage.

## SECTION 26 — FUTURE ENHANCEMENTS
- Add SHAP values for pre-training feature importance.
- Add Cramér's V for Categorical-Categorical correlation.
- Add Automated Data Storytelling (Generative AI summary of the stats).

## SECTION 27 — CONCLUSION
Phase 5 Dataset Understanding transforms a black-box machine learning pipeline into a glass-box analytics engine. By autonomously generating statistical metadata, visualizations, and human-readable insights, InsightFlow AI empowers users to trust their data before a single model is ever trained.
