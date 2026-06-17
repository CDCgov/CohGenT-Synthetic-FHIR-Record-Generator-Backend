from datetime import datetime

from faker import Faker
from fastapi import HTTPException
from sqlalchemy.orm import Session
from loguru import logger

from api.features.generation.alias_types import Distributions, PatientRow
import api.features.generation.constants as C
from api.features.generation.generators.dates import calculate_birth_date, generate_age_at_event_date
from api.features.generation.generators.email import generate_email
from api.features.generation.generators.names import generate_name
from api.features.generation.generators.uuids import generate_uuid_identifier
from api.features.generation.setting_handler import find_setting
from api.features.generation.special_extension_handlers import SpecialExtensions, generate_tribal_affiliation
from api.features.generation.type_handlers import handle_by_type, value_coding_to_string
from api.models.cohort_settings import CohortSettings, Setting
from api.models.entity import Entity
from api.models.patient_meta import PatientMeta
from api.models.use_case import UseCase
from api.models.value_types import is_value_coding, is_value_range

fake = Faker()

def process_entity(entity: Entity, patient_meta: PatientMeta, patient_row_as_dict: PatientRow, use_case: UseCase, distributions: Distributions, configuration: CohortSettings, default_settings: list[Setting], main_db: Session):
    if entity.resource_type == C.FhirResourceTypes.PATIENT.value:
        # TODO: Add handling to skip if not in record. require?
        assert(entity.fields is not None)                
        
        for patient_dist_field in C.PATIENT_DIST_FIELDS_SET:                    
            # Grab a value from the distributions.
            if patient_dist_field in distributions:
                dist_field_value = distributions[patient_dist_field].pop()
                patient_row_as_dict[(entity.entity_id), f"{entity.entity_id}/{patient_dist_field}"] = dist_field_value.lower()
                if patient_dist_field == C.PatientDistributionFields.GENDER.value:
                    patient_meta.update_sex(dist_field_value.lower())
        
        # Set Patient Name based on Sex/Gender.
        patient_meta.update_name(generate_name(patient_meta.sex))


        # Set Patient Age/BirthDate based on Event Date.
        patient_age_field = next((field for field in entity.fields if field.path == C.SpecialFields.BIRTH_DATE.value), None)
        if patient_age_field is not None: 
            patient_age_field_setting: Setting | None = find_setting(patient_age_field, configuration.user_responses, default_settings)
            if patient_age_field_setting is not None:
                if is_value_range(patient_age_field_setting.value):
                    patient_age = generate_age_at_event_date(int(patient_age_field_setting.value.min), int(patient_age_field_setting.value.max))
                    patient_birth_date = calculate_birth_date(patient_meta.event_date, patient_age)
                    patient_row_as_dict[(entity.entity_id), f"{entity.entity_id}/Patient.birthDate"] = str(patient_birth_date)

    for field in entity.fields or []:
        # Tracks extension index to match to headers. Will always increment whenever an Extension is seen, even if the Patient lacks that extension.
        extension_index = 2 # TODO: CHANGE ONCE FHIR SHEETS BUG WITH EXTENSIONS RESOLVED -- CHANGE BOTH LOCATIONS

        if field.path not in C.SPECIAL_FIELDS_SET:
            field_setting: Setting | None = None

            generated_value = None

            '''
            Find field settings, starting with searching for a user defined setting then falling back to the default setting.
            '''
            if field.user_configured:
                field_setting = find_setting(field, configuration.user_responses, default_settings)
                # TODO: This is likely redundant now but leaving to avoid breaking conditional/refactoring
                if field_setting is None:
                    # If no default setting found, well... this ain't gonna work.
                    raise ValueError(f"Both user and default field setting for {field.path} missing.")
                elif field.type == C.FhirType.EXTENSION.value:
                    # Catch extensions to handle them differently.
                    if field.extension_details is None:
                        pass
                        # TODO: Implement error handling
                    else:
                        if field.extension_details.special_handler in SpecialExtensions:
                            generated_value = generate_tribal_affiliation(field_setting, main_db)
                        else:
                            generated_value = handle_by_type(field.extension_details.value_type, field, patient_meta, field_setting)
                else:                            
                    generated_value = handle_by_type(field.type, field, patient_meta, field_setting)

                    # If field is declared by the use case as the end date, see if it is
                    # earlier than the cohort wide "generate until" date. Ensuring that the field
                    # in question is a date is a validation requirement for the Use Case, so the type
                    # can be implied here.
                    if use_case.generation_rules is not None and generated_value is not None:
                        if f"{entity.entity_id}/{field.path}" == use_case.generation_rules.end_date:
                            if isinstance(generated_value, datetime):
                                patient_meta.generate_until_date = min(patient_meta.generate_until_date, generated_value.date())
                            else:
                                raise HTTPException(status_code=500, detail=f"Error generating. End date {use_case.generation_rules.end_date} does not point to a valid datetime.")
            else:
                # Special Type Functions.
                if field.value == C.SpecialTypeFunctions.UUID.value:
                    generated_value = generate_uuid_identifier()
                elif field.value == C.SpecialTypeFunctions.EVENT_DATE.value:
                    generated_value = str(patient_meta.event_date)
                elif field.value == C.SpecialTypeFunctions.CONDITION_CLINICAL_STATUS.value:
                    # determine if abatement setting exists and is not 0.
                    # set value
                    abatement_field = next((afield for afield in entity.fields if afield.path.startswith("Condition.abatement")), None)
                    if abatement_field is not None:
                        # If an abatement field was found at all, delve deeper into the settings.
                        abatement_setting = find_setting(abatement_field, configuration.user_responses, default_settings)
                        # This assumes that the setting is ValueTimeRangeAsDays, this should be refactored if other types are allowed.
                        if abatement_setting.value.start == 0 and abatement_setting.value.end == 0:
                            # If there is no abatement range configured at all, assume status is active.
                            generated_value = C.ConditionClinicalStatusValues.ACTIVE.value
                        else:
                            # Otherwise, if there is some value it means abatement has or will be generated so set to resolved.
                            generated_value = C.ConditionClinicalStatusValues.RESOLVED.value

                    else:
                        # If no abatement field was found in the entity, just assume active.
                        generated_value = C.ConditionClinicalStatusValues.ACTIVE.value
                elif field.value == C.SpecialTypeFunctions.PATIENT_CONTACT_POINT.value:
                    generated_value = [
                        # TODO: HIGH PRIORITY!! "Masked" should be moved to a general setting to cover these values
                        {"system": "email", "value": generate_email(patient_meta.name)},
                        {"system": "phone", "value": fake.basic_phone_number()}
                    ]
                else:
                    generated_value = handle_by_type(field.type, field, patient_meta, field_setting)


            if field.type == C.FhirType.IDENTIFIER.value:
                patient_row_as_dict[(entity.entity_id), f"{entity.entity_id}/{field.path}/Value"] = generated_value
                patient_row_as_dict[(entity.entity_id), f"{entity.entity_id}/{field.path}/System"] = C.identifier_system + ":" + entity.resource_type.lower()
            elif field.type == C.FhirType.CONTACT_POINT.value:
                if isinstance(generated_value, list):
                    for i, v in enumerate(generated_value):
                        patient_row_as_dict[(entity.entity_id), f"{entity.entity_id}/{field.path}[{i}]/Value"] = v["value"]
                        patient_row_as_dict[(entity.entity_id), f"{entity.entity_id}/{field.path}[{i}]/System"] = v["system"]
                else:
                    logger.warning(f"Issue setting ContactPoint. Skipping.")
            elif field.type == C.FhirType.EXTENSION.value:
                if field.extension_details.value_type == "Complex":
                    # TODO: Support complex extension types in the entity model. For now this only actually supports Tribal Affiliation.
                    # Value object needs to be refactored to allow complexity, but for now sets directly to the sub extension value repeatedly.
                    # Eventually this can be made to work universally with the better generated_value handler.
                    if generated_value is not None:
                        patient_row_as_dict[(entity.entity_id), f"{entity.entity_id}/{field.path}.[{extension_index}]/Uri"] = field.extension_details.extension_uri
                        if field.extension_details.special_handler == SpecialExtensions.TRIBAL_AFFILIATION:
                            for sub_ext in field.extension_details.sub_extensions or []:
                                patient_row_as_dict[(entity.entity_id), f"{entity.entity_id}/{field.path}.[{extension_index}].extension.[0]/Uri"] = sub_ext.extension_uri
                                patient_row_as_dict[(entity.entity_id), f"{entity.entity_id}/{field.path}.[{extension_index}].extension.[0]/Value"] = generated_value
                else:
                    patient_row_as_dict[(entity.entity_id), f"{entity.entity_id}/{field.path}.[{extension_index}]/Value"] = generated_value
                    patient_row_as_dict[(entity.entity_id), f"{entity.entity_id}/{field.path}.[{extension_index}]/Uri"] = field.extension_details.extension_uri
                extension_index = extension_index + 1
            else:
                patient_row_as_dict[(entity.entity_id), f"{entity.entity_id}/{field.path}"] = generated_value


def process_static_entity(entity: Entity, patient_row_as_dict: PatientRow):
    '''
    Simplified handler for entirely static entities (e.g., common entities and provider entities)
    '''
    # Handle entity's main fields
    for field in entity.fields or []:
        val = field.value
        if is_value_coding(field.value):
            val = value_coding_to_string(field.value)
        elif isinstance(field.value, str):
            val = field.value
        elif isinstance(field.value, bool):
            val = field.value
        else:
            logger.warning(f"Unable to process {entity.entity_id} field value {field.value}, found unexpected type {type(field.value)}. Skipping.")
            continue
        patient_row_as_dict[(entity.entity_id), f"{entity.entity_id}/{field.path}"] = val
    
