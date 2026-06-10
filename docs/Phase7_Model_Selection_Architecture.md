# PHASE 7 — UNIVERSAL AUTOML MODEL SELECTION & TRAINING STRATEGY ENGINE

**Project Name:** InsightFlow AI
**Document Purpose:** Enterprise Architecture & Implementation Specification for Phase 7

## SECTION 1 — EXECUTIVE SUMMARY

### What is an AutoML Model Selection Engine?
The AutoML Model Selection Engine is a sophisticated orchestration layer that evaluates dataset characteristics to intelligently select, filter, prioritize, and configure the most optimal machine learning algorithms. It replaces the traditional "try everything" brute-force approach with a heuristic-driven, hardware-aware decision engine.

### Why is this phase necessary?
Without an intelligent gatekeeper, AutoML pipelines waste immense compute resources training algorithms that are mathematically doomed to fail. Phase 7 ensures that the algorithms chosen have the correct mathematical capacity for the dataset's specific shape, complexity, and variance.

### Why should unsuitable algorithms be eliminated before training?
Executing GridSearch on an O(N^3) algorithm (like SVM) with a 5-million-row dataset will crash the cloud instance. Similarly, running Deep Learning on 50 rows will catastrophically overfit. Eliminating them prior to execution ensures stability, scalability, and high-quality leaderboard results.

### How does this reduce computational cost?
By shrinking the algorithmic search space and generating tailored, narrow hyperparameter grids based on dataset size, Phase 7 drastically limits the number of cross-validation fits required, directly translating to lowered cloud CPU/GPU billing and faster time-to-insight.

### Role of Phase 7 inside InsightFlow AI
Phase 7 acts as the orchestrator between Problem Detection (Phase 6) and Model Training (Phase 8). It consumes abstract problem types and translates them into a strict, executable JSON payload detailing exactly which Python classes to instantiate and how to train them.

---

## SECTION 2 — OBJECTIVES

* **Business Objectives:** Reduce cloud infrastructure costs and accelerate the delivery of ML models to business stakeholders.
* **Machine Learning Objectives:** Maximize predictive accuracy by matching algorithmic strengths to dataset characteristics and preventing overfitting/underfitting.
* **AutoML Objectives:** Automate the complex, intuitive decision-making process of senior data scientists regarding algorithm selection and hyperparameter bounding.
* **Scalability Objectives:** Support datasets ranging from 100 rows to 10M+ rows without memory exhaustion.
* **Computational Optimization Objectives:** Optimize parallelization (`n_jobs`) and early stopping to conserve compute.
* **User Experience Objectives:** Provide transparent reasoning (Explainable AI) for why certain models were chosen over others.

---

## SECTION 3 — POSITION IN THE ML PIPELINE

Upload
↓
Validation
↓
Cleaning
↓
Feature Engineering
↓
Dataset Understanding
↓
Problem Type Detection (Phase 6)
↓
**Model Selection Engine (Phase 7)**
↓
Model Training (Phase 8)
↓
Evaluation
↓
Explainability
↓
Insight Generation

### Interaction between Phase 6, Phase 7, and Phase 8
* **Phase 6** tells the system *what* the problem is (e.g., Binary Classification with High Imbalance).
* **Phase 7** takes that report, analyzes the dataset's physical footprint, and decides *how* to solve it (e.g., LightGBM with StratifiedKFold and SMOTE).
* **Phase 8** is a pure execution engine that blindly runs the `model.fit()` loop using the exact blueprints provided by Phase 7.

---

## SECTION 4 — INPUT SOURCES

Phase 7 consumes data from MongoDB and Kafka.

* **Engineered Dataset** (Loaded via `engineeredFileId`)
* **Problem Detection Report** (From Phase 6)
* **Dataset Complexity Report** (Calculated internally)
* **Target Analysis Report** (From Phase 5)
* **ML Readiness Report** (From Phase 5)
* **Class Imbalance Report** (From Phase 5)

### Example Kafka Event (`problem-detected` topic)
```json
{
  "eventId": "evt_90123",
  "datasetId": "6a299339ab0f9a235002ce27",
  "problemType": "classification",
  "subType": "binary",
  "trainingReady": true,
  "timestamp": 1781109561597
}
```

---

## SECTION 5 — OUTPUT DESIGN

Phase 7 outputs a comprehensive payload to MongoDB and Kafka.

