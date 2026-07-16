"""
Terminology search result models for clinical concept lookup.

This module defines models for returning standardized clinical terminology search
results from OMOP vocabulary database queries. Used by the terminology search API
endpoints to provide concept lookup functionality for diagnoses, procedures, labs, etc.
"""

from api.models.no_null_camel_model import NoNullCamelModel
from api.database.db_omop_tables import Concept
from typing import Optional
from api.features.terminologysearch.system_map import reverse_lookup_system
from pydantic import Field as PyField

class ConceptResult(NoNullCamelModel):
    """
    Single clinical concept search result.
    
    Represents one standardized clinical concept (diagnosis, procedure, lab test,
    medication, etc.) from a terminology system like SNOMED CT, LOINC, RxNorm, or
    ICD-10. Converted from OMOP Concept table records for API responses.
    
    Attributes:
        name: Human-readable display name for the concept (e.g., "Type 2 Diabetes Mellitus").
        code: The concept's code within its terminology system (e.g., "44054006" for SNOMED CT).
        system: The translated FHIR URI of the terminology system (e.g., "http://snomed.info/sct").
        domain: OMOP domain classification (e.g., "Condition", "Procedure", "Measurement").
        has_presets: Whether preset value configurations exist for this concept
            (e.g., normal ranges for lab tests).
    
    Example:
        ```
        ConceptResult(
            name="Glucose [Mass/volume] in Serum or Plasma",
            code="2345-7",
            system="http://loinc.org",
            domain="Measurement",
            has_presets=True
        )
        ```
    """
    name: str = PyField(
        ...,
        description="Human-readable display name for the concept."
    )
    code: str = PyField(
        ...,
        description="Concept code within its terminology system."
    )
    system: str = PyField(
        ...,
        description="Canonical URL of the terminology system (e.g., 'http://snomed.info/sct', 'http://loinc.org')."
    )
    domain: str = PyField(
        ...,
        description="OMOP domain classification (e.g., 'Condition', 'Procedure', 'Measurement', 'Drug')."
    )
    has_presets: Optional[bool] = PyField(
        default=None,
        description="Whether preset value configurations exist for this concept (e.g., normal lab ranges)."
    )

    @classmethod
    def from_concept_table(cls, concept: Concept, has_presets: bool = False):
        """
        Create ConceptResult from OMOP Concept ORM object.
        
        Converts an OMOP vocabulary Concept database record into the API response
        format, mapping OMOP vocabulary IDs to FHIR canonical system URLs.
        
        Args:
            concept: OMOP Concept ORM object from database query.
            has_presets: Whether preset configurations exist for this concept.
        
        Returns:
            ConceptResult ready for API response.
        """
        return cls(
            name=concept.concept_name,
            code=concept.concept_code,
            system=reverse_lookup_system(concept.vocabulary_id),
            domain=concept.domain_id,
            has_presets=has_presets
        )
    
class TerminologySearchResults(NoNullCamelModel):
    """
    Paginated terminology search results container.
    
    Wraps a list of concept search results with pagination metadata and search
    parameters. Returned by terminology search API endpoints for concept lookup.
    
    Attributes:
        term: The search term used for this query (e.g., "diabetes", "glucose").
        system: Optional terminology system filter applied (e.g., "http://snomed.info/sct").
        domain: Optional OMOP domain filter applied (e.g., "Condition", "Measurement").
        total: Total number of matching concepts across all pages.
        count: Number of results on this page.
        page: Current page number (1-indexed).
        sort_by: Field used for sorting results (e.g., "name", "code").
        sort_order: Sort direction ("asc" or "desc").
        results: List of concept results on this page.
    
    Example:
        ```
        TerminologySearchResults(
            term="glucose",
            system="http://loinc.org",
            domain="Measurement",
            total=156,
            count=25,
            page=1,
            sort_by="name",
            sort_order="asc",
            results=[...]  # List of ConceptResult objects
        )
        ```
    """
    term: str = PyField(
        ...,
        description="Search term used for this query."
    )
    system: str | None = PyField(
        ...,
        description="Terminology system filter applied (e.g., 'http://snomed.info/sct'), or None for all systems."
    )
    domain: str | None = PyField(
        ...,
        description="OMOP domain filter applied (e.g., 'Condition', 'Measurement'), or None for all domains."
    )
    total: int = PyField(
        ...,
        description="Total number of matching concepts across all pages."
    )
    count: int = PyField(
        ...,
        description="Number of results included on this page."
    )
    page: int = PyField(
        ...,
        description="Current page number (1-indexed)."
    )
    sort_by: str = PyField(
        ...,
        description="Field used for sorting results (e.g., 'name', 'code')."
    )
    sort_order: str = PyField(
        ...,
        description="Sort direction: 'asc' for ascending or 'desc' for descending."
    )
    results: list[ConceptResult] = PyField(
        ...,
        description="List of concept results on this page."
    )