from enum import Enum
from typing import Literal, Optional

from pydantic import Field, field_validator

from api.models.no_null_camel_model import NoNullCamelModel

class DomainFilter(str, Enum):
    """OMOP domain filter options for terminology search"""
    ALL = "All"
    CONDITION = "Condition"
    DRUG = "Drug"
    MEASUREMENT = "Measurement"
    OBSERVATION = "Observation"
    PROCEDURE = "Procedure"
    SPECIMEN = "Specimen"
    OTHER = "Other"

MAIN_DOMAINS = [
    DomainFilter.CONDITION.value,
    DomainFilter.DRUG.value,
    DomainFilter.MEASUREMENT.value,
    DomainFilter.OBSERVATION.value,
    DomainFilter.PROCEDURE.value,
    DomainFilter.SPECIMEN.value
]
    
class SearchConceptsRequest(NoNullCamelModel):
    term: str = Field(..., description="Search term (code or name)", min_length=1)
    system: Optional[str] = Field(None, description="Vocabulary/System ID (LOINC, SNOMED, etc.)")
    domain: Optional[DomainFilter] = Field(None, description="OMOP Domain filter")
    sort_by: Literal["name", "code", "system", "relevance"] = Field("relevance", description="What field or condition to sort by")
    sort_order: Literal["asc", "desc"] = Field("asc", description="Sort order")
    page: int = Field(1, ge=1, description="Page number (starts at 1)")
    count: int = Field(20, ge=1, le=50, description="Results per page")
    # TODO: If UI Implements conditional presets checking, this should be changed to a default of False.
    check_for_presets: bool = Field(True, description="Check if preset values are available for returned codes (labs only)")

    @field_validator('domain', mode='before')
    @classmethod
    def normalize_domain(cls, v):
        """Make domain case-insensitive"""
        if v is None or isinstance(v, DomainFilter):
            return v
        
        # Convert string to proper case
        if isinstance(v, str):
            # Try to match case-insensitively
            for member in DomainFilter:
                if v.lower() == member.value.lower():
                    return member
        return v