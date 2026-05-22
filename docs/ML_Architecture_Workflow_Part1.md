# InsightFlow AI: Comprehensive ML Workflow Architecture

This document provides a highly detailed, professional-grade explanation of the complete end-to-end Machine Learning workflow for the InsightFlow AI automated data analytics platform. It is designed for final year project discussions, technical documentation, architectural planning, and viva explanations.

---

## Executive Summary & System Architecture

InsightFlow AI is designed to automate the entire lifecycle of data analytics, from dataset ingestion to insight generation. The system is built on a modern microservices architecture:
- **Frontend:** React (Dashboard & User Interface)
- **Backend Core:** Spring Boot (User management, file routing, orchestration)
- **ML Service:** Python FastAPI (Data processing, model training, AI logic)
- **Database:** MongoDB (Metadata, results, configurations)
- **Event Bus:** Apache Kafka (Asynchronous communication)

### Workflow Overview
The system processes data sequentially through an intelligent pipeline:
Upload → Validation → Cleaning → Feature Engineering → Dataset Understanding → Problem Detection → Model Selection → Training → Evaluation → Explainability → Insights → Visualization → Export.

---

## PHASE 1 — DATASET UPLOAD

### 1. Goal of the Phase
To securely accept, parse, and store user datasets while generating the necessary metadata to track the dataset through the ML pipeline.

### 2. Why this phase is important
It forms the entry point of the pipeline. Without robust ingestion, corrupted files or unsupported formats will break downstream processes.

### 3. Input and Output
- **Input:** Raw dataset file (CSV, Excel, JSON) uploaded via the frontend.
- **Output:** A standardized file saved in storage, a generated `dataset_id`, and metadata stored in MongoDB.

### 4. Internal ML Processing Steps
1. The frontend React app sends a multipart/form-data request to the Spring Boot API Gateway.
2. Spring Boot validates the file size and extension.
3. The file is saved to local storage (or AWS S3).
4. Spring Boot creates a MongoDB document containing the `dataset_id`, filename, size, and status (`UPLOADED`).
5. A Kafka event (`dataset-upload`) is published containing the `dataset_id` and file path.
6. The Python FastAPI ML service consumes the Kafka event and loads the dataset into a Pandas DataFrame.

### 5. Algorithms or Techniques Used
- File parsing techniques.
- Event-driven asynchronous messaging.

### 6. Real-World Examples
A retail manager uploads `sales_Q1_2026.csv` to analyze product performance.

### 7. Error Handling Methods
- **File too large:** Throw `PayloadTooLargeException`.
- **Unsupported format:** Return HTTP 415 Unsupported Media Type.
- **Corrupted file:** If Pandas cannot read the file, publish a `dataset-failed` Kafka event.

### 8. Libraries/Frameworks Used
- **Backend:** Spring Web, Spring Kafka, Spring Data MongoDB.
- **ML Service:** Pandas (`pd.read_csv`, `pd.read_json`), FastAPI, Confluent-Kafka.

### 9. API Flow
`React (POST /api/dataset/upload) → Spring Boot → Kafka Event → FastAPI`

### 10. Database Interactions (MongoDB)
```json
{
  "_id": "ds_938475",
  "userId": "user001",
  "filename": "sales_data.csv",
  "status": "UPLOADED",
  "uploadDate": "2026-05-22T10:00:00Z"
}
```

### 11. Example Python Code Snippet
```python
@app.post("/internal/load-dataset")
async def load_dataset(dataset_id: str, file_path: str):
    try:
        df = pd.read_csv(file_path)
        # Store df in memory cache (Redis) or proceed to validation
        return {"status": "success", "rows": len(df), "cols": len(df.columns)}
    except pd.errors.EmptyDataError:
        return {"error": "File is empty"}
```

### 12. Best Practices & Connection to Next Phase
**Best Practice:** Never block the user waiting for ML processing. Return a success response immediately after upload and use WebSockets/SSE to notify them of progress.
**Connection:** Once loaded, the DataFrame is passed directly to the **Data Validation Service**.

---

## PHASE 2 — DATA VALIDATION SERVICE

### 1. Goal of the Phase
To automatically inspect the dataset for structural integrity, schema compliance, missing values, duplicates, and anomalies before applying any transformations.

### 2. Why this phase is important
"Garbage In, Garbage Out" (GIGO). Training an ML model on unvalidated data leads to catastrophic failures in predictions. 

### 3. Input and Output
- **Input:** Raw Pandas DataFrame.
- **Output:** A detailed JSON Validation Report and a flagged DataFrame.

### 4. Internal ML Processing Steps
1. **Schema Validation:** Ensure required columns exist.
2. **Datatype Validation:** Check if a column meant to be numeric contains text.
3. **Missing Value Detection:** Calculate percentage of nulls per column.
4. **Duplicate Detection:** Identify completely identical rows.
5. **Constant Column Detection:** Flag columns where every row has the same value (zero variance).

### 5. Algorithms or Techniques Used
- Pandas profiling operations.
- Rule-based heuristics for schema validation.

### 6. Real-World Examples
A dataset has a "Revenue" column but row 45 contains the string `"N/A"`, causing the entire column to be treated as an `object` rather than `float64`.

### 7. Error Handling Methods
- **High missing values (>80%):** Flag column for deletion (Severity: HIGH).
- **Format mismatch:** Attempt auto-cast; if failed, flag row.

### 8. Libraries/Frameworks Used
- Pandas, Great Expectations (optional for advanced schema validation), Numpy.

