from enum import Enum

from sqlalchemy.orm import Session
from api.features.generation.generators.occupation import generate_occupation
from api.models.cohort_settings import Setting, ValueX
from api.models.field import BooleanMap, ConceptMap, Field
from api.models.patient_meta import PatientMeta
from api.features.generation.constants import SpecialValues
from api.features.generation.generators.dates import append_days
from api.features.generation.generators.addresses import generate_address
from api.features.generation.generators.numbers import generate_number_from_range
from api.features.generation.weighted_values import select_from_weighted_list
from typing import Optional
from api.features.generation.alias_types import Code
import datetime # NOTE: Importing individual objects from datetime module breaks date type checking.
from api.models.value_types import ValueCoding, is_value_occupation
from api.models.value_types import  is_value_coding, is_value_time_range_as_days, is_value_location, is_value_range_with_units, is_value_weights, is_bool
from api.models.cohort_settings import EventSetEntry
from loguru import logger
from fastapi import HTTPException


'''
TODO: Refactor to following pattern seen in boolean and Coding:
# check if static value is none to see which method argument must be handled.
if static value is None
    if type of field setting value is what is expected/supported for the type in question, e.g. weights for strings/range for quantities/etc.
        do the generation
    if not
        raise error, not supported for fhir type error
if static value is not none
    if type of static value matches the fhir type directly (e.g., is a Coding object for Coding)
       return the static value, it's all good
    if it does not match
        raise error, this is not usable
'''

#TODO The parameters are out of order compared to the individual handlers, needs refactoring.
def handle_by_type(fhir_type: str, field: Field, patient_meta: PatientMeta, field_setting: Optional[Setting], mask_pii_enabled: bool = False, main_db: Session | None = None) -> str | bool | datetime.datetime | None:
    if field.user_configured and field_setting is None:
        raise ValueError("Field setting required for all user configurable values.")
    if field.user_configured:
        value = globals()[fhir_type](field_setting, patient_meta, None, boolean_maps = field.boolean_maps, concept_maps = field.concept_maps, mask_pii_enabled = mask_pii_enabled, main_db = main_db)
    else:
        value = globals()[fhir_type](field_setting, patient_meta, field.value, boolean_maps = field.boolean_maps, concept_maps = field.concept_maps, mask_pii_enabled = mask_pii_enabled, main_db = main_db)
    return value

def boolean(field_setting: Setting, patient_meta: PatientMeta, static_value: ValueX, boolean_maps: list[BooleanMap] | None, **kwargs) -> bool:
    if static_value is None:
        if is_value_weights(field_setting.value):
            if boolean_maps is None:
                raise ValueError(f"Boolean map not found. Weighted booleans require a boolean map to be set in the entity field.")
            else:
                value = select_from_weighted_list(field_setting.value)
                map_object = next((map_object for map_object in boolean_maps if map_object.value == value), None)
                if map_object is None:
                    raise ValueError(f"Value of {value} not found in boolean map: {boolean_maps}")
                return map_object.map_to
        else:
            raise TypeError(f"{type(field_setting.value)} not (yet?) supported for FHIR type of boolean, occurred when generating {field_setting.rule_id}.")
    elif is_bool(static_value):
        return static_value
    else:
        raise TypeError(f"Static value type is not none and does not match the expected FHIR type of boolean.")

def date(field_setting: Setting, patient_meta: PatientMeta, static_value: ValueX, **kwargs): # -> date:
    raise NotImplementedError("date type handler not implemented. Patient birth date handled specially.")

def dateTime(field_setting: Setting, patient_meta: PatientMeta, static_value: ValueX, **kwargs) -> datetime.datetime | None:
    if field_setting.value is None: #TODO This may need to be added everywhere to allow for non provided values?
        return None
    elif is_value_time_range_as_days(field_setting.value):
        if field_setting.value.start == 0 and field_setting.value.end == 0:
            return None
        else:
            value = append_days(patient_meta.event_date, field_setting.value)
            if type(value) is datetime.date:
                value = datetime.datetime.combine(value, datetime.time.min)
                return value
            elif type(value) is datetime.datetime:
                return value
            else:
                raise ValueError(f"Error processing date when generating {field_setting.rule_id}, type found was {type(value)}.")
    else:
        raise TypeError(f"{type(field_setting.value)} not (yet?) supported by dateTime when generating {field_setting.rule_id}.")

def instant(field_setting: Setting, patient_meta: PatientMeta, static_value: ValueX, **kwargs) -> datetime.datetime | None:
    return dateTime(field_setting, patient_meta, static_value)

def string(field_setting: Setting, patient_meta: PatientMeta, static_value: ValueX, **kwargs) -> str:
    if isinstance(static_value, str):
        return static_value
    return "ERROR - MAY NOT BE IMPLEMENTED"

def code(field_setting: Setting, patient_meta: PatientMeta, static_value: ValueX, **kwargs) ->  Code:
    return string(field_setting, patient_meta, static_value)

