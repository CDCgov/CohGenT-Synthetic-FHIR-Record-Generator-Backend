from api.models.no_null_camel_model import NoNullCamelModel
from decimal import Decimal
from typing import Optional

class CreateValuePreset(NoNullCamelModel):
    code: str
    system: str
    value_type: str
    preset_name: str
    quantity_min: Optional[int | float | Decimal] = None
    quantity_max: Optional[int | float | Decimal] = None
    quantity_unit: Optional[str] = None
    priority: Optional[int] = None

    # TODO: Add value field for strings
    # TODO: Add validation for type (Quantity and string only)
    # TODO: Add constraints on value field by type (require min and max for quantity)

class DeleteValuePreset(NoNullCamelModel):
    code: str
    system: str
    preset_name: str