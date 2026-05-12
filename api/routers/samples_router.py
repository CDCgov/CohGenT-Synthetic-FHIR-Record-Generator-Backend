from typing import Any, Dict, Optional

from loguru import logger
from fastapi import Depends, HTTPException, APIRouter
from api.models.responses.jsonresponse import PrettyJSONResponse
from api.database.database_client import get_main_db
from sqlalchemy.orm import Session
from api.database.db_sample_tables import SampleSettings
from api.models.no_null_camel_model import NoNullCamelModel

router = APIRouter()

# Arbitray JSON record with a the metadata field. Cannot validate UI form settings
class SampleSettingsMetaData(NoNullCamelModel):
    start: str
    end: str
    until: Optional[str] = None
    cohort_name: str
    
class SampleSettingsPostBody(NoNullCamelModel):
    metadata: SampleSettingsMetaData

    class Config:
        extra = "allow" 

@router.get("/samples", response_class=PrettyJSONResponse)
def read_samples(db: Session = Depends(get_main_db)):
    results = db.query(SampleSettings).order_by(SampleSettings.name).all()
    return results

@router.post("/samples", response_class=PrettyJSONResponse)
def create_sample(sample_post_body: SampleSettingsPostBody, db: Session = Depends(get_main_db)):
    try:
        new_sample = SampleSettings(
            name=sample_post_body.metadata.cohort_name,
            data=sample_post_body.model_dump_json(by_alias=True, exclude_none=True)
        )
        db.add(new_sample)
        db.commit()
        db.refresh(new_sample)
        
        return {
            "id": new_sample.id,
            "name": new_sample.name,
            "data": new_sample.data
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/samples", response_class=PrettyJSONResponse)
def delete_sample(id: int, db: Session = Depends(get_main_db)):
    try:
        sample = db.query(SampleSettings).filter(SampleSettings.id == id).first()
        if sample:
            db.delete(sample)
            db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail= str(e))
# Update Not Implemented - Delete and re-create for now.