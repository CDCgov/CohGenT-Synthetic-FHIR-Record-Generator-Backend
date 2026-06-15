from typing import Any

from sqlalchemy.orm import Session

from api.features.generation.alias_types import Distributions, PatientRow
from api.features.generation.entity_handler import process_entity
from api.features.generation.generators.email import generate_email
from api.features.generation.generators.names import generate_name
from api.features.generation.setting_handler import find_setting
from api.models.field import Field
from loguru import logger
from fhir_sheets.core.model.cohort_data_entity import CohortData, PatientEntry
from api.models.cohort_settings import CohortSettings, MedicationSet, Setting
from api.models.option import ControlType
from api.models.use_case import AdditionalEntity, UseCase, FormRule
from api.models.entity import Entity
from api.models.patient_meta import PatientMeta
from api.models.value_types import is_value_coding, is_value_range, is_value_time_range_as_days, is_value_tribal_affiliation, is_value_prevalence
from api.features.generation.fhir_sheets_interfaces import generate_all
from api.utilities.file_reader import get_use_case_by_id, read_common_entity
from api.features.generation.type_handlers import handle_by_type, process_choice_of_data_type_value, fhir_type_match_check, value_coding_to_string
from api.features.generation.weighted_values import distribute_weighted_values, select_medication_set
import api.features.generation.constants as C
from api.features.generation.special_extension_handlers import SpecialExtensions, generate_tribal_affiliation
from faker import Faker
import random
import time
from datetime import datetime, timedelta
from copy import copy
from api.features.generation.provider_cache import ProviderCache
from api.features.generation.generators.uuids import generate_uuid_identifier
from api.features.generation.generators.dates import generate_event_datetime, generate_age_at_event_date, calculate_birth_date
from fastapi import HTTPException
from api.utilities.settings import get_settings
from api.utilities.logger_setup import create_run_logger, log_resource_definitions, log_resource_links
from api.utilities.logger_tables import log_pydantic_as_tables
from enum import Enum

fake = Faker()
settings = get_settings()



class LoadedCommonEntityKeys(Enum):
    DIAGNOSTIC_REPORT = "DiagnosticReport"

