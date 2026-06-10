# PHASE 6 — INTELLIGENT PROBLEM TYPE DETECTION & AUTOML STRATEGY PREPARATION ENGINE
**Enterprise Architecture & Implementation Document**

**Project:** InsightFlow AI
**Version:** 2.0
**Status:** Architecture Approved

---

## SECTION 1 — EXECUTIVE SUMMARY

### What is Problem Type Detection?
Problem Type Detection is the analytical brain of the AutoML pipeline. It is responsible for mathematically inferring the nature of a machine learning task (e.g., Regression, Classification, Time Series, Clustering) solely by analyzing the structure, variance, and distribution of the dataset and its target variable. 

### Why do enterprise AutoML platforms require a dedicated problem detection stage?
AutoML aims for zero-configuration AI. Enterprise users may not know the difference between logistic regression and linear regression, or when to apply SMOTE. A dedicated problem detection stage bridges the gap between raw data understanding and model training by translating statistical realities into execution strategies.

### How does this phase reduce training failures and wasted computation?
By predicting risks such as severe class imbalance, sparse matrix explosion, or target leakage *before* training begins, this phase acts as a safeguard. It prevents the orchestration engine from instantiating resource-heavy models on mathematically unviable data, saving immense cloud compute costs.

### Why should this phase exist between Dataset Understanding and Model Selection?
Dataset Understanding (Phase 5) provides raw statistics (mean, variance, skewness, correlation). Problem Detection (Phase 6) uses those statistics to establish the rules of engagement. Model Selection (Phase 7) then blindly executes the strategy dictated by Phase 6. Without this intermediate translation layer, Phase 7 would be forced to guess hyperparameters and algorithms.

---

## SECTION 2 — OBJECTIVES

- **Business Objectives:** Democratize AI by completely removing the need for users to manually define their machine learning task type.
- **Machine Learning Objectives:** Ensure algorithms are mathematically compatible with the target distribution.
- **AutoML Objectives:** Generate a definitive "AutoML Strategy Report" detailing exact cross-validation strategies, resampling techniques, and metric selections.
- **User Experience Objectives:** Provide users with transparent, readable reports explaining *why* the AI chose a specific modeling path.
- **Computational Optimization Objectives:** Filter out excessively heavy models (e.g., Deep Learning) for small datasets, or prevent algorithms prone to OOM errors on sparse data.

---

## SECTION 3 — POSITION IN INSIGHTFLOW PIPELINE

**Pipeline Flow:**
Dataset Upload
↓
Validation
↓
Cleaning
↓
Feature Engineering
↓
Dataset Understanding
↓
**Problem Type Detection & AutoML Strategy**
↓
Model Selection
↓
Model Training
↓
Evaluation

### Input/Output Mechanics Between Adjacent Phases
- **From Phase 5 to Phase 6:** Phase 5 provides the deep statistical metrics (skewness, variance, correlations).
- **From Phase 6 to Phase 7:** Phase 6 outputs a `Candidate Model List` and `Training Strategy` (e.g., "Use XGBoost and Logistic Regression with Stratified K-Fold and SMOTE"). Phase 7 uses this list to initialize the exact estimators.

---

## SECTION 4 — INPUT SOURCES

### Phase 6 Consumes:
1. **Engineered Dataset** (`engineeredFileId`): Pulled from MongoDB GridFS.
2. **Validation Report:** To verify initial state and strict rules.
3. **Feature Engineering Report:** To understand one-hot encoding inflation.
4. **Dataset Profile:** Total rows, columns, memory.
5. **Dataset Health Report:** From Phase 5, providing the 0-100 score.
6. **ML Readiness Report:** Flags concerning empty columns.
7. **Business Insight Report:** Natural language correlation findings.
8. **User-selected Target Column** (optional): The column the user wishes to predict.

### Sample Kafka Event (Input)
```json
{
  "dataset_id": "64a2f8b9e4b0d8c1a2f3e4d5",
  "status": "DATASET_UNDERSTOOD",
  "timestamp": "2026-06-10T12:00:00Z"
}
```

### Sample MongoDB Document Snippet (Input)
```json
{
  "_id": ObjectId("64a2f8b9e4b0d8c1a2f3e4d5"),
  "targetColumn": "Churn",
  "engineeredFileId": "64a2f8b9e4b0d8c1a2f3e4d6",
  "understandingReport": {
    "profile": {"rows": 10000, "columns": 50},
    "healthScore": 92
  }
}
```

---

## SECTION 5 — OUTPUT DESIGN

Phase 6 generates an extensive `problemDetectionReport` object appended to the MongoDB dataset document.