### Example Output JSON
```json
{
  "datasetId": "6a299339ab0f9a235002ce27",
  "status": "training_strategy_ready",
  "modelSelectionReport": {
    "totalEvaluated": 8,
    "totalEliminated": 5,
    "candidateModelReport": [
      {
        "modelName": "XGBoostClassifier",
        "reason": "Best in class for tabular data",
        "priorityRank": 1,
        "estimatedMemoryMB": 1024
      },
      {
        "modelName": "RandomForestClassifier",
        "reason": "Robust to variance",
        "priorityRank": 2,
        "estimatedMemoryMB": 512
      }
    ]
  },
  "trainingConfigurationReport": {
    "validationStrategy": "StratifiedKFold",
    "k_folds": 5,
    "primaryMetric": "f1_score"
  },
  "hyperparameterStrategyReport": {
    "XGBoostClassifier": {
      "strategy": "RandomizedSearchCV",
      "params": {
        "learning_rate": [0.01, 0.1],
        "max_depth": [3, 5, 7]
      }
    }
  },
  "automlStrategyReport": {
    "applySMOTE": true,
    "earlyStoppingRounds": 50
  },
  "resourcePlanningReport": {
    "estimatedTimeSeconds": 300,
    "parallelJobs": -1
  }
}
```

---

## SECTION 6 — SUPPORTED DATASET TYPES

### Supported (MVP & Standard):
1. **Binary Classification:** Target has exactly 2 classes.
2. **Multi-Class Classification:** Target has 3 to 100 classes.
3. **Regression:** Target is a continuous numeric variable.
4. **Clustering:** Unsupervised grouping (no target).

### Supported (Advanced):
5. **Time Series Forecasting:** Data with a strict sequential datetime index.
6. **Anomaly Detection:** Unsupervised outlier detection.
7. **Mixed Numerical/Categorical:** Standard tabular data.
8. **High-Dimensional Datasets:** Features outnumber rows.
9. **Sparse Datasets:** Heavy zero-variance matrices.
10. **Imbalanced Datasets:** Skewed class distributions.

### Outside MVP Scope:
* **Images, Audio, Video:** Requires Deep Learning/CNNs/Transformers, which have vastly different hardware (GPU cluster) and preprocessing requirements.
* **Graph Data:** Requires Graph Neural Networks (GNNs).
* **Reinforcement Learning:** Requires environment simulation rather than tabular dataset fitting.

---

## SECTION 7 — DATASET COMPLEXITY ANALYZER

This module calculates the physical footprint to guide resource limits.

### Analyzed Metrics:
* Row Count & Column Count
* Number of Features (post-OneHotEncoding)
* Class Imbalance Ratio
* Dataset Sparsity (%)
* Estimated Memory Footprint (Rows * Cols * 8 bytes)

### Categorization:
* **Tiny (<1k rows):** Enforce strict regularization; use simple models to prevent overfitting.
* **Small (1k–10k rows):** Sweet spot. All tabular models are viable.
* **Medium (10k–100k rows):** SVM becomes too slow. Ensembles thrive.
* **Large (100k–1M rows):** LightGBM/XGBoost required. Drop expensive tree-building models like standard RF if features are high.
* **Very Large (>1M rows):** LightGBM required. Implement downsampling for hyperparameter tuning.

---

## SECTION 8 — MODEL FAMILY MAPPING ENGINE

### Binary & Multi-Class Classification:
* **Logistic Regression:** Baseline. Fast, highly interpretable.
* **Decision Tree:** Baseline. Highly interpretable, but weak alone.
* **Random Forest:** Low variance, robust to unscaled data. Computationally heavy on large datasets.
* **Support Vector Machine:** Excellent for complex boundaries. Fails spectacularly on >100k rows.
* **XGBoost:** SOTA accuracy. Prone to overfitting if not tuned.
* **LightGBM:** SOTA speed and memory efficiency on large data.

### Regression:
* **Linear / Ridge / Lasso / ElasticNet:** Baselines. Fast. Ridge handles multicollinearity; Lasso handles feature selection.
* **Random Forest / XGBoost Regressor:** Best for non-linear variance.

### Clustering:
* **K-Means:** Spherical clusters, scales well.
* **DBSCAN:** Density-based, great for anomaly detection.
* **Hierarchical Clustering:** Great for small datasets requiring dendrograms.

