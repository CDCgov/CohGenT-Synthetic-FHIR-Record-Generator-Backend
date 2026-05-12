from typing import Literal, Optional

from pydantic import Field

from api.models.no_null_camel_model import NoNullCamelModel


class SearchConceptsRequest(NoNullCamelModel):
    term: str = Field(..., description="Search term (code or name)", min_length=1)
    system: Optional[str] = Field(None, description="Vocabulary/System ID (LOINC, SNOMED, etc.)")
    sort_by: Literal["name", "code", "system", "relevance"] = Field("relevance", description="What field or condition to sort by")
    sort_order: Literal["asc", "desc"] = Field("asc", description="Sort order")
    page: int = Field(1, ge=1, description="Page number (starts at 1)")
    count: int = Field(20, ge=1, le=50, description="Results per page")