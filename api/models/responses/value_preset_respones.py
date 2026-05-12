from api.models.no_null_camel_model import NoNullCamelModel
from typing import Optional
from decimal import Decimal
from typing import Any

class ValuePresetResponse(NoNullCamelModel):
    value_type: str
    preset_name: str
    quantity_min: Optional[int | float | Decimal] = None
    quantity_max: Optional[int | float | Decimal] = None
    quantity_unit: Optional[str] = None

class SearchParameters(NoNullCamelModel):
    code: str
    system: str

class ValuePresetSearchResponse(NoNullCamelModel):
    parameters: SearchParameters
    count: int
    results: list[ValuePresetResponse]

class DeleteValuePresetResponse(NoNullCamelModel):
    message: str
    status: int