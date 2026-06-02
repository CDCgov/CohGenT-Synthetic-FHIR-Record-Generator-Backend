from enum import Enum
from typing import Dict

from api.models.value_types import ValueCoding

class SpecialTypeFunctions(str, Enum):
    UUID = "$uuid"
    EVENT_DATE = "$eventDate"
    CONDITION_CLINICAL_STATUS = "$conditionClinicalStatus"
    PATIENT_CONTACT_POINT = "$patientContactPoint"

# Type Enums
class FhirType(str, Enum):
    IDENTIFIER = "Identifier"
    CONTACT_POINT = "ContactPoint"
    EXTENSION = "Extension"

identifier_system: str = "urn:cohgent:identifier"

class ConditionClinicalStatusValues(str, Enum):
    ACTIVE = "http://terminology.hl7.org/CodeSystem/condition-clinical^active^Active"
    RESOLVED = "http://terminology.hl7.org/CodeSystem/condition-clinical^resolved^Resolved"