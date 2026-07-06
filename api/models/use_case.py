"""
Use case scenario definition models.

This module defines the structure of use case scenarios, which are JSON/JSON5 files
that configure how CohGenT generates synthetic FHIR records. A use case scenario
specifies:
  - Which FHIR resources to generate (entities)
  - How the UI should present configuration options (form rules)
  - Which reusable entities can be added (common entities)
  - Special generation rules (temporal boundaries, etc.)

Use case scenarios drive both the frontend form rendering and backend generation logic.

Model Hierarchy:
    UseCase (root)
    ├── Entity[] - Core FHIR resource templates
    ├── FormRule[] - UI form configuration
    ├── CommonEntities - References to reusable entities
    │   ├── AdditionalEntity[] - Repeatable clinical data (labs, procedures)
    │   ├── MedicationEntity - Medication generation config
    │   └── diagnostic_report - DiagnosticReport profile reference
    └── GenerationRules - Temporal and logical constraints

See Also:
    - api/models/entity.py for Entity structure
    - api/models/option.py for Option/control types
    - api/utilities/file_reader.py for use case loading
"""

from enum import Enum

from fastapi_camelcase import CamelModel
from typing import Literal, Optional

from pydantic import Field
from api.models.entity import Entity
from api.models.option import Option

class FormRuleType(str, Enum):
    """
    Types of form rule steps in use case scenarios.
    
    Each type determines how the UI renders the configuration step and what
    kind of data it collects from the user.

    NOTE: This should be expanded as more types are implmented for the UI
    for future use case scenarios.
    """
    CUSTOM = "custom"
    """Custom form step with user-defined options/controls."""
    ADDITIONAL_DATA_TIME_SERIES = "additional-data-time-series"
    """Step for configuring repeating clinical data (EventSets) over time."""
    MEDICATION = "medication"
    """Step for configuring medication generation (MedicationSets)."""

##

class FormRule(CamelModel):
    """
    Defines a step in the UI configuration form.
    
    Form rules specify how the UI should render configuration options for the user.
    Each rule represents a form step/section with controls (checkboxes, sliders,
    date pickers, etc.) that collect user input for generation parameters.
    
    The collected values are returned as Settings in CohortSettings.userResponses,
    which then drive field generation during cohort creation.
    """
    step_order: int = Field(description="Display order for this form step (1-indexed)")
    type: FormRuleType = Field(description="Form step type determining UI rendering behavior")
    title: str = Field(description="Step title displayed in UI")
    description: str = Field(description="Explanatory text for this form step")
    options: Optional[list[Option]] = Field(None, description="List of form controls/options for user input (see Option model)")

class DynamicReferencePointer(CamelModel):
    link_identifier: str
    target_entity_identifier: str

class AdditionalEntity(CamelModel):
    entity_id: str
    type: str
    button_label: str
    entity_file: str
    default_system: Optional[str] = None
    dynamic_references: Optional[list[DynamicReferencePointer]] = None

class MedicationEntity(CamelModel):
    entity_file: str
    dynamic_references: Optional[list[DynamicReferencePointer]] = None

class CommonEntities(CamelModel):
    additional_entities: Optional[list[AdditionalEntity]] = None
    medication: Optional[MedicationEntity] = None
    diagnostic_report: Optional[str] = None

class GenerationRules(CamelModel):
    event_date: str
    end_date: Optional[str] = None

class UseCase(CamelModel):
    """
    Root model representing a complete use case scenario.
    
    A use case scenario is a JSON configuration file that defines everything needed
    to generate a cohort of synthetic FHIR records for a specific clinical scenario
    (e.g., "condition-based-record", "observation-based-record").
    
    The model includes:
      - Metadata (ID, version, title)
      - Entity definitions (FHIR resources to generate)
      - Form rules (UI configuration for user input)
      - Common entities (reusable templates for labs, medications, etc.)
      - Generation rules (temporal and logical constraints)
    
    Example file location:
        api/assets/usecasetemplates/condition-based-record_R4_core610.json5
    """
    use_case_id: str = Field(description="Unique identifier for this use case (e.g., 'condition-based-record')")
    use_case_version: str = Field(description="Version string for this use case configuration")
    title: str = Field(description="Human-readable title displayed in UI")
    fhir_version: Literal["R4", "R5"] = Field(description="FHIR standard version this use case targets")
    us_core_version: Optional[str] = Field(default=None, description="US Core Implementation Guide version if applicable (e.g., '6.1.0')")
    description: str = Field(description="Detailed description of what this use case generates")
    generation_rules: Optional[GenerationRules] = Field(default=None, description="Special rules for generation timing and boundaries. Warning: Experimental, not fully implemented.")
    form_rules: Optional[list[FormRule]] = Field(default=None, description="UI form configuration specifying user input controls. Should only be empty if use case has no customization.")
    entities: Optional[list[Entity]] = Field(default=None, description="Core FHIR resource entity definitions (Patient, Condition, Encounter, etc.)")
    common_entities: Optional[CommonEntities] = Field(default=None, description="References to reusable entity templates for labs, medications, etc. and their configuration options")