### Time Series & Anomaly Detection:
* **ARIMA / Prophet:** Standard forecasting.
* **Isolation Forest / Local Outlier Factor:** Best for detecting point anomalies in tabular data.

---

## SECTION 9 — MODEL ELIMINATION ENGINE

Aggressively removes models to save compute.

### Rules:
* **Size Limit:** IF rows > 100,000 THEN Drop `SVM` and `KNN`.
* **Sparsity Limit:** IF sparsity > 80% THEN Drop `DecisionTrees` (use Linear models or specialized sparse-GBMs).
* **Dimensionality Limit:** IF columns > rows THEN Drop standard Regression (force `Lasso` to penalize/drop features).
* **Time Series Guard:** IF `is_timeseries == False` THEN Drop `ARIMA`, `Prophet`.

---

## SECTION 10 — CANDIDATE MODEL GENERATOR

Produces a ranked list of 3-5 survivors.

### Example (Regression, Medium Dataset):
1. **Ridge Regression:** (Rank 1). Extremely fast baseline.
2. **XGBoost Regressor:** (Rank 2). High accuracy for non-linear data.
3. **Random Forest Regressor:** (Rank 3). Robust fallback.

---

## SECTION 11 — HYPERPARAMETER STRATEGY ENGINE

### Tuning Strategies:
* **GridSearchCV:** Explores every combination. Too slow for production.
* **RandomizedSearchCV (MVP Strategy):** Highly efficient. Explores a random subset of the grid. Best ROI for computation.
* **Optuna / Bayesian (Enterprise Strategy):** Uses probability to hone in on the best parameters.

### Example Grid (Random Forest):
```python
{
  "n_estimators": [100, 200, 500],
  "max_depth": [10, 20, None],
  "min_samples_split": [2, 5, 10]
}
```

---

## SECTION 12 — VALIDATION STRATEGY ENGINE

Determines how to split data to evaluate model performance without bias.

* **Binary / Multi-Class:** `StratifiedKFold` (Ensures class ratios are maintained across all 5 folds).
* **Regression / Clustering:** `KFold`.
* **Time Series:** `TimeSeriesSplit` (Prevents data leakage from the future into the past).
* **Huge Datasets (>1M):** Switch from KFold to simple `TrainTestSplit` (80/20) to save massive amounts of time.

---

## SECTION 13 — PREPROCESSING & SAFETY CHECK ENGINE

Final pre-flight checks:
* Verify `Target` is cleanly encoded (no strings for XGBoost).
* Ensure `NaNs` are fully imputed (Phase 3 validation).
* Drop explicitly marked "Leakage" or "ID" columns.

---

## SECTION 14 — RESOURCE PLANNING ENGINE

Estimates the cluster footprint.
* **Parallel Training:** Suggests `n_jobs=-1` (use all cores).
* **Early Stopping:** Enforces `early_stopping_rounds=20` for XGBoost to halt training if validation accuracy plateaus.
* **Time Estimate:** `Number of Models * K-Folds * Avg Search Iterations`.

---

## SECTION 15 — AUTOML STRATEGY ENGINE

High-level strategic directives generated for Phase 8.
* If Minority Class < 15%: `apply_smote = true`, `metric = f1_score`.
* If Regression: `metric = rmse`.
* Provide a Confidence Score (e.g., 92%) based on dataset health.

---

## SECTION 16 — ML RISK ASSESSMENT

* **Overfitting Risk (HIGH):** Detected if Features > Rows.
* **Class Imbalance Risk (CRITICAL):** Detected if target skew is severe.
* **Memory Exhaustion (MEDIUM):** Detected if Dataset MB > Available RAM limit.

---

## SECTION 17 — ALL POSSIBLE DATASET SCENARIOS

| Scenario | Detection Logic | Models to Avoid | Strategy | Metric |
| :--- | :--- | :--- | :--- | :--- |
| **Binary Class** | Classes == 2 | Regressors | Stratified CV | ROC_AUC / F1 |
| **Multi Class** | Classes > 2 | SVM (slow) | Stratified CV | F1_Macro |
| **Regression** | Target is Float | Classifiers | KFold CV | RMSE / MAE |
| **Imbalanced** | Minority < 10% | Accuracy-optimized | SMOTE, Class Weights | F1_Score |
| **High-Dim** | Cols > Rows/10 | Unpenalized | Lasso / Ridge | Task-dependent |
| **Tiny (<1k)** | Rows < 1000 | Deep Learning | Heavy Regularization | Task-dependent |

