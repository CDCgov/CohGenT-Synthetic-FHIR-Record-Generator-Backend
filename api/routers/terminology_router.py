from loguru import logger
from fastapi import Body, Depends, Query, status, APIRouter
from api.models.responses.jsonresponse import PrettyJSONResponse
from api.database.db_omop_tables import Concept
from api.database.database_client import get_omop_db
from sqlalchemy.orm import Session
from sqlalchemy import or_, asc, desc
from typing import Optional, Literal
from api.features.terminologysearch import concepts
from api.models.terminology_search_results import TerminologySearchResults
from api.models.requests.search_request import SearchConceptsRequest

router = APIRouter()

@router.get("/terminology/systems", response_class=PrettyJSONResponse)
async def get_systems():
    pass



def _search_concepts_logic(
        term: str,
        system: Optional[str],
        sort_by: Literal["name", "code", "system", "relevance"],
        sort_order: Literal["asc", "desc"],
        page: int,
        count: int,
        db: Session
    ):
    results, total_count = concepts.search_concepts(db, term, system, sort_by, sort_order, page, count)
    return TerminologySearchResults(
            term = term,
            system = system,
            total = total_count,
            count = len(results),
            page = page,
            sort_by = sort_by,
            sort_order = sort_order,
            results = results
        )


@router.get("/terminology/search")
def search_concepts(
        term: str = Query(..., description="Search term (code or name)", min_length=1),
        system: Optional[str] = Query(None, description="Vocabulary/System ID (LOINC, SNOMED, etc.)"),
        sort_by: Literal["name", "code", "system", "relevance"] = Query("relevance", description="What field or condition to sort by"),
        sort_order: Literal["asc", "desc"] = Query("asc", description="Sort order"),
        page: int = Query(1, ge=1, description="Page number (starts at 1)"),
        count: int = Query(20, ge=1, le=50, description="Results per page"),
        db: Session = Depends(get_omop_db)
    ):
    return _search_concepts_logic(term, system, sort_by, sort_order, page, count, db)



@router.post("/terminology/search")
def search_concepts_post(
    request: SearchConceptsRequest = Body(...),
    db: Session = Depends(get_omop_db)
):
    return _search_concepts_logic(
        request.term,
        request.system,
        request.sort_by,
        request.sort_order,
        request.page,
        request.count,
        db
    )