from typing import Literal, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import ColumnElement, and_, case, func, not_, or_, asc, desc
from api.database.db_omop_tables import Concept
from api.models.terminology_search_results import ConceptResult
from api.features.terminologysearch.system_map import lookup_system, fhir_to_omop_systems

def search_concepts(
    db: Session,
    term: str,
    system: Optional[str] = None,
    sort_by: Literal["name", "code", "system", "relevance"] = "relevance",
    sort_order: Literal["asc", "desc"] = "asc",
    page: int = 1,
    count: int = 100
    ):

    # Break up search terms...
    all_terms = [word.strip() for word in term.split() if word.strip()]
    match_conditions: list[ColumnElement[bool]] = []
    for individual_term in all_terms:
        match_conditions.append(
            or_(
                Concept.concept_code.ilike(f"%{individual_term}%"),
                Concept.concept_name.ilike(f"%{individual_term}%")
            )
        )

    # Base Query
    query = db.query(Concept)

     # List of Filters
    filters = []
    
    # 1. Match terms and filter out invalid codes.
    filters.append(and_(*match_conditions))

    filters.append(or_(
        Concept.invalid_reason == '',
        Concept.invalid_reason.is_(None)
    ))

    # 2. Add system filter if present.
    if system:
        omop_vocabulary_id = lookup_system(system)
        if omop_vocabulary_id is None:
            supported_systems = list(fhir_to_omop_systems.keys())
            detail_string = f"Invalid system. Supported systems include: {', '.join(supported_systems)} "
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail_string)
        filters.append(Concept.vocabulary_id == omop_vocabulary_id)
    
    # 3. Filter out non-main LOINC codes.
    filters.append(
        not_(
            or_(
                Concept.concept_code.ilike('LA%'),
                Concept.concept_code.ilike('LP%'),
                Concept.concept_code.ilike('LG%')
            )
        )
    )
    
    # Run all Filters.
    query = query.filter(and_(*filters))

    # Get Total Count.
    total_count: int = query.count()

    # # Setting up Relevance Scoring
    relevance_score = build_relevance_score(term)

    # Handle Sorting
    if sort_by == "relevance" or not sort_by:
        # Sort by relevance first, then alphabetically by name
        if sort_order == "desc":
            query = query.order_by(desc(relevance_score), asc(Concept.concept_name))
        else:
            query = query.order_by(asc(relevance_score), asc(Concept.concept_name))
    else:
        sort_column_map = {
            "name": Concept.concept_name,
            "code": Concept.concept_code,
            "system": Concept.vocabulary_id,
        }
        
        primary_sort = sort_column_map[sort_by]
        
        # Apply sorting
        if sort_order == "desc":
            query = query.order_by(desc(primary_sort), asc(Concept.concept_name))
        else:
            query = query.order_by(asc(primary_sort), asc(Concept.concept_name))
    
    # Pagination
    offset: int = (page - 1) * count
    results = query.offset(offset).limit(count).all()

    # Parse results to Pydantic Model to verify integrity
    results_validated = [ConceptResult.from_concept_table(row) for row in results]
    return results_validated, total_count

def build_relevance_score(search_term: str):
    """
    Build order-sensitive relevance score for concept search.
    Lower scores = higher priority (better match).
    """
    term = search_term.strip()
    all_terms = [t for t in term.split() if t]  # Remove empty strings
    
    conditions = []
    
    # Priority 1: Exact match on code
    conditions.append((func.lower(Concept.concept_code) == term.lower(), 1))
    
    # Priority 2: Exact match on name
    conditions.append((func.lower(Concept.concept_name) == term.lower(), 2))
    
    # Priority 3: Code starts with exact search term
    conditions.append((Concept.concept_code.ilike(f"{term}%"), 3))
    
    # Priority 4: Name starts with exact search term
    conditions.append((Concept.concept_name.ilike(f"{term}%"), 4))
    
    # For multi-word searches - ORDER MATTERS
    if len(all_terms) > 1:
        # Priority 5: Name contains all terms IN ORDER with wildcards between
        # e.g., "Potassium%blood" matches "Potassium [Mass/volume] in Blood"
        in_order_pattern = "%".join(all_terms)
        conditions.append((
            Concept.concept_name.ilike(f"%{in_order_pattern}%"),
            5
        ))
        
        # Priority 6: Code contains all terms IN ORDER
        conditions.append((
            Concept.concept_code.ilike(f"%{in_order_pattern}%"),
            6
        ))
        
        # Priority 7: Name starts with first term AND contains rest in order
        conditions.append((
            Concept.concept_name.ilike(f"{all_terms[0]}%{in_order_pattern[len(all_terms[0]):]}%"),
            7
        ))
        
        # Priority 8: All terms present in name (any order, but lower priority)
        conditions.append((
            and_(*[Concept.concept_name.ilike(f"%{t}%") for t in all_terms]),
            8
        ))
        
        # Priority 9: All terms present in code (any order)
        conditions.append((
            and_(*[Concept.concept_code.ilike(f"%{t}%") for t in all_terms]),
            9
        ))
    
    # Priority 10: Single term or fallback - name contains term
    conditions.append((Concept.concept_name.ilike(f"%{term}%"), 10))
    
    # Priority 11: Code contains term
    conditions.append((Concept.concept_code.ilike(f"%{term}%"), 11))
    
    relevance_score = case(*conditions, else_=99)
    
    return relevance_score