from enum import Enum
from typing import Dict

from api.models.value_types import ValueCoding

class SpecialValues(str, Enum):
    CURRENT = "$current"
    MASKED = "$masked"

class FhirResourceTypes(str, Enum):
    PATIENT = "Patient"

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

class PatientDistributionFields(str, Enum):
    GENDER = "Patient.gender"
    RACE = "Patient.extension[Race].ombCategory.value"
    ETHNICITY = "Patient.extension[Ethnicity].ombCategory.value"

class SpecialFields(str, Enum):
    BIRTH_DATE = "Patient.birthDate"

PATIENT_DIST_FIELDS_SET = frozenset(f.value for f in PatientDistributionFields)
SPECIAL_FIELDS_SET = frozenset(f.value for f in PatientDistributionFields) | frozenset(f.value for f in SpecialFields)

patient_dist_fields = [
                    "Patient.gender",
                    "Patient.extension[Race].ombCategory.value",
                    "Patient.extension[Ethnicity].ombCategory.value"]
special_fields = [*patient_dist_fields, "Patient.birthDate"] # Special Fields is a superset of Patient Dist Fields