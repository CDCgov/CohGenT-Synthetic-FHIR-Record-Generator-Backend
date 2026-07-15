"""
Cohort generation configuration models.

This module defines the primary user-facing models for cohort generation,
including CohortSettings (main configuration), EventSet (repeating clinical
data), and MedicationSet (medication configurations).
"""

from datetime import date
from enum import Enum
from fastapi_camelcase import CamelModel
from pydantic import Field as PyField, field_validator, model_validator
from typing import Optional
from api.models.value_types import ValueCoding, ValueLocation, ValueOccupation, ValueRange, ValueWeights, ValueTimeRangeAsDays, ValueRangeWithUnits, ValuePrevalence, ValueTribalAffiliation

type ValueX = bool | str | ValueWeights | ValueLocation | ValueRange | ValueCoding | ValueTimeRangeAsDays | ValueRangeWithUnits | ValuePrevalence | ValueTribalAffiliation | ValueOccupation | None

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
    until: Optional[int] = None # in Days

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
    """
    Complete configuration for cohort generation, submitted by the UI.
    
    This model defines all user-configurable parameters that control how
    synthetic FHIR records are generated, including patient count, temporal
    boundaries, and clinical data specifications.
    
    Relationships:
        - References a UseCase by useCaseId
        - Contains EventSet[] for repeating clinical observations
        - Contains MedicationSet[] for medication generation
    """
    output_format: Optional[OutputFormat] = PyField(
        default=OutputFormat.JSON,
        description="Format for the generated FHIR bundle output. Choose 'json' for a single Bundle resource or 'ndjson' for newline-delimited JSON with individual resources."
    )
    use_case_id: str = PyField(
        ...,
        description="Unique identifier referencing a use case template that defines the clinical scenario, resources, and data structure to generate."
    )
    fhir_version: Optional[str] = PyField(
        default="R4",
        description="FHIR specification version to use for generated resources. Currently only 'R4' is supported."
    )
    us_core_version: Optional[str] = PyField(
        default=None,
        description="US Core Implementation Guide version (e.g., '6.1.0'). Note: Filtering by US Core version is not currently implemented."
    )
    count: int = PyField(
        default=1,
        ge=1,
        le=50,
        description="Number of synthetic patients to generate in the cohort. Must be between 1 and 50."
    )
    seed: int = PyField(
        ...,
        description="Random seed value for reproducible data generation. Using the same seed with identical settings will produce the same synthetic data."
    )
    event_period: EventPeriod = PyField(
        ...,
        description="Time boundaries defining when clinical events occur for all patients in the cohort. Includes start date, end date, and optional extended generation boundary."
    )
    user_responses: Optional[list[Setting]] = PyField(
        default=None,
        description="User-configured field settings that override default use case values. Each setting targets a specific rule_id with a custom value."
    )
    medication_sets: Optional[list[MedicationSet]] = PyField(
        default=None,
        description="Weighted sets of medications to distribute across the patient cohort. Each set has a weight determining how frequently it's assigned to patients."
    )
    event_sets: Optional[list[EventSet]] = PyField(
        default=None,
        description="Repeating clinical event configurations (e.g., lab panels, procedures) that occur at specified intervals throughout the event period."
    )
    
    @field_validator("seed")
    def validate_seed(cls, v):
        """Ensure seed is a positive integer for reproducibility."""
        if v <= 0:
            raise ValueError("Seed must be positive")
        return v