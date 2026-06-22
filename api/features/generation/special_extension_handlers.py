from decimal import Decimal
from enum import Enum

from fastapi import HTTPException
import random

from sqlalchemy import func
from sqlalchemy.orm import Session
from api.models.cohort_settings import Setting
from api.models.value_types import is_value_prevalence, is_value_tribal_affiliation
from api.database.db_other_tables import TribalAffiliation

class SpecialExtensions(str, Enum):
    TRIBAL_AFFILIATION = "tribal-affiliation"

def generate_tribal_affiliation(setting: Setting, main_db: Session):
    # Tribal Affiliation is a two tiered handler.
    # Setting type must be either ValuePrevalence or ValueTribalAffiliation
    if is_value_prevalence(setting.value) or is_value_tribal_affiliation(setting.value):

        # Determine if patient has a Tribal Affiliation at all based on prevalence.
        prevalence: Decimal = setting.value.prevalence
        has_affiliation = random.random() < float(prevalence)

        # If not, return with None.
        if not has_affiliation:
            return None
        
        # If yes, figure out which...
        # Default behavior (None) is randomized affiliation, but if user passes in a specific tribal affiliation, use it.
        specific_tribal_affiliation_code: str | None = None
        if is_value_tribal_affiliation(setting.value):
            specific_tribal_affiliation_code = setting.value.affiliation_code

        if specific_tribal_affiliation_code is not None:
            affiliation = main_db.query(TribalAffiliation).filter(
                TribalAffiliation.code == specific_tribal_affiliation_code
            ).first()
            if not affiliation:
                raise ValueError(f"Tribal affiliation code '{specific_tribal_affiliation_code}' not found")            
            return f"{affiliation.system}^{affiliation.code}^{affiliation.display}"
        else:
            total_count = main_db.query(TribalAffiliation).count()
            random_offset = random.randint(0, total_count - 1)
            affiliation = main_db.query(TribalAffiliation).offset(random_offset).limit(1).first()
            if not affiliation:
                raise ValueError(f"Tribal affiliation selection failed for unknown reason.")
            return f"{affiliation.system}^{affiliation.code}^{affiliation.display}"

    else:
        raise HTTPException(status_code=500, detail=f"Issue processing tribal affiliation setting type. Expected: ValuePrevalence, ValueTribalAffiliation. Found: {type(setting.value)}")