def start_generation(configuration: CohortSettings, main_db: Session, iteration_limit: int = 50):
    start = time.time() # Start run timer
    session_id = f"{datetime.fromtimestamp(start)} - {generate_uuid_identifier()}"

    entity_cache = ProviderCache(main_db)
    
    if settings.enable_run_logs:
        log_handler_id = create_run_logger(session_id)

    with logger.contextualize(run_id=session_id):
        if settings.enable_run_logs:
            logger.info((f'== COHORT GENERATION LOG ==\n'
                    f'  Generation Parameter Summary\n'
                    f'    Use Case ID: {configuration.use_case_id}\n'
                    f'    Patient Count: {configuration.count}\n' 
                    f'    Seed: {configuration.seed}\n'
                    f'    Time: {datetime.fromtimestamp(start)}'
                ))
            logger.info("\n")
            logger.info(log_pydantic_as_tables(session_id, "Cohort User Settings", configuration))
    
    # Set seeds for Random and Faker.
    Faker.seed(configuration.seed)
    random.seed(configuration.seed)

    use_case: UseCase = get_use_case_by_id(configuration.use_case_id)

    # Build default settings from Use Case.
    if use_case.form_rules is None:
        raise HTTPException(status_code=500, detail=f"No Form Rules found for {use_case.use_case_id}.")
    else:
        default_settings = parse_default_settings(use_case.form_rules)

    # Initialize major entities (non-repeatable)
    entities: list[Entity] = generate_entities(use_case)
    dynamic_entities: list[Entity] = []
    dynamic_resource_links: list[tuple[str, str, str]] = [] # Entity A (Origin) -> Path -> Entity B (Target), typically for Diagnostic Reports -> Observation on .result.

    # Pre-load common entities
    loaded_common_entities: dict[LoadedCommonEntityKeys, Entity] = {}
    if use_case.common_entities is not None and use_case.common_entities.diagnostic_report is not None:
        dr_entity_temp = read_common_entity(use_case.common_entities.diagnostic_report)
        if dr_entity_temp is not None:
            loaded_common_entities[LoadedCommonEntityKeys.DIAGNOSTIC_REPORT] = dr_entity_temp
            with logger.contextualize(run_id=session_id):
                if settings.enable_run_logs:
                    logger.info(f"Successfully loaded common entity: {use_case.common_entities.diagnostic_report}")

    # Pre-loop Initializers
    patients_as_dicts: list[dict[tuple[str,str], str]] = []
    distributions: Distributions = setup_patient_distributions(entities, configuration, default_settings)

    # Cache common entities before loops.
    # TODO: Add error handling on this.
    # NOTE: This uses reference by "entry.type" (when iterating over the additional clinical data/common entities). To fully make this data driven in conjunction with the UI, this likely need to be reworked and more done by ID. Likely needs notable refactoring.
    common_entities_map = {
        entity.entity_id: entity 
        for entity in (use_case.common_entities.additional_entities or [])
    }

    entity_file_cache: dict[str, Entity | None] = {}
    def get_base_entity(common_entity: AdditionalEntity) -> Entity | None:
        if not common_entity.entity_file:
            return None
        if common_entity.entity_file not in entity_file_cache:
            entity_file_cache[common_entity.entity_file] = read_common_entity(common_entity.entity_file)
        return entity_file_cache[common_entity.entity_file]
    
    # Generate Patient Rows
    '''
    Handle static entities and patient initialization.
    '''
    for patient_count in range(configuration.count):
        '''
        Initialize Patient Row and Major Dependent Variables
        patient_row = The row of data for the patient. (Equivalent to spreadsheet row.)
        patient_event_date = The central date for this patient to which other dates are relative.
        patient_gender = The sex/gender of the patient to use for fields which may be gender dependent.
        '''
        patient_row_as_dict: PatientRow = {}
        patient_event_date = generate_event_datetime(configuration.event_period.start, configuration.event_period.end)
        patient_meta: PatientMeta = PatientMeta(patient_event_date, None, None) # Name/Gender set later based on distribution.

        '''
        Set the common end boundary for generation. "Generate until" date is required to be after "end" date if present.
        this setting will be potentially overwritten later in generation if the use case has a field set as end date (e.g., condition abatement).
        The earliest date will always be used.
        '''

        if configuration.event_period.until is not None:
            patient_meta.generate_until_date = configuration.event_period.until
        else:
            patient_meta.generate_until_date = configuration.event_period.end

        '''
        Iterate over entities and build the non repeatable contents of the rows.
        '''
        for entity in entities:
            process_entity(entity,
                           patient_meta,
                           patient_row_as_dict,
                           use_case, distributions,
                           configuration,
                           default_settings,
                           main_db)
        '''
        Handle Additional Clinical Data (Event Sets)
        '''
        if configuration.event_sets:
            for event_set_count, event_set in enumerate(configuration.event_sets):
                
                # If Event Set is set to include diagnostic report, create the diagnostic report. Throw an error if a DR profile is not set within the use case/scenario.
                # Note: The use of a DR is entirely subject to user control. There is no logic applies to confirm it is an appropriate use for a DR.
                # TODO :Fix this conditional error handling, no time atm :(
                # if event_set.include_diagnostic_report and \
                #         use_case.common_entities is not None and \
                #         use_case.common_entities.diagnostic_report is in keys(common_entities):
                #     raise HTTPException(status_code=500, detail="Use case does not support Diagnostic Reports or a diagnostic report entity was not able to be loaded.")
                
                # current_dr_entity_model = None
                # diagnostic_result_entities: list[Entity] = []
 
                # Create a list of entities for the event set.
                '''
                Repetitive generation for event sets.
                "Date grouping" forward to support diagnostic reports.
                '''
                start_date = patient_meta.event_date
                current_date = start_date + timedelta(days=event_set.timing.offset)
                end_date = patient_meta.generate_until_date
                increment = event_set.timing.repeat_timing
                
                '''
                Iteration break to avoid users setting up endless looping. This is controlled by the iteration_limit
                parameter on the generate function. iteration_limit determines the max number of iterations that may
                occur.
                '''
                current_iteration = 1

                while current_date <= end_date:
                    
                    # If include_diagnostc_report, set that up first
                    # Setup reference to build link objects.
                    current_dr_entity_id: str | None = None

                    if event_set.include_diagnostic_report:
                        assert(use_case.common_entities is not None)
                        cloned_dr_entity = copy(loaded_common_entities[LoadedCommonEntityKeys.DIAGNOSTIC_REPORT])
                        cloned_dr_entity.entity_id = f"{cloned_dr_entity.entity_id}_{event_set_count}_{current_date}_{patient_meta.id}"
                        current_dr_entity_id = cloned_dr_entity.entity_id
                        dynamic_entities.append(cloned_dr_entity)
                        assert(event_set.diagnostic_report_concept)

                        for field in cloned_dr_entity.fields or []:
                            key: tuple[str, str] = (cloned_dr_entity.entity_id), f"{cloned_dr_entity.entity_id}/{field.path}"
                            value: str = ""
                            if not field.user_configured:
                                if field.value is not None and field.value == C.SpecialValues.CURRENT.value:
                                    value = str(current_date)
                                else:
                                    value = handle_by_type(field.type, field, patient_meta, None)
                            else:
                                if field.path == "DiagnosticReport.code":
                                    value = f"{event_set.diagnostic_report_concept.system}^{event_set.diagnostic_report_concept.code}^{event_set.diagnostic_report_concept.display}"
                            patient_row_as_dict[key] = value

                    for entry_count, entry in enumerate(event_set.entry):

                        # match to a common entity
                        common_entity = common_entities_map.get(entry.type)


                        if common_entity is not None:

                            if common_entity.entity_file:
                                base_entity = get_base_entity(common_entity)
                            else:
                                base_entity = None
                            if base_entity is not None:
                                cloned_entity = copy(base_entity)
                                cloned_entity.entity_id = f"{cloned_entity.entity_id}_{event_set_count}_{entry_count}_{current_date}_{patient_meta.id}"
                                dynamic_entities.append(cloned_entity)
                                if event_set.include_diagnostic_report and current_dr_entity_id is not None:
                                    dynamic_resource_links.append((current_dr_entity_id, "result", cloned_entity.entity_id))
 
                                for field in cloned_entity.fields or []:
                                    include_field: bool = True
                                    key: tuple[str, str] = (cloned_entity.entity_id), f"{cloned_entity.entity_id}/{field.path}"
                                    value: str = "" # Default
                                    if not field.user_configured:
                                        if field.value is not None and field.value == C.SpecialValues.CURRENT.value:
                                            value = str(current_date)
                                        else:
                                            value = handle_by_type(field.type, field, patient_meta, None)
                                    else:
                                        # TODO: make generic/move to handler, supporting all codeable concepts.
                                        # Currently only supports fields with "code" field label for now in alighment with support ofr Observation and Procedure.
                                        if field.path.endswith(".code"):
                                            value = f"{entry.codeable_concept.system}^{entry.codeable_concept.code}^{entry.codeable_concept.display}"
                                        elif field.path.startswith("Observation.value"):
                                            # As each potential choice of data type is a separate field, check alignment with user defined settings and skip what doesn't match.
                                            if fhir_type_match_check(entry.value, field.type):
                                                value = str(process_choice_of_data_type_value(entry, field))
                                            else:
                                                include_field = False # Toggle this is there is not a type match to avoid overwrites from Nones.
                                    if include_field:
                                        patient_row_as_dict[key] = value
                                
                                # Handle dynamic linked entities (e.g., Practitioners/Practitioner Roles) setup in the use case
                                if cloned_entity.dynamic_references and common_entity.dynamic_references:
                                    for dynamic_reference in cloned_entity.dynamic_references or []:
                                        linked_target = next((link_dr for link_dr in common_entity.dynamic_references if link_dr.link_identifier == dynamic_reference.link_identifier), None)
                                        if linked_target:
                                            linked_entity_model = entity_cache.get_provider_entity(linked_target.target_entity_identifier)
                                            dynamic_entities.append(linked_entity_model)
                                            dynamic_resource_links.append((cloned_entity.entity_id, dynamic_reference.reference_path, linked_entity_model.entity_id))
                                            
                                            patient_row_as_dict.update(create_static_entity_patient_rows(linked_entity_model))

                                            # Handled any linked static references (e.g., PractitionerRole -> Organization and Practitioner)
                                            # NOTE: These must be fully self contained entities without any user configuration, the same as the initial dynamic entity.
                                            for static_reference in linked_entity_model.static_references or []:
                                                static_reference_entity = entity_cache.get_provider_entity(static_reference.target_entity)
                                                dynamic_entities.append(static_reference_entity)
                                                dynamic_resource_links.append((linked_entity_model.entity_id, static_reference.reference_path, static_reference_entity.entity_id))
                                                patient_row_as_dict.update(create_static_entity_patient_rows(static_reference_entity))

                                        else:
                                            logger.warning(f"Could not load entity with identifier: {dynamic_reference.link_identifier}. Skipped.")

                        else:
                            raise HTTPException(status_code=422, detail=f"Issue parsing common entity. Unable to find entity file for type {entry.type}. Ensure use case/scenario refers to an existing file name and that the file name is parsable.")


                    # Increment iteration counter and break out of loop if surpassed.
                    current_iteration += 1
                    if current_iteration > iteration_limit:
                        break
                    
                    # If the event set is not set to repeat, immediately break. Otherwise, increment the current date for next loop.
                    if not event_set.timing.repeat:
                        break
                    else:
                        current_date += timedelta(days=increment)

        if use_case.common_entities and use_case.common_entities.medication and configuration.medication_sets:
            medication_base_entity = read_common_entity(use_case.common_entities.medication)
            if medication_base_entity:
                patient_medications, medication_fields = process_patient_medications(
                    medication_base_entity,
                    configuration.medication_sets,
                    patient_count
                )
                dynamic_entities.extend(patient_medications)
                patient_row_as_dict.update(medication_fields)



        patients_as_dicts.append(patient_row_as_dict)
    entities.extend(dynamic_entities)

    end = time.time()
    with logger.contextualize(run_id=session_id):
        if settings.enable_run_logs:
            logger.info(f"Cohort Generated Successfully! Beginning output processing.")
            logger.info(f"Run Time: {end - start}")
    
    '''
    Setting up and calling FHIR Sheets.
    '''
    # Build FHIR Sheets Objects
    resource_definitions, resource_links, headers = generate_all(entities, dynamic_resource_links)
    patients: list[PatientEntry] = [PatientEntry(patient_as_dict) for patient_as_dict in patients_as_dicts]
    cohort = CohortData(headers, patients)

    with logger.contextualize(run_id=session_id):
        if settings.enable_run_logs:
            logger.info(f"Outputting FHIR Sheets Inputs...")
            log_resource_definitions(session_id, resource_definitions)
            log_resource_links(session_id, resource_links)
            logger.info(headers)
            logger.info(patients)
    
    return resource_definitions, resource_links, cohort