### Output JSON Schema
```json
"problemDetectionReport": {
  "problemType": "CLASSIFICATION",
  "subType": "BINARY",
  "targetAnalysisReport": {...},
  "datasetComplexityReport": {...},
  "classImbalanceReport": {...},
  "mlRiskAssessmentReport": {...},
  "trainingFeasibilityReport": {"isTrainable": true, "confidence": 98},
  "modelRecommendationReport": {
    "candidateModels": ["RandomForestClassifier", "XGBoostClassifier", "LogisticRegression"]
  },
  "trainingStrategyReport": {
    "validationStrategy": "StratifiedKFold",
    "preprocessingStrategy": ["SMOTE"],
    "recommendedMetric": "f1_score"
  }
}
```

---

## SECTION 6 — TARGET COLUMN ANALYSIS ENGINE

### Analysis Parameters
- **Does a target column exist?** If NULL → trigger Clustering.
- **Was it selected by the user?** If no, can we infer it? (e.g., the last column).
- **Target Datatype:** Boolean, Categorical, Integer, Float.
- **Number of unique values:** Cardinality check.
- **Missing target labels:** Triggers instant failure or row dropping.
- **Target variance & entropy:** Measures information content.
- **Target cardinality:** E.g., 2 (Binary), 3-20 (Multi-class), >20 (Regression/High Cardinality ID).

### Decision Algorithms
- **Entropy Formula:** `-sum(p * log2(p))` where `p` is the probability of a class. High entropy means perfectly balanced classes.
- **Target Profile JSON Generation:** Bundles the variance, skew, and counts into the `targetAnalysisReport`.

---

## SECTION 7 — PROBLEM TYPE DETECTION ENGINE

### Detection Logic & Rules

- **Binary Classification:**
  - *Conditions:* Target exists. Unique values == 2.
  - *Example:* Churn (Yes/No).
- **Multi-Class Classification:**
  - *Conditions:* Target exists. Datatype is Categorical or Integer. 3 <= Unique values <= 20.
  - *Example:* Risk Level (Low/Medium/High).
- **Multi-Label Classification:**
  - *Conditions:* Target is an array or delimited string indicating multiple true states.
- **Regression:**
  - *Conditions:* Target exists. Datatype is Float/Integer. Unique values > 20. Variance > 0.
  - *Example:* House Price prediction.
- **Time Series Forecasting:**
  - *Conditions:* Target is Numeric. A strictly sequential DateTime column exists.
- **Clustering:**
  - *Conditions:* No target column provided.
- **Anomaly Detection:**
  - *Conditions:* Binary Classification where Minority Class < 1%.

---

## SECTION 8 — DATASET COMPLEXITY ANALYZER

### Calculated Metrics
- **Number of Rows / Features:** Basic dimensions.
- **Dataset Sparsity:** Ratio of zeros to total elements.
- **Feature-to-Sample Ratio:** `n_features / n_samples`. Critical for Overfitting Risk.
- **High Cardinality Features:** Count of text columns with > 100 unique values.

### Classifications
- **Small:** Rows < 1,000.
- **Medium:** 1,000 <= Rows <= 100,000.
- **Large:** Rows > 100,000.
- **High Dimensional:** Features > Rows OR Features > 1,000.
- **Sparse:** Sparsity > 80%.

*Why it matters:* High dimensional, sparse datasets will crash standard Random Forests but excel with Logistic Regression (using L1 regularization).

---

## SECTION 9 — CLASS IMBALANCE ANALYZER

Applies to Classification datasets only.

### Metrics & Recommendations
- **Balanced (40-60%):** No action needed. Standard K-Fold.
- **Mild Imbalance (20-40%):** Recommend Class Weighting. Stratified Split.
- **Severe Imbalance (5-20%):** Recommend SMOTE or Random Oversampling. Use F1-Score / ROC-AUC.
- **Extreme Imbalance (<5%):** Recommend Anomaly Detection models.

---

## SECTION 10 — TIME SERIES DETECTOR

Automatically routes sequential data to specialized ML pipelines (ARIMA/Prophet).

### Detection Logic
- Requires at least one `DateTime` feature.
- Sorts data by DateTime.
- Checks for **Sequential ordering** and **Regular intervals** (e.g., exactly 24 hours between rows).
- If gaps > 10%, flags dataset as irregular and falls back to standard Regression.

---

## SECTION 11 — CLUSTERING & UNSUPERVISED DETECTOR

Triggered when the prediction objective is missing.

### Recommendations
- **K-Means:** Recommended if dataset is mostly numeric, dense, and spherical.
- **DBSCAN:** Recommended if spatial data or high outlier presence.
- **Hierarchical:** Recommended for Small datasets (<2000 rows) for dendrogram visualization.

---

## SECTION 12 — ANOMALY DETECTION DETECTOR

Identifies data meant for Fraud Detection, Network Intrusion, or Predictive Maintenance.

### Recommendations
- **Isolation Forest**
- **One-Class SVM**
- Automatically selects these if `Class Imbalance < 1%`.

