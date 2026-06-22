from typing import Any, Optional
from loguru import logger
from fastapi import Depends, HTTPException, APIRouter
from api.models.responses.jsonresponse import PrettyJSONResponse
from api.database.database_client import get_main_db
from sqlalchemy.orm import Session
from api.database.db_sample_tables import SampleSettings
from api.models.no_null_camel_model import NoNullCamelModel

router = APIRouter()

# Arbitray JSON record with the metadata field. Cannot validate UI form settings
class SampleSettingsMetaData(NoNullCamelModel):
    start: str
    end: str
    until: Optional[str] = None
    cohort_name: str
    
class SampleSettingsPostBody(NoNullCamelModel):
    metadata: SampleSettingsMetaData

    class Config:
        extra = "allow"

class OperationOutcome(NoNullCamelModel):
    id: int
    message: str
    name: Optional[str] = None
    data: Optional[dict[str, Any]] = None

@router.get("/samples", response_class=PrettyJSONResponse)
def read_samples(db: Session = Depends(get_main_db)):
    """Fetch all sample settings."""
    results = db.query(SampleSettings).order_by(SampleSettings.name).all()
    return results

@router.post("/samples", status_code=201, response_class=PrettyJSONResponse)
def create_sample(sample_post_body: SampleSettingsPostBody, db: Session = Depends(get_main_db)):
    """Create new sample settings."""
    try:
        new_sample = SampleSettings(
            name=sample_post_body.metadata.cohort_name,
            data=sample_post_body.model_dump(by_alias=True, exclude_none=True)
        )
        db.add(new_sample)
        db.commit()
        db.refresh(new_sample)

        logger.info(f"Created new sample with ID {new_sample.id} and name {new_sample.name}.")
        
        return OperationOutcome(
            message="Successfully created new sample settings.",
            id=new_sample.id,
            name=new_sample.name,
            data=new_sample.data
        )
    except Exception:
        db.rollback()
        logger.exception(f"Error creating sample settings: {sample_post_body.metadata.cohort_name}")
        raise HTTPException(status_code=500, detail=f"Failed to create sample. Please try again or contact administrator if this continues.")

@router.delete("/samples", response_class=PrettyJSONResponse)
def delete_sample(id: int, db: Session = Depends(get_main_db)):
    """Delete sample settings.
    
    Args:
        id (int): The ID of the sample to delete.
    
    """
    try:
        sample = db.query(SampleSettings).filter(SampleSettings.id == id).first()
        if not sample:
            raise HTTPException(
                status_code=404,
                detail=f"Sample with id {id} not found."
            )
        else:
            db.delete(sample)
            db.commit()

            logger.info(f"Succesfully deleted sample with ID {id} and name {sample.name}.")
            
            return OperationOutcome(
                    message="Sample deleted successfully",
                    id=id
            )
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception(f"Error deleting sample settings with id {id}")
        raise HTTPException(status_code=500, detail=f"Failed to delete sample. Please try again or contact administrator if this continues.")
    

@router.put("/samples/{id}", response_class=PrettyJSONResponse)
def update_sample(id: int, update_body: SampleSettingsPostBody, db: Session = Depends(get_main_db)):
    """Update an existing sample settings."""
    try:
        # Find existing sample
        sample = db.query(SampleSettings).filter(SampleSettings.id == id).first()
        
        if not sample:
            logger.warning(f"Attempt to update non-existent sample with ID {id}")
            raise HTTPException(
                status_code=404,
                detail=f"Sample with id {id} not found."
            )
        
        if update_body.metadata and update_body.metadata.cohort_name:
            sample.name = update_body.metadata.cohort_name        
        sample.data = update_body.model_dump(by_alias=True, exclude_none=True)
        
        db.commit()
        db.refresh(sample)
        
        logger.info(f"Updated sample with ID {id} (name: {sample.name})")
        
        return OperationOutcome(
            message="Succesfully updated sample.",
            id=sample.id,
            name=sample.name,
            data=sample.data
        )
    
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception(f"Error updating sample settings with id {id}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update sample. Please try again or contact administrator if this continues."
        )