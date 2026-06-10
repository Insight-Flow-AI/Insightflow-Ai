import logging
import time
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
try:
    from xgboost import XGBClassifier
except ImportError:
    XGBClassifier = None
try:
    from lightgbm import LGBMClassifier
except ImportError:
    LGBMClassifier = None

# Use imblearn Pipeline so SMOTE is applied correctly within CV folds
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, KFold
from sklearn.metrics import make_scorer, f1_score, accuracy_score, mean_squared_error, r2_score

logger = logging.getLogger(__name__)

# Map string algorithm names to classes
MODEL_REGISTRY = {
    "LogisticRegression": LogisticRegression,
    "RandomForestClassifier": RandomForestClassifier,
    "GradientBoostingClassifier": GradientBoostingClassifier,
    "SVC": SVC,
    "XGBClassifier": XGBClassifier,
    "LightGBMClassifier": LGBMClassifier
}

def get_base_estimator(algo_name):
    cls = MODEL_REGISTRY.get(algo_name)
    if cls is None:
        raise ValueError(f"Algorithm {algo_name} not supported or library not installed.")
    return cls(random_state=42) if algo_name != "SVC" else cls(random_state=42, probability=True)

def build_pipeline(algo_name, apply_smote=False):
    """
    Constructs a mathematical pipeline to prevent data leakage.
    SMOTE is added if the dataset is heavily imbalanced.
    """
    steps = []
    if apply_smote:
        logger.info(f"Adding SMOTE to {algo_name} pipeline to handle imbalance.")
        steps.append(('smote', SMOTE(random_state=42)))
        
    steps.append(('classifier', get_base_estimator(algo_name)))
    return Pipeline(steps)

def get_cv_strategy(strategy_name, n_splits=5):
    if strategy_name == "StratifiedKFold":
        return StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    return KFold(n_splits=n_splits, shuffle=True, random_state=42)

def train_candidate(algo_name, param_grid, X_train, y_train, strategy_report):
    """
    Trains and tunes a single candidate model using RandomizedSearchCV.
    """
    logger.info(f"Starting tuning for {algo_name}...")
    start_time = time.time()
    
    # 1. Parse strategy
    apply_smote = "SMOTE" in strategy_report.get("preprocessingStrategy", [])
    validation_strategy = strategy_report.get("validationStrategy", "StratifiedKFold")
    
    # Reduce CV splits if dataset is too small
    n_splits = 5
    if len(X_train) < 50:
        n_splits = 3
    
    cv = get_cv_strategy(validation_strategy, n_splits)
    
    # 2. Build Pipeline
    pipeline = build_pipeline(algo_name, apply_smote)
    
    # Prefix hyperparams with 'classifier__' because they are inside the Pipeline!
    pipeline_param_grid = {}
    for key, value in param_grid.items():
        pipeline_param_grid[f"classifier__{key}"] = value
        
    # 3. Setup Search
    search = RandomizedSearchCV(
        estimator=pipeline,
        param_distributions=pipeline_param_grid,
        n_iter=10, # Keep MVP compute low
        cv=cv,
        scoring='f1_macro', # Standard classification metric for MVP
        n_jobs=-1, # Parallelize cross-validation
        random_state=42,
        error_score='raise'
    )
    
    # 4. Execute Training (This is where the heavy lifting happens!)
    try:
        search.fit(X_train, y_train)
    except Exception as e:
        logger.error(f"Training failed for {algo_name}: {e}")
        return None
        
    duration = time.time() - start_time
    logger.info(f"Finished {algo_name} in {duration:.2f}s. Best CV Score: {search.best_score_:.4f}")
    
    # Un-prefix the best parameters for the report
    best_params_clean = {k.replace('classifier__', ''): v for k, v in search.best_params_.items()}
    
    return {
        "algorithm": algo_name,
        "best_estimator": search.best_estimator_,
        "best_hyperparameters": best_params_clean,
        "cv_score_mean": search.best_score_,
        "cv_score_std": search.cv_results_['std_test_score'][search.best_index_],
        "training_time_seconds": duration
    }
