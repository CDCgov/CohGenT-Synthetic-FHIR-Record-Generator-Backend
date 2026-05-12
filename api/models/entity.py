from api.models.field import Field
from fastapi_camelcase import CamelModel
from typing import Optional

class EntityReference(CamelModel):
    reference_path: str
    target_entity: str

class Entity(CamelModel):
    entity_id: str
    abstract: bool
    resource_type: str
    fields: Optional[list[Field]] = None
    base_entity: Optional[str] = None
    profile: Optional[str] = None
    reference_path: Optional[str] = None
    other_references: Optional[list[EntityReference]] = None