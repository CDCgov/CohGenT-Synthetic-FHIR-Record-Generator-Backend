from typing import Optional
from loguru import logger
from fastapi import Depends, HTTPException, APIRouter
from pydantic import Field
from api.database.db_other_tables import TribalAffiliation
from api.models.responses.jsonresponse import PrettyJSONResponse
from api.database.database_client import get_main_db
from sqlalchemy.orm import Session
from api.database.db_sample_tables import SampleSettings
from api.models.no_null_camel_model import NoNullCamelModel

'''
Valuesets Router

Provides endpoints for accessing standard medical terminology or related valuesets (e.g., UCUM measurements or census values).
Valuesets are curated lists of codes used for supporting the CohGenT UI.

(Maintenace Note: The "terminology search" feature and it's database are considered to be entirely self contained, is considered
optional and not always present nor fully loaded even if present. Valuesets are more structural and must always be available.)
'''
router = APIRouter()

class SimpleConcept(NoNullCamelModel):
    system: Optional[str] = Field(None)
    code: Optional[str] = Field(None)
    display: Optional[str] = Field(None)
    
    model_config = {"from_attributes": True} 

class SimpleConceptListResponse(NoNullCamelModel):
    total: int
    results: list[SimpleConcept] = Field([])


@router.get("/valuesets/tribal-affiliation", response_class=PrettyJSONResponse)
def get_tribal_affiliations(db: Session = Depends(get_main_db)) -> SimpleConceptListResponse:
    """
    Fetch all US Tribal Affiliations.

    Returns the complete HL7 v3 TribalEntityUS valueset containing tribal entity codes for federally recognized tribes.

    """
    try:
        results = db.query(TribalAffiliation).order_by(TribalAffiliation.display).all()
        concepts = [SimpleConcept.model_validate(aff) for aff in results]
        return SimpleConceptListResponse(total= len(concepts), results=concepts)
    except Exception as e:
        logger.error(f"Error fetching tribal affiliations: {e}")
        raise HTTPException(status_code=500, detail="Error fetching tribal affiliations")
    
from api.database.db_other_tables import Occupation

@router.get("/valuesets/occupation", response_class=PrettyJSONResponse)
def get_occupations(db: Session = Depends(get_main_db)) -> SimpleConceptListResponse:
    """Get list of available occupations for ODH profiles"""
    try:
        results = db.query(Occupation).order_by(Occupation.display).all()
        concepts = [SimpleConcept.model_validate(occ) for occ in results]
        return SimpleConceptListResponse(total=len(concepts), results=concepts)
    except Exception as e:
        logger.error(f"Error fetching occupations: {e}")
        raise HTTPException(status_code=500, detail="Error fetching occupations")
