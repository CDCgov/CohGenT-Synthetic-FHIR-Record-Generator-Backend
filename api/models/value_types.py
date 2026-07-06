"""
Value type models for cohort generation user input.

This module defines Pydantic models that represent different types of user-configurable
values in the CohGenT system. These models serve as the building blocks for form
controls and generation parameters, bridging user input with FHIR data generation.

Model Categories:
    - FHIR-Aligned Types: Models that map directly to FHIR datatypes (ValueCoding)
    - Range Types: Numeric and temporal range specifications (ValueRange, ValueTimeRangeAsDays)
    - Distribution Types: Weighted value distributions (ValueWeights, ValuePrevalence)
    - Geographic Types: Location-based values (ValueLocation)
    - Special Types: Domain-specific values (ValueTribalAffiliation)

Each model includes a corresponding TypeGuard function (e.g., is_value_coding) for
runtime type checking and validation.
"""

from fastapi_camelcase import CamelModel
from typing import TypeGuard, Optional
from decimal import Decimal

from pydantic import Field, model_validator


'''
Primitive Types
'''
def is_bool(value: object) -> TypeGuard[bool]:
    '''
    TypeGuard for bool values
    '''
    return isinstance(value, bool)

'''
FHIR Aligned Types

The following are types aligned to FHIR to manage inputs where there are strict expectations.
'''
# NOTE: Due to how the input for FHIR Sheets works, ValueCoding is the input for the FHIR CodeableConcept type as well as its aligned Coding type.

class ValueCoding(CamelModel):
    """
    Represents a coded value with system, code, and display components.
    
    This model maps to both FHIR Coding and CodeableConcept types. It's used
    for any field that requires standardized terminology (diagnoses, lab codes,
    medications, etc.).
    
    Validation:
        - At least one of 'code' or 'display' must be provided
        - If 'code' is absent, 'system' is automatically set to None
    
    Examples:
        Diagnosis: {"system": "http://snomed.info/sct", "code": "44054006", 
                    "display": "Diabetes mellitus type 2"}
        Lab Test: {"system": "http://loinc.org", "code": "2823-3",
                   "display": "Potassium in Serum"}
    """
    system: Optional[str] = Field(default=None, description="The code system URI (e.g., http://loinc.org, http://snomed.info/sct)")
    code: Optional[str] = Field(default=None, description="The code value from the specified system")
    display: Optional[str] = Field(default=None, description="Human-readable display text for the code")

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
    """
    Represents a numeric range with minimum and maximum bounds.
    
    Used for numeric fields like patient age ranges, value ranges for
    measurements, or any scenario requiring a bounded numeric input.
    
    Example:
        Patient age: {"min": 18, "max": 65}
    """
    min: int | Decimal = Field(description="Minimum value (inclusive)")
    max: int | Decimal = Field(description="Maximum value (inclusive)")

def is_value_range(value: object) -> TypeGuard[ValueRange]:
     return isinstance(value, ValueRange)

class ValueRangeWithUnits(ValueRange):
    """
    Numeric range with an associated unit of measure.
    
    Used for clinical measurements that require units, such as lab values
    (glucose mg/dL, potassium mmol/L, etc.).
    
    Example:
        Blood glucose: {"min": 70, "max": 100, "unit": "mg/dL"}
    """
    unit: str = Field(description="Unit of measure (e.g., 'mg/dL', 'mmol/L')")

def is_value_range_with_units(value: object) -> TypeGuard[ValueRangeWithUnits]:
     return isinstance(value, ValueRangeWithUnits)

class ValueLocation(CamelModel):
    """
    Geographic location specification for address generation.
    
    Used to constrain address generation to specific geographic areas.
    Both fields are optional to allow varying levels of specificity.

    Note: If including state only, city generated will be randomized
    but is not gauranteed to be in state. Data is only as "real to life"
    as is provided by users.
    
    Example:
        {"state": "Georgia", "city": "Atlanta"}
        {"state": "California", "city": None}
    """
    state: Optional[str] = Field(default=None, description="US state name for address generation")
    city: Optional[str] = Field(default=None, description="City name for address generation")

def is_value_location(value: object) -> TypeGuard[ValueLocation]:
     return isinstance(value, ValueLocation)

class ValueTimeRangeAsDays(CamelModel):
    """
    Temporal range specified as days relative to a reference date.
    
    Used for relative date calculations in generation, such as onset dates,
    resolution dates, or event timing. Both start and end are offsets in days
    from a reference point (typically the patient's event date).
    
    Validation:
        - End must be >= start (chronologically valid)
        - Use 0,0 to indicate "do not generate" for optional temporal fields
    """
    start: int = Field(description="Start offset in days (can be negative for past dates)")
    end: int = Field(description="End offset in days (can be negative for past dates)")

    @model_validator(mode='after')
    def check_end_after_start(self) -> 'ValueTimeRangeAsDays':
        """Ensure end date is not before start date."""
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
    """
    A single value with an associated weight for distribution.
    
    Used as an element in weighted distributions for demographic or clinical
    parameters.
    """
    value: str = Field(description="The value (e.g., 'Male', 'Female', 'White', 'Asian')")
    weight: int | float = Field(description="Relative weight for this value in the distribution")

class ValueWeights(CamelModel):
    """
    Collection of weighted values for generating distributions.
    
    Used for demographic distributions (gender, race, ethnicity) and other
    categorical fields that require weighted random selection. Weights are
    relative and will be normalized during generation.
    
    Example:
        Gender: {"values": [
            {"value": "Male", "weight": 0.5},
            {"value": "Female", "weight": 0.5},
            {"value": "Unknown", "weight": 0.0}
        ]}
    """
    values: list[ValueWeight] = Field(description="List of values with their associated weights")

def is_value_weights(value: object) -> TypeGuard[ValueWeights]:
    return isinstance(value, ValueWeights)

def is_value_weight(value: object) -> TypeGuard[ValueWeight]:
    return isinstance(value, ValueWeight)

class ValuePrevalence(CamelModel):
    """
    Represents a prevalence rate as a decimal between 0 and 1.
    
    Used for features that appear in a certain percentage of the population
    (e.g., tribal affiliation prevalence).
    
    Example:
        {"prevalence": 0.15}  # 15% of population
    """
    prevalence: Decimal = Field(ge=0, le=1, description="Prevalence rate as decimal (0.0 to 1.0)")

def is_value_prevalence(value: object) -> TypeGuard[ValuePrevalence]:
    return isinstance(value, ValuePrevalence)

class ValueTribalAffiliation(ValuePrevalence):
    """
    Tribal affiliation configuration combining prevalence and optional code.
    
    Extends ValuePrevalence to include an optional tribal affiliation code
    for patients with Native American/Alaska Native heritage. When prevalence
    is set, a random percentage of patients will have tribal affiliation
    extension data generated.
    
    Example:
        {"prevalence": 0.05, "affiliation_code": "1234-5"}  # 5% with specific tribe
        {"prevalence": 0.05, "affiliation_code": None}  # 5% with random tribe
    """
    affiliation_code: Optional[str] = Field(
        default=None,
        description="Specific tribal affiliation code, or None for random selection"
    )

def is_value_tribal_affiliation(value: object) -> TypeGuard[ValueTribalAffiliation]:
    return isinstance(value, ValueTribalAffiliation)