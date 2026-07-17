"""
Field definition models for FHIR resource generation.

This module defines how individual fields within FHIR resources are configured,
including their types, values, validation rules, and special handling for
extensions, mappings, and PII masking.
"""

from fastapi_camelcase import CamelModel
from pydantic import model_validator, Field as PyField
from typing import Optional
from api.models.value_types import ValueCoding, ValueOccupation
from api.features.generation.special_extension_handlers import SpecialExtensions

class BooleanMap(CamelModel):
    """
    Mapping from weighted string values to boolean outcomes.
    
    Used when a field accepts weighted string options that map to boolean
    values (e.g., "smoker": true, "non-smoker": false). The generation
    process selects a weighted value and this map determines the actual
    boolean to use in the FHIR resource.
    """
    value: str = PyField(
        ...,
        description="The string value from weighted distribution that triggers this mapping."
    )
    map_to: bool = PyField(
        ...,
        description="The boolean value to use in the FHIR resource when this value is selected."
    )

class ConceptMap(CamelModel):
    """
    Mapping from weighted string values to coded concepts.
    
    Enables selection from user-friendly string options that map to proper
    FHIR coding (system, code, display).

    Example (in JSON camel case):
    {
        "value": "Employed",
        "mapTo": {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationValue",
            "code": "Employed",
            "display": "Employed"
        }
    },
    """
    value: str = PyField(
        ...,
        description="The string value from weighted distribution that triggers this mapping."
    )
    map_to: ValueCoding = PyField(
        ...,
        description="The coded concept (system/code/display) to use when this value is selected."
    )

class ExtensionDetails(CamelModel):
    """
    Configuration for FHIR extension fields.
    
    Defines how to generate FHIR extensions, which extend the base FHIR
    specification with additional data elements. Supports both simple
    value extensions and complex nested extensions with sub-extensions.
    
    Attributes:
        value_type: The type of value for this extension (e.g., 'Coding',
            'string', 'Complex' for nested extensions).
        extension_uri: The canonical URL identifying this extension.
        sub_extensions: For complex extensions, the nested extension definitions.
        special_handler: Optional enum indicating this extension requires
            custom generation logic (e.g., tribal affiliation).
    """
    value_type: str = PyField(
        ...,
        description="Type of value this extension holds ('Coding', 'string', 'Complex', etc.)."
    )
    extension_uri: str = PyField(
        ...,
        description="Canonical URI identifying this extension (e.g., 'http://hl7.org/fhir/us/core/...')."
    )
    sub_extensions: Optional[list['ExtensionDetails']] = PyField(
        default=None,
        description="Nested extensions for complex extension types. Each sub-extension is itself an ExtensionDetails."
    )
    special_handler: Optional[SpecialExtensions] = PyField(
        default=None,
        description="Indicates this extension requires custom generation logic (e.g., TRIBAL_AFFILIATION)."
    )

    # TODO: If value_type is complex, must have sub extensions.

ExtensionDetails.model_rebuild()

