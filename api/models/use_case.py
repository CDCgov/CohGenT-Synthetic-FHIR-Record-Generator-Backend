from fastapi_camelcase import CamelModel
from typing import Literal, Optional
from api.models.entity import Entity
from api.models.option import Option


class FormRule(CamelModel):
    step_order: int
    type: str
    title: str
    description: str
    options: Optional[list[Option]] = None

class AdditionalEntity(CamelModel):
    entity_id: str
    type: str
    button_label: str
    entity_file: str
    default_system: Optional[str] = None

class CommonEntities(CamelModel):
    additional_entities: Optional[list[AdditionalEntity]] = None
    medication: Optional[str] = None
    diagnostic_report: Optional[str] = None

class GenerationRules(CamelModel):
    event_date: str
    end_date: Optional[str] = None

class UseCase(CamelModel):
    use_case_id: str
    use_case_version: str
    title: str
    fhir_version: Literal["R4", "R5"]
    us_core_version: Optional[str] = None
    description: str
    generation_rules: Optional[GenerationRules] = None
    form_rules: Optional[list[FormRule]] = None # TODO: Remove optionals once more fleshed out
    entities: Optional[list[Entity]] = None
    common_entities: Optional[CommonEntities] = None