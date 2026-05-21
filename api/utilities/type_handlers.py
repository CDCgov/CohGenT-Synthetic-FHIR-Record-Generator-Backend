from enum import Enum
from api.models.cohort_settings import Setting, ValueX
from api.models.field import BooleanMap, Field
from api.models.patient_meta import PatientMeta
from api.features.generation.generators.names import generate_name
from api.features.generation.generators.dates import append_days
from api.features.generation.generators.addresses import generate_address
from api.features.generation.generators.numbers import generate_number_from_range
from api.utilities.weighted_values import select_from_weighted_list
from typing import Optional, TypeGuard
import datetime # NOTE: Importing individual objects from datetime module breaks date type checking.
from api.models.value_types import ValueCoding
from api.models.value_types import  is_value_coding, is_value_time_range_as_days, is_value_location, is_value_range_with_units, is_value_weights, is_value_coding
from api.models.cohort_settings import EventSetEntry
from loguru import logger
from fastapi import HTTPException

type Code = str

'''
TODO: Refactor to following pattern seen in boolean:
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
def handle_by_type(field: Field, patient_meta: PatientMeta, field_setting: Optional[Setting]) -> str | bool | datetime.datetime | None:
    if field.user_configured and field_setting is None:
        raise ValueError("Field setting required for all user configurable values.")
    if field.user_configured:
        value = globals()[field.type](field_setting, patient_meta, None, boolean_maps = field.boolean_map)
    else:
        value = globals()[field.type](field_setting, patient_meta, field.value, boolean_map = field.boolean_map)
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
    return "ERROR - MAY NOT IMPLEMENTED"

def code(field_setting: Setting, patient_meta: PatientMeta, static_value: ValueX, **kwargs) ->  Code:
    return string(field_setting, patient_meta, static_value)

def Address(field_setting: Setting, patient_meta: PatientMeta, static_value: ValueX, **kwargs):
    # line^city^county^postalcode^state^country
    if is_value_location(field_setting.value):
        address_string = generate_address(field_setting.value.city, field_setting.value.state)

        return address_string
    else:
        raise TypeError(f"{type(field_setting.value)} not (yet?) supported by Address when generating {field_setting.rule_id}.")

def Identifier(field_setting: Setting, patient_meta: PatientMeta, static_value: ValueX, **kwargs):
    raise NotImplementedError("Identifier type handler not implemented. Randomized identifiers should be handled through the $uuid special value for now.")

# Note: This handles whether or not names should be masked. There is never a reason to process the HumanName type itself, nor static values.
def HumanName(field_setting: Setting, meta: PatientMeta, static_value: ValueX, **kwargs):
    if is_bool(field_setting.value):
        if field_setting.value:
            return "$masked"
        else:
            return meta.name
    else:
        raise ValueError(f"Expected bool for type HumanName to determine data masking - {field_setting}.")

# In FHIR Sheets, CodeableConcept is only handled as a single Coding value. The FHIR typing is retained for entity building, so the handler just passes to Coding.
def CodeableConcept(field_setting: Setting, patient_meta: PatientMeta, static_value: ValueCoding, **kwargs):
    return Coding(field_setting, patient_meta, static_value)

def Coding(field_setting: Setting, patient_meta: PatientMeta, static_value: ValueCoding, **kwargs):
    if is_value_coding(static_value):
        system = static_value.system if static_value.system is not None else ''
        code = static_value.code if static_value.code is not None else ''
        display = static_value.display if static_value.display is not None else ''
        return f"{static_value.system}^{static_value.code}^{static_value.display}"
    elif is_value_coding(field_setting.value):
        system = field_setting.value.system if field_setting.value.system is not None else ''
        code = field_setting.value.code if field_setting.value.code is not None else ''
        display = field_setting.value.display if field_setting.value.display is not None else ''
        return f"{system}^{code}^{display}"
    else:
        raise TypeError(f"Expected ValueCodeableConcept for type Codeable Concept - {field_setting}")



def is_bool(value: object) -> TypeGuard[bool]:
    return isinstance(value, bool)

def Quantity(field_setting: Setting, patient_meta: PatientMeta, static_value: dict, **kwargs):
    raise NotImplementedError("Quantity type handler not implemented. Quantity is only supported through the choice of data type handler for observations for now.")


class ChoiceOfDataTypes(Enum):
    QUANTITY = "Quantity"
    STRING = "string"

# TODO: Generalize the handling to the type handlers above.
def process_choice_of_data_type_value(entry: EventSetEntry, field: Field):
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