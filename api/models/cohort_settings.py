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
"""Union type for all possible field setting values.

Encompasses the various value types that can be configured for cohort generation
fields, including simple types (bool, str) and complex value objects for weights,
ranges, locations, and clinical coding.
"""

class Setting(CamelModel):
    """
    User configuration override for a specific field in cohort generation.
    
    Links a rule_id (from the use case's form_rules) to a user-provided value
    that overrides the default setting. The value type must match what the
    target field expects (e.g., ValueRange for age, ValueWeights for distributions).
    """
    rule_id: str = PyField(
        ...,
        description="Identifier matching a rule in the use case's form_rules that this setting targets."
    )
    value: ValueX = PyField(
        ...,
        description="The configured value for this setting. Type must match the field's expected value type."
    )

class Medication(CamelModel):
    """
    Single medication specification with coding and dosage information.
    
    Defines a medication to be prescribed in generated patient records, including
    its code (from standard terminologies like RxNorm) and optional dosage text.
    """
    codeable_concept: ValueCoding = PyField(
        ...,
        description="Coded medication identifier with system, code, and display (e.g., RxNorm code for the drug)."
    )
    dosage: Optional[str] = PyField(
        default=None,
        description="Human-readable dosage instruction text (e.g., 'Take 1 tablet daily')."
    )

class MedicationSet(CamelModel):
    """
    Weighted collection of medications for distribution across patients.
    
    Groups multiple medications together with a weight that determines how
    frequently this set is assigned to patients in the cohort. Higher weights
    mean more patients receive this combination of medications.
    
    Example:
        A weight of .9 for "Set A" and .1 for "Set B" means Set A is assigned
        to 90% of patients and Set B to 10%.
    """
    medications: list[Medication] = PyField(
        default=[],
        description="List of medications included in this set."
    )
    weight: int | float = PyField(
        ...,
        description="Relative frequency weight for assigning this set to patients. Higher values mean more frequent assignment."
    )

class EventPeriod(CamelModel):
    """
    Temporal boundaries for clinical event generation in the cohort.
    
    Defines the time range during which clinical events (observations, procedures,
    conditions, etc.) occur for patients. The 'until' date optionally extends
    generation beyond the event period for time-dependent data.
    
    Validation:
        - end must be after start
        - until (if provided) must be after end
    """
    start: date = PyField(
        ...,
        description="Beginning date of the clinical event period. Events are generated starting from this date."
    )
    end: date = PyField(
        ...,
        description="Final date of the main event period. Primary clinical events occur by this date."
    )
    until: Optional[date] = PyField(
        default=None,
        description="Extended boundary for time-dependent event generation (e.g., condition resolution dates). If omitted, defaults to 'end' date."
    )

    @model_validator(mode='after')
    def validate_dates(self) -> 'EventPeriod':
        if self.end <= self.start:
            raise ValueError("End date must be after start date")
        if self.until is not None and self.until <= self.end:
            raise ValueError("Until date must be after end date")
        return self

class EventSetTiming(CamelModel):
    """
    Temporal configuration for repeating clinical events.
    
    Controls when and how often event sets (lab panels, vital signs, procedures)
    repeat throughout the event period for a given patient. Supports one-time
    events or recurring patterns at specified intervals.
    """
    offset: int = PyField(
        ...,
        description="Days from patient event date when this event set first occurs."
    )
    repeat: bool = PyField(
        ...,
        description="Whether this event set repeats at intervals or occurs only once."
    )
    repeat_timing: Optional[int] = PyField(
        default=None,
        description="Days between repetitions if repeat is true (e.g., 30 for monthly labs)."
    )
    until: Optional[int] = PyField(
        default=None,
        description="Maximum days from start to continue repeating. If omitted, repeats until patient level data period end."
    )

class EventSetEntry(CamelModel):
    """
    Single clinical observation or procedure within an event set.
    
    Represents one component of a repeating clinical event (e.g., a single lab
    test within a panel, or a procedure). The type references a common entity
    template that defines the resource structure.
    """
    type: str = PyField(
        ...,
        description="Identifier referencing a common entity template that defines this entry's resource structure."
    )
    codeable_concept: ValueCoding = PyField(
        ...,
        description="Clinical code for this entry (e.g., LOINC code for a lab test, CPT code for a procedure)."
    )
    value: Optional[ValueX] = PyField(
        default=None,
        description="Optional value specification for observations (e.g., ValueRange for numeric results)."
    )

class EventSet(CamelModel):
    """
    Collection of related clinical events that repeat together.
    
    Groups multiple clinical entries (observations, procedures) that logically
    occur together at specified intervals. Optionally wraps entries in a
    DiagnosticReport resource for structured lab panels.
    
    Example:
        A "Complete Blood Count" event set with offset=0, repeat=true,
        repeat_timing=90 would generate CBC panels every 90 days throughout
        the event period, with each panel containing multiple lab results
        defined by the contents of the event set entries.
    """
    name: str = PyField(
        ...,
        description="Descriptive name for this event set (e.g., 'Annual Physical Lab Panel')."
    )
    timing: EventSetTiming = PyField(
        ...,
        description="When and how often this event set occurs during the event period."
    )
    entry: list[EventSetEntry] = PyField(
        ...,
        description="Clinical observations or procedures included in this event set."
    )
    include_diagnostic_report: Optional[bool] = PyField(
        default=False,
        description="Whether to wrap entries in a DiagnosticReport resource (typical for lab panels)."
    )
    diagnostic_report_concept: Optional[ValueCoding] = PyField(
        default=None,
        description="Code for the DiagnosticReport if include_diagnostic_report is true (e.g., LOINC code for panel type)."
    )

    @model_validator(mode='after')
    def validate_dr(self) -> 'EventSet':
        if self.include_diagnostic_report and self.diagnostic_report_concept is None:
            raise ValueError("If include_diagnostic_report is true, must include a diagnostic_report_concept.")
        return self

class OutputFormat(str, Enum):
    """
    Supported output formats for generated FHIR bundles.
    
    Determines how generated resources are structured in the output file.
    JSON produces a single Bundle resource, while NDJSON produces individual
    resources separated by newlines (useful for bulk data operations).
    """
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