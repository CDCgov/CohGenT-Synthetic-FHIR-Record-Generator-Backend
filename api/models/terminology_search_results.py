from api.models.no_null_camel_model import NoNullCamelModel
from api.database.db_omop_tables import Concept
from typing import List, Optional
from api.features.terminologysearch.system_map import reverse_lookup_system

class ConceptResult(NoNullCamelModel):
    name: str
    code: str
    system: str
    has_presets: Optional[bool] = None

    @classmethod
    def from_concept_table(cls, concept: Concept, has_presets: bool = False):
        """Create from ORM Concept object."""
        return cls(
            name=concept.concept_name,
            code=concept.concept_code,
            system=reverse_lookup_system(concept.vocabulary_id),
            has_presets=has_presets
        )
    
class TerminologySearchResults(NoNullCamelModel):
    term: str
    system: str | None
    total: int
    count: int
    page: int
    sort_by: str
    sort_order: str
    results: List[ConceptResult]