from fastapi_camelcase import CamelModel
from pydantic import model_validator, Field as PyField
from typing import Optional
from api.models.value_types import ValueCoding
from api.features.generation.special_extension_handlers import SpecialExtensions

class BooleanMap(CamelModel):
    value: str = PyField(...)
    map_to: bool = PyField(...)

class ExtensionDetails(CamelModel):
    value_type: str = PyField(...)
    extension_uri: str = PyField(...)
    special_handler: Optional[SpecialExtensions] = PyField(None)

class Field(CamelModel):
    path: str = PyField(...)
    type: str = PyField(...)
    user_configured: bool = PyField(...)
    user_setting_rule_id: Optional[str] = PyField(None)
    value: Optional[str | ValueCoding] = PyField(None)
    boolean_map: Optional[list[BooleanMap]] = PyField(None)
    extension_details: Optional[ExtensionDetails] = PyField(None)

    @model_validator(mode='after')
    def check_value_exists(self) -> 'Field':
        if not self.user_configured and self.value is None:
            raise ValueError("If field is not configurable by user a static value or special function must be provided.")
        return self

    # TODO Add model validation based on type
