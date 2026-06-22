from api.models.field import Field
from fastapi_camelcase import CamelModel
from typing import Optional

class EntityReference(CamelModel):
    reference_path: str
    target_entity: str

class DynamicReference(CamelModel):
    reference_path: str
    link_identifier: str

class Entity(CamelModel):
    entity_id: str
    abstract: bool
    resource_type: str
    fields: Optional[list[Field]] = None
    base_entity: Optional[str] = None
    profile: Optional[str] = None
    reference_path: Optional[str] = None
    static_references: Optional[list[EntityReference]] = None
    dynamic_references: Optional[list[DynamicReference]] = None