from fastapi_camelcase import CamelModel
from pydantic import model_validator
from typing import Optional
from api.models.value_types import ValueCoding

class BooleanMap(CamelModel):
    value: str
    map_to: bool

class Field(CamelModel):
    path: str
    type: str
    user_configured: bool
    user_setting_rule_id: Optional[str] = None
    value: Optional[str | ValueCoding] = None
    boolean_map: Optional[list[BooleanMap]] = None

    @model_validator(mode='after')
    def check_value_exists(self) -> 'Field':
        if not self.user_configured and self.value is None:
            raise ValueError("If field is not configurable by user a static value or special function must be provided.")
        return self

    # TODO Add model validation based on type
