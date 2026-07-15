"""
UI form control configuration models for use case field configuration.

This module defines how user-configurable fields are presented and controlled
in the UI, including control types (checkboxes, ranges, weighting sliders) and
their default values.
"""

from fastapi_camelcase import CamelModel
from typing import Optional
from pydantic import model_validator, Field as PyField
from api.models.value_types import ValueOccupation, ValuePrevalence, ValueWeights, ValueTimeRangeAsDays
from enum import Enum

class ControlType(str, Enum):
    """
    Supported UI control types for field configuration.
    
    Each control type determines how users interact with a field setting
    in the UI and what value types are valid.
    
    Values:
        CHECKBOX: Binary on/off toggle for boolean fields.
        RANGE: Numeric range input with min/max bounds (e.g., age 20-65).
        WEIGHTING: Distribution slider for weighted value selection
            (e.g., 40% male, 60% female).
        LOCATION: Geographic location selector (state, city).
        RELATIVE_TIME_RANGE: Time range relative to event date in days
            (e.g., condition onset 30-90 days before event).
        TRIBAL_AFFILIATION: Tribal affiliation selector with prevalence.
        PREVALENCE: Prevalence-based control for optional features.
        CONCEPT: Clinical concept/terminology selector (codes, diagnoses).
        OCCUPATION: Occupation code selector from standard occupation database.
    """
    CHECKBOX = "checkbox"
    RANGE = "range"
    WEIGHTING = "weighting"
    LOCATION = "location"
    RELATIVE_TIME_RANGE = "relative-time-range"
    TRIBAL_AFFILIATION = "tribal-affiliation"
    PREVALENCE = "prevalence"
    CONCEPT = "concept"
    OCCUPATION = "occupation"

class Option(CamelModel):
    """
    UI form control configuration for a user-configurable field.
    
    Defines how a field appears and behaves in the UI, including
    the control type, labels, tooltips, and default values. Maps to a specific
    field via rule_id which links to Field.user_setting_rule_id.
    
    Different control types use different subsets of attributes:
    - CHECKBOX: default_state
    - RANGE: default_values (list[int]), decimal_spaces_allowed, min_max
    - WEIGHTING: values (list[str]), default_values (ValueWeights)
    - RELATIVE_TIME_RANGE: default_values (ValueTimeRangeAsDays)
    - TRIBAL_AFFILIATION: default_values (ValuePrevalence with affiliation_code)
    - OCCUPATION: default_values (ValueOccupation)
    
    Validation:
        - Control-specific required fields are validated
        - TODO: Enhanced validation for range bounds, weighting length matching
    
    Attributes:
        rule_id: Unique identifier linking this option to a Field's user_setting_rule_id.
        label: Display label shown in the UI for this control.
        description: Optional longer description explaining what this field controls.
        tooltip: Optional hover tooltip text for additional guidance.
        tags: Optional tags for categorization/filtering in the UI.
        control: Type of UI control to render for this field.
        default_state: For CHECKBOX controls, the initial on/off state.
        default_values: Default value(s) appropriate for the control type
            (range bounds, weights, time ranges, etc.).
        decimal_spaces_allowed: For RANGE controls, whether decimal values are permitted.
        min_max: For RANGE controls, the absolute minimum and maximum allowed values.
        values: For WEIGHTING controls, the list of string options to weight.
    
    Examples:
        Checkbox control:
        ```
        Option(
            rule_id="include-smoker",
            label="Include smoking status",
            control=ControlType.CHECKBOX,
            default_state=True
        )
        ```
        
        Range control:
        ```
        Option(
            rule_id="patient-age",
            label="Patient age range",
            control=ControlType.RANGE,
            default_values=[20, 65],
            decimal_spaces_allowed=False,
            min_max=(0, 120)
        )
        ```
        
        Weighting control:
        ```
        Option(
            rule_id="patient-gender",
            label="Gender distribution",
            control=ControlType.WEIGHTING,
            values=["male", "female"],
            default_values={"male": 0.5, "female": 0.5}
        )
        ```
    """
    rule_id: str = PyField(
        ...,
        description="Unique identifier linking this option to a Field's user_setting_rule_id."
    )
    label: str = PyField(
        ...,
        description="Display label for this control in the configuration UI."
    )
    description: Optional[str] = PyField(
        default=None,
        description="Optional detailed description explaining what this field controls."
    )
    tooltip: Optional[str] = PyField(
        default=None,
        description="Optional tooltip text shown on hover for additional guidance."
    )
    tags: Optional[list[str]] = PyField(
        default=None,
        description="Optional tags for categorizing/filtering this option in the UI."
    )
    control: ControlType = PyField(
        ...,
        description="Type of UI control to render (checkbox, range, weighting, etc.)."
    )

    # Checkbox control attributes
    default_state: Optional[bool] = PyField(
        default=None,
        description="For CHECKBOX controls, the initial checked/unchecked state."
    )

    # Range, weighting, and other control attributes
    default_values: Optional[ValueWeights | ValueTimeRangeAsDays | ValuePrevalence | ValueOccupation | list[int]] = PyField(
        default=None,
        description="Default value(s) for this control. Type depends on control type: list[int] for RANGE, ValueWeights for WEIGHTING, etc."
    )
    decimal_spaces_allowed: Optional[bool] = PyField(
        default=None,
        description="For RANGE controls, whether decimal values are permitted."
    )
    min_max: Optional[tuple[int|float, int|float]] = PyField(
        default=None,
        description="For RANGE controls, the absolute (minimum, maximum) bounds allowed."
    )

    # Weighting control attributes
    values: Optional[list[str]] = PyField(
        default=None,
        description="For WEIGHTING controls, the list of string options to assign weights to."
    )
    # default_values reused here for the actual weights

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