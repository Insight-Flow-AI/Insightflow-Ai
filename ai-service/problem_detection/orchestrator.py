import os
import io
import json
import logging
import pandas as pd
from bson.objectid import ObjectId
from confluent_kafka import Producer
from motor.motor_asyncio import AsyncIOMotorGridFSBucket

from database import db
from .target_analyzer import analyze_target
from .complexity_analyzer import analyze_complexity
from .classification_detector import detect_classification
from .regression_detector import detect_regression
from .imbalance_detector import analyze_class_imbalance
from .leakage_detector import detect_leakage
from .training_feasibility import evaluate_training_feasibility
from .model_recommender import recommend_models
from .automl_strategy import generate_automl_strategy
from .risk_assessment import assess_risks

logger = logging.getLogger(__name__)

KAFKA_BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC_NEXT = "problem-detected"

producer_conf = {
    'bootstrap.servers': KAFKA_BROKER,
    'client.id': 'ai-service-problem-detection'
}
producer = Producer(producer_conf)

def delivery_report(err, msg):
    if err is not None:
        logger.error(f"[Phase 6] Message delivery failed: {err}")
    else:
        logger.info(f"[Phase 6] Triggered Phase 7 on {msg.topic()} [{msg.partition()}]")

async def process_problem_detection(dataset_id: str):
    logger.info(f"[Phase 6] Started Problem Type Detection for dataset: {dataset_id}")
    
    try:
        dataset_oid = ObjectId(dataset_id)
    except Exception:
        logger.error(f"[Phase 6] Invalid dataset_id: {dataset_id}")
        return

    dataset = await db.datasets.find_one({"_id": dataset_oid})
    if not dataset:
        logger.error(f"[Phase 6] Dataset not found: {dataset_id}")
        return

    engineered_file_id = dataset.get("engineeredFileId")
    if not engineered_file_id:
        logger.error(f"[Phase 6] No engineeredFileId found for {dataset_id}.")
        return

    understanding_report = dataset.get("understandingReport", {})
    target_column = dataset.get("targetColumn")
    health_score = understanding_report.get("healthScore", 100)
    correlation_report = understanding_report.get("correlations", {})

    # Load Engineered CSV
    fs = AsyncIOMotorGridFSBucket(db)
    try:
        grid_out = await fs.open_download_stream(ObjectId(engineered_file_id))
        file_data = await grid_out.read()
        df = pd.read_csv(io.BytesIO(file_data), on_bad_lines='skip', engine='python')
    except Exception as e:
        logger.error(f"[Phase 6] GridFS read failed: {e}")
        return

    # TEMPORARY FIX: If target_column is missing, assume 'Churn' or the LAST column is the target
    # This allows users to test the ML pipeline end-to-end without a UI for selecting the target
    if not target_column and not df.empty:
        if 'Churn' in df.columns:
            target_column = 'Churn'
        else:
            target_column = df.columns[-1]
        logger.info(f"[Phase 6] No target column provided. Auto-selecting column: '{target_column}'")

    # Phase 6 Execution
    target_analysis = analyze_target(df, target_column)
    complexity = analyze_complexity(df)
    
    is_class, class_type = detect_classification(target_analysis)
    is_reg = detect_regression(target_analysis)

    problem_type = "CLUSTERING"
    sub_type = None

    if is_class:
        problem_type = "CLASSIFICATION"
        sub_type = class_type
    elif is_reg:
        problem_type = "REGRESSION"
        
    imbalance_report = analyze_class_imbalance(df, target_column, problem_type)
    leaked_features = detect_leakage(correlation_report, target_column)
    feasibility = evaluate_training_feasibility(target_analysis, complexity, health_score, problem_type)
    
    candidate_models = recommend_models(problem_type, complexity)
    strategy = generate_automl_strategy(problem_type, imbalance_report, leaked_features)
    risk_report = assess_risks(complexity, imbalance_report, leaked_features)

    # Bundle Output
    problem_detection_report = {
        "problemType": problem_type,
        "subType": sub_type,
        "targetAnalysisReport": target_analysis,
        "datasetComplexityReport": complexity,
        "classImbalanceReport": imbalance_report,
        "mlRiskAssessmentReport": risk_report,
        "trainingFeasibilityReport": feasibility,
        "modelRecommendationReport": {
            "candidateModels": candidate_models
        },
        "trainingStrategyReport": strategy
    }

    # Save to MongoDB
    await db.datasets.update_one(
        {"_id": dataset_oid},
        {"$set": {
            "status": "problem_detected",
            "currentStep": 6,
            "problemDetectionReport": problem_detection_report
        }}
    )

    logger.info(f"[Phase 6] Completed for dataset={dataset_id} | Type={problem_type} | Trainable={feasibility['isTrainable']}")

    # Kafka Payload for Phase 7
    event_payload = {
        "datasetId": str(dataset_id),
        "problemType": problem_type,
        "subType": sub_type,
        "trainingReady": feasibility["isTrainable"],
        "datasetComplexity": complexity.get("sizeClass", "Medium").lower(),
        "recommendedModels": candidate_models,
        "recommendedMetric": strategy.get("recommendedMetric"),
        "recommendedValidation": strategy.get("validationStrategy"),
        "recommendedPreprocessing": strategy.get("preprocessingStrategy")
    }

    try:
        producer.produce(
            KAFKA_TOPIC_NEXT, 
            json.dumps(event_payload).encode('utf-8'), 
            callback=delivery_report
        )
        producer.poll(0)
    except Exception as e:
        logger.error(f"[Phase 6] Failed to publish Kafka event for Phase 7: {e}")