---

## SECTION 13 — DATA LEAKAGE & TRAINING SAFETY CHECK

Crucial step to prevent useless models.

### Detection Mechanisms
- **Identifier Columns:** Flags columns where unique values == total rows.
- **Target Leakage / Perfect Correlation:** Pearson correlation > 0.99.
- **Post-event Variables:** Variables that only exist *after* the target event occurs (e.g., "Days_Since_Churned" when predicting "Churn").

*Action:* Automatically adds leaking columns to a `drop_features` list for Phase 7.

---

## SECTION 14 — TRAINING FEASIBILITY ENGINE

The ultimate Gatekeeper for Phase 7.

### Checks
- **Minimum dataset size:** > 100 rows?
- **Minimum samples per class:** > 5 samples for the minority class?
- **Target diversity:** Variance > 0?
- **Leakage status:** Is the target literally a duplicate of a feature?

### Output
```json
"trainingFeasibilityReport": {
  "isTrainable": true,
  "confidenceScore": 95,
  "failureReasons": []
}
```

---

## SECTION 15 — MODEL FAMILY RECOMMENDATION ENGINE

Outputs the exact algorithms Phase 7 must instantiate.

### Classification Candidate List
- **Logistic Regression:** Selected as a baseline. Very fast.
- **Random Forest:** Selected for non-linear interactions. Robust to outliers.
- **XGBoost / LightGBM:** Selected for complex, medium-to-large datasets. Highest accuracy potential.

### Regression Candidate List
- **Linear Regression / Ridge:** Baseline models.
- **Random Forest Regressor:** Non-linear baseline.
- **Gradient Boosting Regressor:** High-performance boosting.

*Cost Analysis:* The engine uses the Complexity Analyzer to drop XGBoost if `Rows < 500` to prevent overfitting.

---

## SECTION 16 — AUTOML STRATEGY ENGINE

Generates the exact operational parameters for Phase 7 execution.

### Strategy Rules Generated
- `validationStrategy`: `StratifiedKFold` (Classification) vs `KFold` (Regression) vs `TimeSeriesSplit`.
- `preprocessingStrategy`: `["SMOTE", "DROP_LEAKAGE_COLS"]`.
- `recommendedMetric`: `f1_score` (Imbalanced), `accuracy` (Balanced), `rmse` (Regression).

---

## SECTION 17 — ML RISK ASSESSMENT ENGINE

Evaluates the dangers of the upcoming training phase.

### Severities
- **Overfitting Risk (HIGH):** If Feature-to-Sample Ratio > 0.5.
- **Leakage Risk (CRITICAL):** If feature-target correlation = 1.0.
- **Sparse Matrix Explosion (MEDIUM):** If One-Hot Encoding created > 1000 columns.

---

## SECTION 18 — ALL POSSIBLE DATASET SCENARIOS

| Scenario | Logic | Impact | Action |
|---|---|---|---|
| Binary Classification | 2 unique target values | Clear classification task | Use LogReg/XGBoost |
| Regression | Continuous numeric target | Standard forecasting | Use Ridge/RandomForest |
| Small Dataset | Rows < 500 | High Overfitting Risk | Restrict complex models (XGBoost) |
| Severe Class Imbalance | Minority < 15% | Model predicts majority | Inject SMOTE to strategy |
| High Dimensionality | Cols > Rows | Mathematical impossibility for OLS | Recommend PCA or L1 Reg |
| Data Leakage Detected | Corr > 0.99 | 100% false accuracy | Drop leaking column |

---

## SECTION 19 — CONNECTION TO PHASE 7

Phase 6 produces a tightly coupled JSON payload that directly dictates Phase 7's execution loop.

### Handoff Process
Phase 6 Output → Candidate Model List → Training Strategy → Phase 7 Model Selection Engine.

### Expected Payload for Phase 7
```json
{
  "datasetId": "64a2f8b9e4b0d8c1a2f3e4d5",
  "problemType": "classification",
  "subType": "binary",
  "trainingReady": true,
  "datasetComplexity": "medium",
  "recommendedModels": [
    "RandomForestClassifier",
    "XGBoostClassifier",
    "LogisticRegression"
  ],
  "recommendedMetric": "f1_score",
  "recommendedValidation": "StratifiedKFold",
  "recommendedPreprocessing": [
    "SMOTE",
    "DROP_COLS_['CustomerID']"
  ]
}
```

---

## SECTION 20 — MONGODB DESIGN

Appends `problemDetectionReport` to the main document.

```json
{
  "_id": ObjectId("64a2f8b9..."),
  "status": "problem_detected",
  "problemDetectionReport": {
    "problemType": "classification",
    "targetAnalysisReport": {"entropy": 0.8},
    "trainingStrategyReport": {"metric": "f1_score"}
  }
}
```

