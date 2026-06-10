import logging
from database import db
from bson.objectid import ObjectId

from .dataset_complexity import analyze_complexity
from .model_mapper import map_model_families
from .model_eliminator import eliminate_models
from .candidate_generator import generate_candidates
from .hyperparameter_engine import generate_hyperparameter_grids
from .validation_strategy import generate_validation_strategy
from .resource_planner import estimate_resources
from .automl_strategy import generate_automl_strategy
from .report_generator import generate_report
from .producer import publish_model_selection_complete

logger = logging.getLogger(__name__)

async def process_model_selection(dataset_id: str):
    """
    Main orchestrator for Phase 7
    """
    logger.info(f"[Phase 7] Starting Model Selection for dataset: {dataset_id}")
    
    dataset_oid = ObjectId(dataset_id)
    dataset = await db.datasets.find_one({"_id": dataset_oid})
    
    if not dataset:
        logger.error(f"Dataset {dataset_id} not found.")
        return
        
    problem_report = dataset.get("problemDetectionReport", {})
    understanding_report = dataset.get("understandingReport", {})
    
    problem_type = problem_report.get("problemType", "CLASSIFICATION")
    is_trainable = problem_report.get("trainingFeasibilityReport", {}).get("isTrainable", False)
    
    if not is_trainable:
        logger.info(f"Dataset {dataset_id} is marked as not trainable (likely Clustering without target). Skipping model selection.")
        return
        
    # Extract stats from Phase 5 understanding report
    stats = {
        "total_rows": understanding_report.get("profile", {}).get("total_rows", 0),
        "total_columns": understanding_report.get("profile", {}).get("total_columns", 0)
    }
    class_imbalance = False # simplified for MVP
    
    # 1. Complexity
    complexity = analyze_complexity(stats)
    
    # 2. Map Families
    families = map_model_families(problem_type, "")
    
    # 3. Eliminate
    survivors = eliminate_models(families, complexity)
    
    # 4. Candidates
    candidates = generate_candidates(survivors)
    
    # 5. Hyperparameters
    grids = generate_hyperparameter_grids(candidates)
    
    # 6. Validation
    validation = generate_validation_strategy(problem_type, class_imbalance)
    
    # 7. Resources
    resources = estimate_resources(len(candidates), complexity)
    
    # 8. Strategy
    strategy = generate_automl_strategy(problem_type, class_imbalance)
    
    # 9. Report
    final_report = generate_report(dataset_id, candidates, grids, validation, resources, strategy)
    
    # 10. Update DB
    await db.datasets.update_one(
        {"_id": dataset_oid},
        {"$set": {
            "status": "training_strategy_ready",
            "currentStep": 7,
            "trainingStrategyReport": final_report
        }}
    )
    
    logger.info(f"[Phase 7] Completed for dataset={dataset_id}. Candidates: {len(candidates)}")
    
    # 11. Trigger Phase 8
    publish_model_selection_complete(dataset_id)
