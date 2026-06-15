from fastapi_camelcase import CamelModel
from pydantic import model_validator, Field as PyField
from typing import List, Optional
from api.models.value_types import ValueCoding
from api.features.generation.special_extension_handlers import SpecialExtensions

class BooleanMap(CamelModel):
    value: str = PyField(...)
    map_to: bool = PyField(...)

class ExtensionDetails(CamelModel):
    value_type: str = PyField(...)
    extension_uri: str = PyField(...)
    sub_extensions: Optional[List['ExtensionDetails']] = None
    special_handler: Optional[SpecialExtensions] = PyField(None)

    # TODO: If value_type is complex, must have sub extensions.

ExtensionDetails.model_rebuild()

class Field(CamelModel):
    path: str = PyField(...)
    type: str = PyField(...)
    user_configured: bool = PyField(...)
    user_setting_rule_id: Optional[str] = PyField(None)
    value: Optional[str | bool | ValueCoding] = PyField(None)
    boolean_map: Optional[list[BooleanMap]] = PyField(None)
    extension_details: Optional[ExtensionDetails] = PyField(None)

    @model_validator(mode='after')
    def check_value_exists(self) -> 'Field':
        if not self.user_configured and self.value is None:
            raise ValueError("If field is not configurable by user a static value or special function must be provided.")
        return self

    @model_validator(mode='after')
    def validate_value_type(self) -> 'Field':
        if self.value is None:
            return self  # Skip validation if no value
        
        # Allow special values (start with $) for any type
        if isinstance(self.value, str) and self.value.startswith('$'):
            return self
            
        if self.type == "boolean":
            if not isinstance(self.value, bool):
                raise ValueError(f"Field type 'boolean' requires bool value, got {type(self.value).__name__}")
        elif self.type in ["CodeableConcept", "Coding"]:
            # Allow ValueCoding object OR caret-delimited string
            if isinstance(self.value, ValueCoding):
                pass  # Valid
            elif isinstance(self.value, str):
                # Validate caret-delimited format: "system^code^display"
                if '^' not in self.value:
                    raise ValueError(f"CodeableConcept/Coding string must be caret-delimited format 'system^code^display', got: {self.value}")
            else:
                raise ValueError(f"Field type '{self.type}' requires ValueCoding or caret-delimited string, got {type(self.value).__name__}")

        else:
            # All other types should be strings
            if not isinstance(self.value, str):
                raise ValueError(f"Field type '{self.type}' requires str value, got {type(self.value).__name__}")
        return self