---

## SECTION 21 — KAFKA DESIGN

- **Input Topic:** `dataset-understood`
- **Output Topic:** `problem-detected`

### Workflow
1. Consumer listens for `dataset-understood`.
2. Python service downloads GridFS dataset, runs detection.
3. Produces JSON payload to `problem-detected` to wake up Phase 7 pods.

---

## SECTION 22 — FASTAPI MODULE DESIGN

**Path:** `ai-service/problem_detection/`

- `orchestrator.py`: Main flow coordinator.
- `target_analyzer.py`: Entropy, variance, unique counts.
- `complexity_analyzer.py`: Rows/Cols ratio, sparsity.
- `classification_detector.py`: Logic for binary vs multi-class.
- `regression_detector.py`: Logic for continuous targets.
- `imbalance_detector.py`: Calculates minority percentages.
- `leakage_detector.py`: Finds 0.99 correlations.
- `training_feasibility.py`: The final GATE / validation check.
- `model_recommender.py`: Maps types to Scikit/XGBoost models.
- `automl_strategy.py`: Generates SMOTE/KFold rules.
- `risk_assessment.py`: Flags Overfitting dangers.
- `consumer.py` / `producer.py`: Kafka interfacing.

---

## SECTION 23 — COMPLETE INTERNAL WORKFLOW

1. **Receive Event:** Consumer pulls `dataset-understood`.
2. **Load Engineered Dataset:** Stream CSV from GridFS into Pandas.
3. **Load Understanding Reports:** Fetch Phase 5 metrics from Mongo.
4. **Analyze Target Column:** `target_analyzer.py` calculates entropy.
5. **Determine ML Problem Type:** Check uniqueness to decide Classification vs Regression.
6. **Analyze Dataset Complexity:** Check Row/Col ratio.
7. **Check Class Balance:** Calculate minority %.
8. **Detect Leakage Risks:** Scan correlation matrix.
9. **Evaluate Training Feasibility:** Gating function (Rows > 100?).
10. **Generate Model Family Recommendations:** Output `["XGBoost", "RandomForest"]`.
11. **Generate AutoML Strategy:** Output `SMOTE`, `StratifiedKFold`.
12. **Generate Risk Report:** Output `OVERFITTING_RISK=LOW`.
13. **Save Reports to MongoDB:** `db.datasets.update_one`.
14. **Update Status:** `"status": "problem_detected"`.
15. **Publish Kafka Event:** Dispatch to `problem-detected`.

---

## SECTION 24 — COMPLETE REAL-WORLD WALKTHROUGH

**Scenario:** Customer Churn
- **Input:** 10,000 rows, 45 engineered columns, Target = "Churn".
- **Target Analysis:** 2 unique values. Entropy: 0.72.
- **Problem Type Detection:** Binary Classification.
- **Class Imbalance:** 80% No, 20% Yes (Mild Imbalance).
- **Leakage Detection:** PASS.
- **Training Feasibility:** TRUE. Score: 96.
- **Model Recommendation:** Logistic Regression, Random Forest, LightGBM.
- **AutoML Strategy:** StratifiedKFold, Class Weighting, F1-Score.
- **Final MongoDB Update:** Saved.
- **Kafka Event:** `problem-detected` sent to Phase 7.

---

## SECTION 25 — MVP IMPLEMENTATION PLAN

**Implement First (Core Logic):**
- Target Analysis
- Classification / Regression Detection
- Dataset Complexity Analysis
- Class Imbalance & Leakage Detection
- Training Feasibility Check
- Model Recommendation List Generation
- AutoML Strategy Rules
- Kafka/MongoDB Integrations

**Future Versions (Advanced):**
- Reinforcement Learning & Graph ML detection.
- Deep Learning AutoML planning.
- Multi-Agent Orchestration.

---

## SECTION 26 — ADVANTAGES
- Separates statistical analysis (Phase 5) from execution planning (Phase 6), preventing spaghetti code in the Model Selection engine.
- Prevents expensive cloud compute waste by catching leakage or constant targets *before* model training starts.

## SECTION 27 — LIMITATIONS
- Highly deterministic rule engine. Edge cases (e.g., regression targets that happen to have only 15 unique integer values) might be misclassified as Multi-Class Classification without user override.

## SECTION 28 — FUTURE ENHANCEMENTS
- Transition from a static rule engine to a Meta-Learning model that predicts the best algorithm based on dataset meta-features derived from thousands of past experiments.

## SECTION 29 — CONCLUSION
Phase 6 is the Intelligence Layer of InsightFlow AI. By consuming raw statistical understanding and outputting a highly structured, executable AutoML Strategy, this phase guarantees that Phase 7 Model Selection operates with maximum mathematical safety, optimal algorithm choice, and profound efficiency.
