from fastapi_camelcase import CamelModel
from typing import Optional
from pydantic import model_validator
from api.models.value_types import ValuePrevalence, ValueWeights, ValueTimeRangeAsDays

class Option(CamelModel):
    rule_id: str
    label: str
    description: Optional[str] = None
    tooltip: Optional[str] = None
    tags: Optional[list[str]]
    control: str # checkbox | range | weighting | location

    # checkbox
    default_state: Optional[bool] = None

    # range
    default_values: Optional[ValueWeights | ValueTimeRangeAsDays | ValuePrevalence | list[int]] = None
    decimal_spaces_allowed: Optional[bool] = None
    min_max: Optional[tuple[int|float, int|float]] = None

    # weighting
    values: Optional[list[str]] = None
    # default_values reused here

    @model_validator(mode='after')
    def validate_type_dependent_fields(self) -> 'Option':
        if self.control == 'checkbox' and self.default_state is None:
            raise ValueError("DefaultState of bool required when control type checkbox.")
        elif self.control == 'range' and not self.default_values:
            raise ValueError()
        elif self.control == 'weighting' and not self.default_values:
            raise ValueError()
        # TODO:
        # range validation: require default_values, decimal, and min_max
        # weighting validation: require values and default_values
        # weighting validation: match lengths of values and default_values
        # 
        return self