"""
Patient metadata container for generation context.

This module defines PatientMeta, which holds patient-specific metadata that
informs field generation across all resources for a single patient. This includes
demographic information, temporal boundaries, and unique identifiers used
throughout the generation process.
"""

from datetime import date
from uuid import uuid4

class PatientMeta():
    """
    Metadata container for a single patient's generation context.
    
    Holds patient-specific information that influences field generation across
    all FHIR resources for that patient. This includes demographics (name, sex),
    temporal information (event date, generation boundaries), and unique identifiers.
    
    Used throughout the generation process to:
    - Generate gender-appropriate names and values
    - Calculate relative dates (birth date from age, procedure dates from event date)
    - Determine generation boundaries (don't generate events after generate_until_date)
    - Link resources with consistent patient references (via id)
    
    Attributes:
        id (str): UUID for this patient, used in resource references and entity IDs.
        event_date (date): Central date for this patient's clinical scenario. Other
            dates are calculated relative to this (e.g., birth date = event_date - age).
        name (str | None): Generated patient name (set after sex is determined).
        sex (str | None): Patient sex/gender ('male', 'female', or other configured values).
            Influences name generation and potentially other gender-dependent fields.
        generate_until_date (date | None): Latest date for which to generate events.
            Prevents generating data beyond clinical scenario boundaries (e.g., don't
            generate condition resolution dates beyond the cohort's temporal scope).
    
    Examples:
        Initialization during patient generation:
        ```
        patient_meta = PatientMeta(
            event_date=date(2024, 6, 15),
            name=None,  # Set later after sex determined
            sex=None    # Set from distribution
        )
        patient_meta.update_sex("male")
        patient_meta.update_name(generate_name("male"))
        patient_meta.set_until_date(date(2024, 12, 31))
        ```
        
        Using in field generation:
        ```
        # Generate birth date from age relative to event_date
        birth_date = patient_meta.event_date - timedelta(days=age_in_years * 365.25)
        
        # Generate gender-appropriate values
        if patient_meta.sex == "male":
            generate_male_specific_value()
        ```
    """
    def __init__(self, event_date: date, name: str | None, sex: str | None):
        """
        Initialize patient metadata container.
        
        Args:
            event_date: Central date for this patient's clinical scenario. Other
                dates (birth, procedures, observations) are calculated relative to this.
            name: Patient name, typically None initially and set after sex is determined.
            sex: Patient sex/gender, typically None initially and set from distribution.
        """
        self.id = str(uuid4())
        """UUID for this patient, used in resource references and unique entity IDs."""
        
        self.event_date = event_date
        """Central date for this patient's clinical scenario."""
        
        self.name = name
        """Generated patient name (set after sex determination)."""
        
        self.sex = sex
        """Patient sex/gender ('male', 'female', etc.)."""
        
        self.generate_until_date: date | None = None
        """Latest date for event generation. Prevents generating data beyond temporal boundaries."""
    
    def update_name(self, name: str):
        """
        Set the patient's generated name.
        
        Typically called after sex is determined to generate a gender-appropriate name.
        
        Args:
            name: The generated name to assign to this patient.
        """
        self.name = name
        
    def update_sex(self, sex: str):
        """
        Set the patient's sex/gender.
        
        Typically called when pulling from the sex/gender distribution. Influences
        name generation and potentially other gender-dependent field values.
        
        Args:
            sex: The sex/gender value (e.g., 'male', 'female').
        """
        self.sex = sex
    
    def set_until_date(self, until_date: date):
        """
        Set the latest date for generating events for this patient.
        
        Establishes a boundary to prevent generating events (like condition resolution
        dates) beyond the configured temporal scope. May be set from the cohort's
        event_period.until or from field-specific end dates.
        
        Args:
            until_date: The latest date to generate events for this patient.
        """
        self.generate_until_date = until_date