### 9. Example JSON Validation Report
```json
{
  "dataset_id": "ds_938475",
  "total_rows": 1000,
  "issues_found": [
    {"type": "MISSING_VALUES", "column": "Age", "percentage": 15, "severity": "MEDIUM"},
    {"type": "DUPLICATE_ROWS", "count": 5, "severity": "LOW"},
    {"type": "CONSTANT_COLUMN", "column": "Country", "severity": "HIGH"}
  ]
}
```

### 10. Connection to Next Phase
The validation report dictates the rules applied by the **Data Cleaning Engine**.

---

## PHASE 3 — DATA CLEANING ENGINE

### 1. Goal of the Phase
To automatically fix the issues identified during validation to produce a clean, ML-ready dataset.

### 2. Why this phase is important
Models cannot mathematically process nulls or infinite values. Outliers can heavily skew linear models.

### 3. Input and Output
- **Input:** Raw DataFrame + Validation Report.
- **Output:** Cleaned DataFrame.

### 4. Internal ML Processing Steps
1. **Drop Columns:** Remove constant columns or columns with >60% missing data.
2. **Imputation:**
   - *Numerical:* Fill missing values with median (robust to outliers).
   - *Categorical:* Fill missing values with the mode (most frequent).
3. **Outlier Handling:** Cap/floor outliers using the IQR (Interquartile Range) method.
4. **Deduplication:** Drop exact duplicate rows.

### 5. Algorithms or Techniques Used
- **IQR (Interquartile Range):** Identifies outliers below Q1 - 1.5*IQR or above Q3 + 1.5*IQR.
- **Z-Score:** Removes values with a standard deviation > 3.
- **Isolation Forest:** For advanced multivariate anomaly detection.

### 6. Example Python Code Snippet
```python
# Imputing missing values intelligently
for col in df.columns:
    if df[col].dtype in ['int64', 'float64']:
        df[col].fillna(df[col].median(), inplace=True)
    else:
        df[col].fillna(df[col].mode()[0], inplace=True)

# Outlier Capping using IQR
Q1 = df['revenue'].quantile(0.25)
Q3 = df['revenue'].quantile(0.75)
IQR = Q3 - Q1
df['revenue'] = np.where(df['revenue'] > (Q3 + 1.5 * IQR), Q3 + 1.5 * IQR, df['revenue'])
```

### 7. Common Challenges & Best Practices
**Challenge:** Imputing heavily skewed data with the mean. 
**Best Practice:** Always use the median for skewed continuous variables.

### 8. Connection to Next Phase
The clean data is passed to the **Feature Engineering Engine** to extract deeper meaning.

---

## PHASE 4 — FEATURE ENGINEERING ENGINE

### 1. Goal of the Phase
To transform raw data into optimized numerical formats and create new features that improve model predictive power.

### 2. Why this phase is important
Machine Learning models only understand numbers. Feature engineering unlocks the hidden patterns in datetime and text data.

### 3. Input and Output
- **Input:** Cleaned DataFrame.
- **Output:** Encoded, scaled, and feature-selected DataFrame.

### 4. Internal ML Processing Steps
1. **Datetime Extraction:** Convert `OrderDate` into `DayOfWeek`, `Month`, `IsWeekend`.
2. **Categorical Encoding:**
   - *Low Cardinality (<10 unique values):* One-Hot Encoding (pd.get_dummies).
   - *High Cardinality:* Label Encoding or Target Encoding.
3. **Scaling/Standardization:** Apply MinMaxScaler or StandardScaler to numeric columns to ensure algorithms like SVM/K-Means treat all features equally.
4. **Feature Selection:** Use Pearson Correlation to drop highly correlated redundant features (multicollinearity).

### 5. Algorithms or Techniques Used
- **PCA (Principal Component Analysis):** For dimensionality reduction if columns > 50.
- **StandardScaler:** (X - μ) / σ

### 6. Connection to Next Phase
The highly optimized matrix of numbers is now ready for **Dataset Understanding** and Model Training.

---

## PHASE 5 — DATASET UNDERSTANDING

### 1. Goal of the Phase
To perform automated Exploratory Data Analysis (EDA) and generate statistical metadata to explain the dataset's shape and distribution to the user.

### 2. Why this phase is important
Users need to trust the data. Automated EDA gives them a quick snapshot of correlations and distributions without writing code.

### 3. Internal ML Processing Steps
1. Calculate mean, median, standard deviation, skewness, and kurtosis.
2. Generate correlation matrices (Pearson/Spearman).
3. Identify the target variable distribution (balanced vs imbalanced).

### 4. Output Example (Sent to Frontend)
```json
{
  "correlations": [
    {"feature_x": "Age", "feature_y": "Salary", "score": 0.85}
  ],
  "skewness": {"Salary": 2.5} // Indicates right-skewed
}
```

---

## PHASE 6 — PROBLEM TYPE DETECTION

### 1. Goal of the Phase
To automatically decide whether the dataset requires a Classification, Regression, Clustering, or Time Series model based on the user's selected "Target" column.

### 2. Decision Logic
- **If target is missing:** Unsupervised Learning (Clustering / Anomaly Detection).
- **If target is continuous (float):** Regression.
- **If target is categorical (string or int with <20 unique values):** Classification.
- **If dataset has a strong sequential DateTime index:** Time Series Forecasting.

### 3. Real-World Example
If the user selects "Customer_Churn" (values: Yes/No), the system detects **Binary Classification**. If they select "House_Price", it detects **Regression**.

---

*(Part 2 will continue with Model Selection, Training, Evaluation, Explainability, and Deployment)*
