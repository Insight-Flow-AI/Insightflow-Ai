import logging
import time
from database import db
from bson.objectid import ObjectId

from .data_loader import load_and_split_dataset
from .trainer import train_candidate
from .serializer import serialize_and_save_model
from .producer import publish_models_trained

logger = logging.getLogger(__name__)

async def process_model_training(dataset_id: str):
    """
    Main orchestrator for Phase 8: Intelligent AutoML Training.
    """
    logger.info(f"[Phase 8] Starting Model Training for dataset: {dataset_id}")
    start_total_time = time.time()
    
    dataset_oid = ObjectId(dataset_id)
    dataset = await db.datasets.find_one({"_id": dataset_oid})
    
    if not dataset:
        logger.error(f"Dataset {dataset_id} not found.")
        return
        
    # Safety Check
    strategy_report = dataset.get("trainingStrategyReport", {})
    candidates = strategy_report.get("candidateModels", [])
    grids = strategy_report.get("hyperparameterStrategy", {})
    
    if not candidates:
        logger.error(f"[Phase 8] No candidate models found in strategy for {dataset_id}. Aborting.")
        return
        
    # Get inputs for loader
    file_id = dataset.get("engineeredFileId")
    problem_report = dataset.get("problemDetectionReport", {})
    target_col = problem_report.get("targetAnalysisReport", {}).get("columnName")
    problem_type = problem_report.get("problemType", "CLASSIFICATION")
    
    if not file_id or not target_col:
        logger.error(f"[Phase 8] Missing fileId or target_col. Aborting.")
        return
        
    # 1. Load Data and Split Holdout
    try:
        X_train, X_test, y_train, y_test, holdout_file_id = await load_and_split_dataset(
            dataset_id, file_id, target_col, problem_type
        )
    except Exception as e:
        logger.error(f"[Phase 8] Data loading failed: {e}")
        return
        
    trained_models_report = []
    
    # 2. Train Candidates sequentially
    for algo_dict in candidates:
        algo_name = algo_dict["name"]
        param_grid = grids.get(algo_name, {})
        
        # Train & Tune
        result = train_candidate(algo_name, param_grid, X_train, y_train, strategy_report)
        if not result:
            continue
            
        # Serialize
        best_estimator = result.pop("best_estimator")
        artifact_id = await serialize_and_save_model(dataset_id, algo_name, best_estimator)
        
        if artifact_id:
            result["artifact_id"] = artifact_id
            trained_models_report.append(result)
            
    # 3. Generate Final Report
    execution_time = time.time() - start_total_time
    
    training_report = {
        "dataset_id": dataset_id,
        "status": "TRAINING_COMPLETED" if trained_models_report else "TRAINING_FAILED",
        "execution_time_seconds": execution_time,
        "trained_models": trained_models_report,
        "holdout_data_id": holdout_file_id
    }
    
    # 4. Update Database
    await db.datasets.update_one(
        {"_id": dataset_oid},
        {"$set": {
            "status": "models_trained" if trained_models_report else "training_failed",
            "currentStep": 8,
            "trainingReport": training_report
        }}
    )
    
    logger.info(f"[Phase 8] Completed for dataset={dataset_id} in {execution_time:.2f}s. Trained {len(trained_models_report)} models.")
    
    # 5. Trigger Phase 9
    if trained_models_report:
        publish_models_trained(dataset_id, holdout_file_id)
