from fastapi_camelcase import CamelModel
from typing import TypeGuard, Optional
from decimal import Decimal

from pydantic import model_validator

'''
FHIR Aligned Types

The following are types aligned to FHIR to manage inputs where there are strict expectations.
'''
# NOTE: Due to how the input for FHIR Sheets works, ValueCoding is the input for the FHIR CodeableConcept type as well as its aligned Coding type.

class ValueCoding(CamelModel):
    system: Optional[str] = None
    code: Optional[str] = None
    display: Optional[str] = None

    @model_validator(mode='after')
    def check_code_or_display(self) -> 'ValueCoding':
        if not self.code and not self.display:
            raise ValueError('At least either code or display must be provided')
        
        # Remove system (set to None) if code is not present
        if not self.code:
            self.system = None
        return self
    
def is_value_coding(value: object) -> TypeGuard[ValueCoding]:
    return isinstance(value, ValueCoding)

# NOTE: Quantity is not implemented here as it is handled by parsing. To support a static Quantity input, this should be enabled.
# class ValueQuantity(CamelModel):
#     value: Decimal
#     unit: Optional[str] = None

# Internal Types

class ValueRange(CamelModel):
    min: int | Decimal
    max: int | Decimal

def is_value_range(value: object) -> TypeGuard[ValueRange]:
     return isinstance(value, ValueRange)

class ValueRangeWithUnits(CamelModel):
    min: int | Decimal
    max: int | Decimal
    unit: str

def is_value_range_with_units(value: object) -> TypeGuard[ValueRangeWithUnits]:
     return isinstance(value, ValueRangeWithUnits)

class ValueLocation(CamelModel):
    state: Optional[str] = None
    city: Optional[str] = None

def is_value_location(value: object) -> TypeGuard[ValueLocation]:
     return isinstance(value, ValueLocation)

class ValueTimeRangeAsDays(CamelModel):
    start: int
    end: int
    @model_validator(mode='after')
    def check_end_after_start(self) -> 'ValueTimeRangeAsDays':
        if self.end < self.start:
            raise ValueError('End days cannot be smaller than start days.')
        return self
    
def is_value_time_range_as_days(value: object) -> TypeGuard[ValueTimeRangeAsDays]:
     return isinstance(value, ValueTimeRangeAsDays)


'''
NOTE: ValueTimeRangeAsUnits is disabled as support for converting units of time is not currently implemented. Please use ValueTimeRangeAsDays instead.
It does the same thing but just always assume the day conversion has already happened.
'''
# class ValueTimeWithUnits(CamelModel):
#     value: int
#     units: str

# class ValueTimeRangeAsUnits(CamelModel):
#     start: ValueTimeWithUnits
#     end: ValueTimeWithUnits

class ValueWeight(CamelModel):
    value: str
    weight: int | float | Decimal

class ValueWeights(CamelModel):
    values: list[ValueWeight]

def is_value_weights(value: object) -> TypeGuard[ValueWeights]:
    return isinstance(value, ValueWeights)

def is_value_weight(value: object) -> TypeGuard[ValueWeight]:
    return isinstance(value, ValueWeight)