'''

'''
def create_static_entity_patient_rows(entity: Entity) -> dict[tuple[str, str], str]:
    new_patient_rows = {}
    # Handle dynamic entity's main fields
    for field in entity.fields or []:
        val = field.value
        if is_value_coding(field.value):
            val = field.value
            # Handle ValueCoding objects
            if is_value_coding(val):
                # Convert to caret-delimited string
                val = value_coding_to_string(val)
        new_patient_rows[(entity.entity_id), f"{entity.entity_id}/{field.path}"] = val
    
    return new_patient_rows
    


'''
Distributions and Settings
'''
def setup_patient_distributions(entities: list[Entity], configuration: CohortSettings, default_settings: list[Setting]) -> Distributions:
    """
    Pre-calculate patient demographic distributions (e.g., gender, race, and ethnicity).
    Only creates distributions for fields that exist in the patient entity.
    
    Args:
        entities: List of all entities from the use case
        configuration: Cohort configuration with user responses
        default_settings: Default settings from use case
        
    Returns:
        Dictionary mapping field paths to lists of pre-distributed values
    """
    patient_entity = next((e for e in entities if e.resource_type == C.FhirResourceTypes.PATIENT.value), None)
    distributions: Distributions = {}
    if patient_entity is None or patient_entity.fields is None:
        return distributions

    for patient_dist_field in C.PATIENT_DIST_FIELDS_SET:                    
        # 1. Get the field from the entity that matches the current one of the patient distribution fields.
        if patient_entity.fields:
            dist_field = next((field for field in patient_entity.fields if field.path == patient_dist_field), None)

            # 2. If it has not been seen previously (so, this is patient #1), do initialize distributions
            #    This could probably move to a pre-processing step.

            dist_field_setting: Setting | None = find_setting(dist_field, configuration.user_responses, default_settings)
            if dist_field_setting is not None:
                dist_list = distribute_weighted_values(configuration.count, dist_field_setting.value)
                distributions[patient_dist_field] = dist_list
            else:
                raise HTTPException(status_code=500, detail=f"Could not find default setting for {patient_dist_field} distribution.")
    return distributions



