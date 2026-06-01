from typing import Any, Optional, List
from loguru import logger
from fastapi import Depends, HTTPException, APIRouter
from pydantic import Field
from api.database.db_other_tables import TribalAffiliation
from api.models.responses.jsonresponse import PrettyJSONResponse
from api.database.database_client import get_main_db
from sqlalchemy.orm import Session
from api.database.db_sample_tables import SampleSettings
from api.models.no_null_camel_model import NoNullCamelModel

router = APIRouter()

class SimpleConcept(NoNullCamelModel):
    system: Optional[str] = Field(None)
    code: Optional[str] = Field(None)
    display: Optional[str] = Field(None)
    
    @classmethod
    def from_tribal_affiliation(cls, affiliation: TribalAffiliation):
        """Create from TribalAffiliation database model"""
        return cls(
            system="http://terminology.hl7.org/CodeSystem/v3-TribalEntityUS",  # https://terminology.hl7.org/5.0.0/CodeSystem-v3-TribalEntityUS.html
            code=affiliation.code,
            display=affiliation.display
        )

class SimpleConceptListResponse(NoNullCamelModel):
    total: int
    results: List[SimpleConcept] = Field([])


@router.get("/valuesets/tribal-affiliation", response_class=PrettyJSONResponse)
def get_tribal_affiliations(db: Session = Depends(get_main_db)) -> SimpleConceptListResponse:
    """Fetch all US Tribal Affiliations."""
    try:
        results = db.query(TribalAffiliation).order_by(TribalAffiliation.display).all()
        concepts = [SimpleConcept.from_tribal_affiliation(r) for r in results]
        return SimpleConceptListResponse(total= len(concepts), results=concepts)
    except Exception as e:
        logger.error(f"Error fetching tribal affiliations: {e}")
        raise HTTPException(status_code=500, detail="Error fetching tribal affiliations")