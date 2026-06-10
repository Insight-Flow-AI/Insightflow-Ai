import logging
import io
import joblib
from database import db
from motor.motor_asyncio import AsyncIOMotorGridFSBucket

logger = logging.getLogger(__name__)

async def serialize_and_save_model(dataset_id: str, algo_name: str, best_estimator):
    """
    Serializes the trained scikit-learn Pipeline using joblib, 
    and saves the binary artifact to MongoDB GridFS.
    """
    try:
        # 1. Serialize to bytes
        buffer = io.BytesIO()
        joblib.dump(best_estimator, buffer)
        buffer.seek(0)
        
        # 2. Upload to GridFS
        fs = AsyncIOMotorGridFSBucket(db)
        filename = f"{dataset_id}_{algo_name}.joblib"
        
        artifact_id = await fs.upload_from_stream(
            filename,
            buffer.read(),
            metadata={
                "dataset_id": dataset_id,
                "algorithm": algo_name,
                "type": "trained_model_pipeline"
            }
        )
        
        logger.info(f"Successfully serialized and saved {algo_name} to GridFS. Artifact ID: {artifact_id}")
        return str(artifact_id)
        
    except Exception as e:
        logger.error(f"Failed to serialize model {algo_name}: {e}")
        return None