'''
Patient Data Generator
'''
def generate_patient_row(
    entities: list[Entity],
    distributions: Distributions,
    configuration: CohortSettings,
    default_settings: list[Setting],
    common_entities_map: dict,
    entity_file_cache: dict,
    loaded_common_entities: dict
) -> tuple[dict, list[Entity], list[tuple[str, str, str]]]:
    """
    Generate a single patient's data row.
    Returns: (patient_row_dict, dynamic_entities, dynamic_resource_links)
    Lines 121-413
    """
    pass



'''
Medication Generator
'''
def process_patient_medications(
    medication_base_entity: Entity,
    medication_sets: list[MedicationSet],
    patient_index: int
) -> tuple[list[Entity], dict[tuple[str, str], str]]:
    """
    Select and process medications for a single patient.
    
    Args:
        medication_base_entity: Base entity template for medications
        medication_sets: Available medication sets to choose from
        patient_index: Patient index for unique entity IDs
        
    Returns:
        Tuple of (medication entities, patient field values dict)
    """
    medication_entities: list[Entity] = []
    patient_fields: dict[tuple[str, str], str] = {}
    
    # Select a medication set for this patient
    selected_set = select_medication_set(medication_sets)
    
    # Process each medication in the selected set
    for med_count, medication in enumerate(selected_set.medications):
        medication_entity = copy(medication_base_entity)
        medication_entity.entity_id = f"{medication_entity.entity_id}_{patient_index}_{med_count}"
        medication_entities.append(medication_entity)
        
        for field in medication_entity.fields or []:
            key: tuple[str, str] = (
                medication_entity.entity_id,
                f"{medication_entity.entity_id}/{field.path}"
            )
            value: str | None = None
            
            if not field.user_configured:
                value = field.value if isinstance(field.value, str) else ""
            else:
                if field.path == "MedicationRequest.medicationCodeableConcept":
                    value = f"{medication.codeable_concept.system}^{medication.codeable_concept.code}^{medication.codeable_concept.display}"
                elif field.path == "MedicationRequest.dosageInstruction.[0].text":
                    value = medication.dosage
            
            if value is not None:
                patient_fields[key] = value
    
    return medication_entities, patient_fields



