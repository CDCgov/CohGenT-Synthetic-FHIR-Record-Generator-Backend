from datetime import date
from decimal import Decimal
from enum import Enum
from fastapi_camelcase import CamelModel
from pydantic import Field as PydanticField, model_validator
from typing import Optional
from api.models.value_types import ValueCoding, ValueLocation, ValueRange, ValueWeights, ValueTimeRangeAsDays, ValueRangeWithUnits, ValuePrevalence, ValueTribalAffiliation

type ValueX = bool | str | ValueWeights | ValueLocation | ValueRange | ValueCoding | ValueTimeRangeAsDays | ValueRangeWithUnits | ValuePrevalence | ValueTribalAffiliation | None

class Setting(CamelModel):
    rule_id: str
    value: ValueX

class Medication(CamelModel):
    codeable_concept: ValueCoding
    dosage: Optional[str] = None

class MedicationSet(CamelModel):
    medications: list[Medication] = []
    weight: int | float

class EventPeriod(CamelModel):
    start: date
    end: date
    until: Optional[date] = None

    @model_validator(mode='after')
    def validate_dates(self) -> 'EventPeriod':
        if self.end <= self.start:
            raise ValueError("End date must be after start date")
        if self.until is not None and self.until <= self.end:
            raise ValueError("Until date must be after end date")
        return self

class EventSetTiming(CamelModel):
    offset: int # in Days
    repeat: bool
    repeat_timing: Optional[int] = None # in Days

class EventSetEntry(CamelModel):
    type: str
    codeable_concept: ValueCoding
    value: Optional[ValueX] = None
    #TODO: Add model validator for value based on type

class EventSet(CamelModel):
    name: str
    timing: EventSetTiming
    entry: list[EventSetEntry]
    include_diagnostic_report: Optional[bool] = False
    diagnostic_report_concept: Optional[ValueCoding] = None

    @model_validator(mode='after')
    def validate_dr(self) -> 'EventSet':
        if self.include_diagnostic_report and self.diagnostic_report_concept is None:
            raise ValueError("If include_diagnostic_report is true, must include a diagnostic_report_concept.")
        return self

class OutputFormat(str, Enum):
    JSON = "json"
    NDJSON = "ndjson"
    
class CohortSettings(CamelModel):
    output_format: Optional[OutputFormat] = OutputFormat.JSON
    use_case_id: str
    fhir_version: Optional[str] = "R4"
    us_core_version: Optional[str] = None
    count: int = PydanticField(default=1, ge=1, le=50)
    seed: int
    event_period: EventPeriod
    user_responses: Optional[list[Setting]] = None
    medication_sets: Optional[list[MedicationSet]] = None
    event_sets: Optional[list[EventSet]] = None