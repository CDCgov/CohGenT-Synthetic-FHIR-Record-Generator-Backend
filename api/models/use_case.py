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

from pydantic import Field, model_validator
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
    """
    Maps a dynamic reference link to a provider entity.
    
    Dynamic references allow common entities to reference provider resources
    (Practitioner, PractitionerRole, Organization) without hardcoding which
    specific provider entity to use. The use case specifies the mapping from
    linkIdentifier (defined in the common entity) to targetEntityIdentifier
    (the actual provider entity to use).
    
    This enables:
      - Same entity template used with different providers across use cases
      - Automatic reference chain resolution (PractitionerRole -> Practitioner + Organization)
    
    Example:
        Common entity has: {"linkIdentifier": "performer"}
        Use case maps to: {"linkIdentifier": "performer", 
                          "targetEntityIdentifier": "USCorePractitionerRole002"}
        Result: performer reference points to Lab Technician Role + related resources
    """
    link_identifier: str = Field(description=(
            "Link identifier matching a dynamic reference in the common entity. "
            "Must match the link_identifier in the entity's dynamicReferences array."
        )
    )
    target_entity_identifier: str = Field(description=(
            "Entity ID of the provider resource to link to "
            "(e.g., 'USCorePractitionerRole002'). Must exist in provider cache."
        )
    )


class AdditionalEntity(CamelModel):
    """
    Reference to a reusable clinical data entity.
    
    Additional entities are templates for repeating clinical observations,
    procedures, or other resources that can be generated multiple times per
    patient through EventSets. They link to entity files in commonentities/
    and support dynamic references to provider resources.
    
    Example: Lab observation template that can be used for CBC, CMP, etc.
    """
    entity_id: str = Field(description="Unique identifier for this entity reference within the use case")
    type: str = Field(description=(
            "Type identifier matching a common entity type "
            "(e.g., 'observation', 'procedure'). Used to match EventSet entries "
            "to entity templates."
        )
    )
    button_label: str = Field(description="Display label for this entity in the UI")
    entity_file: str = Field(description=(
            "Identifier for the entity definition in api/assets/commonentities/ "
            "(without .json/json5 extension, e.g., 'USCoreObservationLab')"
        )
    )
    default_system: Optional[str] = Field(None,
        description=(
            "Default code system URI for this entity type "
            "(e.g., 'http://loinc.org' for lab observations)"
        )
    )
    dynamic_references: Optional[list[DynamicReferencePointer]] = Field(None,
        description=(
            "Dynamic reference mappings to provider entities. Links entity fields "
            "to provider resources (Practitioner, Organization) by link_identifier."
        )
    )


class MedicationEntity(CamelModel):
    """
    Configuration for medication generation.
    
    References the medication entity template and provider resource mappings
    for generating MedicationRequest resources.
    """
    entity_file: str = Field(description=(
            "Identifier for the entity definition in api/assets/commonentities/ "
            "(e.g., 'USCoreMedicationRequest')"
        )
    )
    dynamic_references: Optional[list[DynamicReferencePointer]] = Field(None,
        description="Dynamic reference mappings to provider entities (e.g., prescriber, pharmacy)"
    )

class CommonEntities(CamelModel):
    """
    References to reusable entity templates.
    
    Common entities are entity definitions stored in separate files
    (api/assets/commonentities/) that can be reused across multiple use cases.
    These typically represent repeating clinical data like lab results,
    procedures, or medications.
    
    Unlike core entities (defined directly in the use case), common entities:
      - Live in separate files for reusability
      - Can be generated multiple times per patient (via EventSets)
      - Support dynamic references to provider resources
    """
    additional_entities: Optional[list[AdditionalEntity]] = Field(None,
        description=(
            "List of reusable clinical data entities (labs, procedures, imaging). "
            "Referenced by EventSet entries to generate repeating observations."
        )
    )
    medication: Optional[MedicationEntity] = Field(None,
        description="Medication entity configuration for MedicationRequest generation"
    )
    diagnostic_report: Optional[str] = Field(None,
        description=(
            "Filename of DiagnosticReport entity template in commonentities/ "
            "(e.g., 'USCoreDiagnosticReportLab'). Used as container for lab panels."
        )
    )

class GenerationRules(CamelModel):
    """
    Rules for controlling generation behavior.
    
    Defines fields that have special meaning during generation, particularly
    for temporal boundaries and date relationships.
    """
    event_date: str = Field(
        description=(
            "Entity field path that represents the primary event date "
            "(e.g., 'PrimaryEncounter/Encounter.period.start'). This field is used "
            "as the reference point for all relative date calculations."
        )
    )
    end_date: Optional[str] = Field(None,
        description=(
            "Entity field path representing the end boundary for generation "
            "(e.g., 'PrimaryCondition/Condition.abatementDateTime'). If this date "
            "is earlier than the cohort-wide end date, it takes precedence for "
            "this patient's record generation."
        )
    )

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
    us_core_version: Optional[str] = Field(None, description="US Core Implementation Guide version if applicable (e.g., '6.1.0')")
    description: str = Field(description="Detailed description of what this use case generates")
    generation_rules: Optional[GenerationRules] = Field(None, description="Special rules for generation timing and boundaries.")
    form_rules: Optional[list[FormRule]] = Field(None, description="UI form configuration specifying user input controls. Should only be empty if use case has no customization.")
    entities: Optional[list[Entity]] = Field(None, description="Core FHIR resource entity definitions (Patient, Condition, Encounter, etc.)")
    common_entities: Optional[CommonEntities] = Field(None, description="References to reusable entity templates for labs, medications, etc. and their configuration options")