class Field(CamelModel):
    """
    Definition of a single field within a FHIR resource entity.
    
    Represents one data element (e.g., Patient.gender, Observation.value[x]) and
    how to generate or configure it. Fields can be user-configurable (with
    rules for UI controls) or have static/computed values.
    
    Validation:
        - Non-user-configured fields must have a value
        - Value type must match field type (boolean, Coding, string, etc.) or
          a defined parsable type
        - Coding/CodeableConcept fields accept ValueCoding objects or
          caret-delimited strings (system^code^display)
        - Special values starting with $ (e.g., $UUID) bypass type validation.
    
    (See maintainer guide for more information.)
    
    Attributes:
        path: FHIR path to this field (e.g., 'Patient.gender', 'Observation.valueQuantity.value').
        type: FHIR data type (e.g., 'code', 'Coding', 'CodeableConcept', 'Quantity').
        user_configured: Whether users can configure this field's value through the UI.
        user_setting_rule_id: If user_configured, the ID of the form rule controlling this field.
        value: Static value, special function ($UUID, $eventDate), or coded concept for this field.
        boolean_maps: For boolean fields, mappings from weighted strings to boolean values.
        concept_maps: For coded fields, mappings from weighted strings to coded concepts.
        extension_details: If this field is an Extension type, its configuration details.
        pii: Whether this field contains personally identifiable information (triggers masking).
    
    Examples:
        User-configured field:
        ```
        Field(
            path="Patient.gender",
            type="code",
            user_configured=True,
            user_setting_rule_id="patient-gender",
            value=None
        )
        ```
        
        Static coded field:
        ```
        Field(
            path="Observation.code",
            type="CodeableConcept",
            user_configured=False,
            value="http://loinc.org^8310-5^Body temperature"
        )
        ```
        
        Special function field:
        ```
        Field(
            path="Patient.id",
            type="id",
            user_configured=False,
            value="$UUID"
        )
        ```
    """
    path: str = PyField(
        ...,
        description="FHIR path to this field within the resource (e.g., 'Patient.birthDate', 'Observation.valueQuantity.value')."
    )
    type: str = PyField(
        ...,
        description="FHIR data type for this field (e.g., 'code', 'Coding', 'CodeableConcept', 'Quantity', 'dateTime')."
    )
    user_configured: bool = PyField(
        ...,
        description="Whether this field's value can be configured by users through the UI."
    )
    user_setting_rule_id: Optional[str] = PyField(
        default=None,
        description="If user_configured, the rule ID that controls this field's configuration options."
    )
    value: Optional[str | bool | ValueCoding | ValueOccupation] = PyField(
        default=None,
        description="Static value, special function ($UUID, $eventDate, $currentDate), or coded concept. Required if not user_configured."
    )
    boolean_maps: Optional[list[BooleanMap]] = PyField(
        default=None,
        description="For boolean fields with weighted options, maps string values to boolean outcomes."
    )
    concept_maps: Optional[list[ConceptMap]] = PyField(
        default=None,
        description="For coded fields with weighted options, maps string values to coded concepts."
    )
    extension_details: Optional[ExtensionDetails] = PyField(
        default=None,
        description="Configuration details if this field is a FHIR extension."
    )
    pii: Optional[bool] = PyField(
        default=False,
        description="Whether this field contains simulated PII that should be masked in outputs when masking is enabled."
    )

    @model_validator(mode='after')
    def check_value_exists(self) -> 'Field':
        """Ensure non-user-configured fields have a value."""
        if not self.user_configured and self.value is None:
            raise ValueError("If field is not configurable by user a static value or special function must be provided.")
        return self

    @model_validator(mode='after')
    def validate_value_type(self) -> 'Field':
        """Validate that field value type matches the declared FHIR type."""
        if self.value is None:
            return self  # Skip validation if no value
        
        # Allow special values (start with $) for any type
        if isinstance(self.value, str) and self.value.startswith('$'):
            return self
            
        if self.type == "boolean":
            if not isinstance(self.value, bool):
                raise ValueError(f"Field type 'boolean' requires bool value, got {type(self.value).__name__}")
        elif self.type in ["CodeableConcept", "Coding"]:
            # Allow ValueCoding object OR caret-delimited string
            if isinstance(self.value, ValueCoding):
                pass  # Valid
            elif isinstance(self.value, ValueOccupation):
                pass # Valid
            elif isinstance(self.value, str):
                # Validate caret-delimited format: "system^code^display"
                if '^' not in self.value:
                    raise ValueError(f"CodeableConcept/Coding string must be caret-delimited format 'system^code^display', got: {self.value}")
            else:
                raise ValueError(f"Field type '{self.type}' requires ValueCoding or caret-delimited string, got {type(self.value).__name__}")

        else:
            # All other types should be strings
            if not isinstance(self.value, str):
                raise ValueError(f"Field type '{self.type}' requires str value, got {type(self.value).__name__}")
        return self