---

## SECTION 18 — CONNECTION TO PHASE 8

Phase 7 publishes the comprehensive `trainingStrategyReport` to Kafka. 
Phase 8 (`model_training.py`) deserializes this JSON, dynamically imports the required Scikit-Learn/XGBoost classes, applies the CV strategy, and executes `.fit()`. Phase 8 requires ZERO decision-making logic.

---

## SECTION 19 — MONGODB DESIGN

Refer to Section 5 for the exact JSON structure inserted via `$set` into the `datasets` collection.

---

## SECTION 20 — KAFKA DESIGN

* **Consumer:** `problem-detected` topic.
* **Producer:** `model-selection-complete` topic.

---

## SECTION 21 — FASTAPI MODULE DESIGN

`ai-service/model_selection/`
* `consumer.py`: Kafka listener.
* `selector.py`: Orchestrator tying modules together.
* `dataset_complexity.py`: Generates footprint metrics.
* `model_mapper.py`: Maps problem types to algorithms.
* `model_eliminator.py`: Runs exclusion rules (e.g., memory limits).
* `candidate_generator.py`: Finalizes top 3 models.
* `hyperparameter_engine.py`: Returns parameter grids.
* `validation_strategy.py`: Stratified vs Standard KFold.
* `preprocessing_checker.py`: Validates readiness.
* `resource_planner.py`: CPU/RAM estimates.
* `automl_strategy.py`: Generates SMOTE/Early Stopping flags.
* `risk_assessment.py`: Flags memory/overfitting risks.
* `report_generator.py`: Compiles the final JSON payload.
* `producer.py`: Kafka publisher.

---

## SECTION 22 — COMPLETE INTERNAL WORKFLOW

1. **Receive Event:** Consume `problem-detected`.
2. **Load Data:** Fetch dataset and Phase 6 reports from Mongo.
3. **Analyze Complexity:** Compute physical footprint.
4. **Map Models:** Fetch all possible algorithms for the problem type.
5. **Eliminate:** Strip out algorithms that violate memory/time rules.
6. **Generate Candidates:** Keep the best 3 remaining.
7. **Hyperparameters:** Assign tuning grids to candidates.
8. **Validation:** Determine Cross-Validation strategy.
9. **Strategy & Risk:** Append SMOTE flags and risk warnings.
10. **Save & Publish:** Update MongoDB; fire Kafka event to Phase 8.

---

## SECTION 23 — REAL-WORLD WALKTHROUGH

**Example: Customer Churn (Binary, 10k rows)**
* *Phase 6 Input:* Binary Classification, Imbalanced.
* *Complexity:* Medium.
* *Candidates:* Logistic Regression, Random Forest, XGBoost.
* *Elimination:* None required (10k rows is safe).
* *Strategy:* StratifiedKFold, SMOTE=True, Metric=F1_Score.
* *Kafka Event:* Sent to Phase 8 to begin training these 3 models.

---

## SECTION 24 — MVP IMPLEMENTATION PLAN

**Implement First:**
* Dataset Complexity Analyzer.
* Model Family Mapper.
* Model Elimination Engine.
* Candidate Model Generator.
* Hyperparameter & Validation Generators.
* Kafka/Mongo Integrations.

**Future Enhancements:**
* Meta-Learning (remembering past successes).
* Neural Architecture Search (NAS).

---

## SECTION 25 — ADVANTAGES
Provides an impenetrable safeguard against crashing cloud instances by aggressively filtering out mathematical mismatches.

## SECTION 26 — LIMITATIONS
Rule-based logic in MVP is static; it cannot dynamically learn new rules without code updates.

## SECTION 27 — FUTURE ENHANCEMENTS
Implementing Reinforcement Learning where the Model Selection Engine gets a "reward" based on how fast and accurate Phase 8 runs, allowing it to mathematically learn the best model mapping over time.

## SECTION 28 — CONCLUSION
Phase 7 is the universal routing layer that transforms abstract data intelligence into highly specific, hardware-aware execution plans, ensuring the downstream Model Training phase runs with maximum efficiency and zero configuration guesswork.