def Address(field_setting: Setting, patient_meta: PatientMeta, static_value: ValueX, mask_pii_enabled: bool = False, **kwargs):
    # line^city^county^postalcode^state^country
    if is_value_location(field_setting.value):
        address_string = generate_address(field_setting.value.city, field_setting.value.state, mask_pii_enabled)
        return address_string
    elif isinstance(field_setting.value, str) and field_setting.value.count("^") == 5:
        # if a string and looks like a valid complete address, just use it directly.
        return field_setting.value
        
    else:
        raise TypeError(f"{type(field_setting.value)} not (yet?) supported by Address when generating {field_setting.rule_id}.")

def Identifier(field_setting: Setting, patient_meta: PatientMeta, static_value: ValueX, **kwargs):
    raise NotImplementedError("Identifier type handler not implemented. Randomized identifiers should be handled through the $uuid special value for now.")

def HumanName(field_setting: Setting, meta: PatientMeta, static_value: ValueX, **kwargs):
    '''
    Processes generation behavior for the FHIR HumanName type. For patient generation where names are always randomized, the expected value is a bool to
    indicate whether or not masking should occur. For static, non-user configured data, this will accept any string in the form of "GivenName FamilyName"
    (e.g., "John Smith") which is bounced back as the value.
    '''
    return meta.name
 
# In FHIR Sheets, CodeableConcept is only handled as a single Coding value. The FHIR typing is retained for entity building, so the handler just passes to Coding.
def CodeableConcept(field_setting: Setting, patient_meta: PatientMeta, static_value: ValueCoding | None, concept_maps: list[ConceptMap] | None, main_db: Session | None = None, **kwargs):
    return Coding(field_setting, patient_meta, static_value, concept_maps, main_db=main_db)

def Coding(field_setting: Setting, patient_meta: PatientMeta, static_value: ValueCoding | None, concept_maps: list[ConceptMap] | None, main_db: Session | None = None, **kwargs):
    if static_value is None:
        if is_value_weights(field_setting.value):
            if concept_maps is None:
                raise ValueError(f"Concept map not found. Weighted concepts require a concept map to be set in the entity field.")
            else:
                value = select_from_weighted_list(field_setting.value)
                map_object = next((map_object for map_object in concept_maps if map_object.value == value), None)
                if map_object is None:
                    raise ValueError(f"Value of {value} not found in concept map: {concept_maps}")
                return value_coding_to_string(map_object.map_to)
        elif is_value_coding(field_setting.value):
            return value_coding_to_string(field_setting.value)
        elif is_value_occupation(field_setting.value):
            if main_db is None:
                raise TypeError(f"{type(field_setting.value)} cannot be used outside of a flow where database is not accessible. Please contact maintainers.")
            else:
                return generate_occupation(field_setting.value, main_db)

        else:
            raise TypeError(f"{type(field_setting.value)} not (yet?) supported for FHIR type of Coding/CodeableConcept, occurred when generating {field_setting.rule_id}.")
    elif is_value_coding(static_value):
        return value_coding_to_string(static_value)
    elif is_value_occupation(static_value):
        if main_db is None:
            raise TypeError(f"{type(static_value)} cannot be used outside of a flow where database is not accessible. Please contact maintainers.")
        else:
            return generate_occupation(static_value, main_db)
    else:
        raise TypeError(f"Expected ValueCoding for types Coding or CodeableConcept for static values - {field_setting}")

def value_coding_to_string(value: ValueCoding) -> str:
    '''
    Convert a ValueCoding object to a FHIR Sheets carat delimited string.
    '''
    return f"{value.system or ''}^{value.code or ''}^{value.display or ''}"

def Quantity(field_setting: Setting, patient_meta: PatientMeta, static_value: dict, **kwargs):
    raise NotImplementedError("Quantity type handler not implemented. Quantity is only supported through the choice of data type handler for observations for now.")

# Currently Supported Choice of DataTypes
class ChoiceOfDataTypes(Enum):
    QUANTITY = "Quantity"
    STRING = "string"

# TODO: Generalize the handling to the type handlers above.
def process_choice_of_data_type_value(entry: EventSetEntry, field: Field):
    '''
    Process FHIR style choice of data type values ("value[x]" fields)
    '''
    # Check if in the Choice of Data Types ENUM to see if handled...
    if field.type in (t.value for t in ChoiceOfDataTypes):

        # Handle by Choice of Data Type and do a check to see if types align with the generator values provided...
        if field.type == ChoiceOfDataTypes.QUANTITY.value and is_value_range_with_units(entry.value):
            value = generate_number_from_range(float(entry.value.min), float(entry.value.max))
            return f"{value}^{entry.value.unit}"
        elif field.type == ChoiceOfDataTypes.STRING.value and is_value_weights(entry.value):
            value = select_from_weighted_list(entry.value)
            return value
        else:
            pass
    else:
        message = f"Unable to process user settings. Choice of data type with type of \"{field.type}\" is not (currently) supported."
        logger.error(message)
        raise HTTPException(status_code=500, detail=message)


def fhir_type_match_check(obj: ValueX, fhir_type: str) -> bool:
    '''
    Simple bool to check type alignment between FHIR and generation settings throughout app.
      ValueWeights supports: string
      ValueRangeWithUnits supports: Quantity
    '''
    if is_value_weights(obj) and fhir_type == ChoiceOfDataTypes.STRING.value:
        return True
    elif is_value_range_with_units(obj) and fhir_type == ChoiceOfDataTypes.QUANTITY.value:
        return True
    else:
        return False