'''
Use Case Handlers
'''
def parse_default_settings(form_rules: list[FormRule]) -> list[Setting]:
    default_settings: list[Setting] = []
    for form_rule in form_rules:
        if form_rule.options is not None:
            for option in form_rule.options:
                # TODO: appropriately type and use as is to match handling of Relative-Time-Range
                setting = { # type: ignore
                    "rule_id": option.rule_id,
                    "value": None
                }
                if option.control == ControlType.CHECKBOX:
                    setting["value"] = option.default_state
                elif option.control == ControlType.RANGE:
                    setting["value"] = {
                        "min": option.default_values[0] if option.default_values is not None else 0,
                        "max": option.default_values[1] if option.default_values is not None else 0
                    }
                elif option.control == ControlType.WEIGHTING:
                    setting["value"] = option.default_values
                elif option.control == ControlType.LOCATION:
                    setting["value"] = {
                        "state": None,
                        "city": None
                    }
                elif option.control == ControlType.RELATIVE_TIME_RANGE:
                    if is_value_time_range_as_days(option.default_values):
                        setting["value"] = option.default_values
                    else:
                        setting["value"] = {
                            "start": 0,
                            "end": 0
                        }
                elif option.control == ControlType.TRIBAL_AFFILIATION:
                    if is_value_tribal_affiliation(option.default_values):
                        setting["value"] = option.default_values
                    elif is_value_prevalence(option.default_values):
                        setting["value"] = option.default_values
                    else:
                        pass
                elif option.control in ControlType:
                    # All other valid control types passed. Some do not allow default values.
                    pass
                else:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Unrecognized control type '{option.control}' for rule '{option.rule_id}'. "
                    )
                
                setting = Setting.model_validate(setting)
                default_settings.append(setting)
    return default_settings

def generate_entities(use_case: UseCase) -> list[Entity]:
    entities = use_case.entities if use_case.entities is not None else []
    non_abstract_entities = [i for i in entities if not i.abstract]
    combined_entities: list[Entity] = []

    for entity in non_abstract_entities:
        combined_entity = build_entity(entity, entities)
        typed_entity: Entity = Entity.model_validate(combined_entity)
        combined_entities.append(typed_entity)
    
    return combined_entities

def build_entity(entity: Entity, entities: list[Entity]) -> Entity:
    '''
    Recursive function to build up a complete entity from base entities.
    '''
    if entity.base_entity is not None:
        base_entity = [i for i in entities if i.entity_id == entity.base_entity][0]
        base_entity = build_entity(base_entity, entities)
        base_entity_fields: list[Field] = base_entity.fields if base_entity.fields is not None else []
        entity.fields.extend(base_entity_fields) # type: ignore
        return entity
    else:
        return entity