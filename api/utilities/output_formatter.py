import time
from typing import Any
from api.models.FHIR.fhirresource import FHIRResource
from api.models.responses.generation_summary import GenerationParameters, GenerationSummaryJson, GenerationSummaryBinary, PatientContainer, PatientRecordSummary
from api.models.cohort_settings import CohortSettings
from api.models.FHIR.patient import Patient
from api.models.FHIR.bundle import Bundle, BundleEntry
from collections import Counter
from datetime import datetime, timezone
from api.utilities.fhir_parser import has_data_absent_reason_extension, get_data_abasent_reason_value
import zipfile
from io import BytesIO
import base64
import orjson
from loguru import logger
from collections import defaultdict
from zoneinfo import ZoneInfo

def package_contents_as_json(bundle_list: list[Bundle], cohort_settings: CohortSettings) -> GenerationSummaryJson:
    patient_containers: list[PatientContainer] = []
    generation_parameters = parse_generation_parameters(cohort_settings)
    for bundle in bundle_list:
        patient_summary = parse_patient_summary_from_bundle(bundle)
        patient_containers.append(PatientContainer(summary = patient_summary, fhir = bundle))
    return GenerationSummaryJson(
        time_stamp = _get_time_as_utc_iso_string(),
        generation_parameters = generation_parameters,
        generation_summary = patient_containers)

def package_contents_as_binary(bundle_list: list[Bundle], cohort_settings: CohortSettings) -> GenerationSummaryBinary:
    patient_containers: list[Any] = []
    zip_buffer = BytesIO()  # Create a buffer for the ZIP archive
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for i, bundle in enumerate(bundle_list):
            patient_summary = parse_patient_summary_from_bundle(bundle)
            patient_containers.append({"summary": patient_summary})
            file_name = f"patient_{i+1}.json"
            try:
                json_bundle = orjson.dumps(bundle.to_dict(), option=orjson.OPT_INDENT_2)
                zipf.writestr(file_name, json_bundle)
            except Exception:
                logger.error(f"Unable to parse JSON for {file_name} with bundle id of {bundle.id}. Skipping.")

        zipf.writestr("meta_data.json", cohort_settings.model_dump_json(indent=2))

    zip_base64 = base64.b64encode(zip_buffer.getvalue()).decode('utf-8')
    generation_parameters = parse_generation_parameters(cohort_settings)

    
    return GenerationSummaryBinary(
            time_stamp= _get_time_as_utc_iso_string(),
            generation_parameters= generation_parameters,
            generation_summary= patient_containers,
            data= zip_base64
        )

def _get_time_as_utc_iso_string() -> str:
    current_time = datetime.now(timezone.utc)
    return current_time.isoformat()

def parse_generation_parameters(cohort_settings: CohortSettings) -> GenerationParameters:
    return GenerationParameters(
                use_case_id = cohort_settings.use_case_id,
                count = cohort_settings.count,
                seed = cohort_settings.seed)

def parse_patient_summary_from_bundle(bundle: Bundle) -> PatientRecordSummary:
    patient_summary = {}
    assert bundle.entry is not None
    bundle_entries: list[BundleEntry] = bundle.entry

    patient_resource = next(bundle_entry.resource for bundle_entry in bundle_entries if bundle_entry.resource["resourceType"] == "Patient")

    # patient_resource: FhirResource = patient_resource["resource"]
    patient_resource = Patient.model_validate(patient_resource)
    patient_summary["name"] = parse_patient_name(patient_resource)
    patient_summary["birthDate"] = str(patient_resource.birth_date)
    patient_summary["sex"] = patient_resource.gender
    list_of_resource_types = [bundle_entry.resource["resourceType"] for bundle_entry in bundle_entries]
    resource_counts = Counter(list_of_resource_types)
    patient_summary["resourceCounts"] = dict(resource_counts)
    return PatientRecordSummary.model_validate(patient_summary)

def parse_patient_name(patient_resource: Patient) -> str:
        if patient_resource.name and patient_resource.name[0]:
            if has_data_absent_reason_extension(patient_resource.name[0]):
                return get_data_abasent_reason_value(patient_resource.name[0])
            elif patient_resource.name[0].given and patient_resource.name[0].family:
                return f"{patient_resource.name[0].given[0]} {patient_resource.name[0].family}"
            else:
                logger.error(f"Failure parsing name field for Patient/{patient_resource.id}")
                return "ERROR - Failed to parse Name"
        else:
            logger.error(f"No name field found for Patient/{patient_resource.id}")
            return "ERROR - No Name Found"

def package_contents_as_ndjson(record_list: list[list[FHIRResource]], cohort_settings: CohortSettings) -> GenerationSummaryBinary:
    flat_resources: list[FHIRResource] = [resource for patient_resources in record_list for resource in patient_resources]
    resources_grouped_by_type: dict[str, list[FHIRResource]] = defaultdict(list)

    for resource in flat_resources:
        resource_type = resource.resource_type
        resources_grouped_by_type[resource_type].append(resource)
    
    patient_containers: list[Any] = [] # make summary from the patient set
    for patient_record in record_list:
        patient_summary = parse_patient_summary_from_obj(patient_record)
        patient_containers.append({"summary": patient_summary})

    zip_buffer = BytesIO()  # Create a buffer for the ZIP archive
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for resource_type, resource_list in resources_grouped_by_type.items():
            # patient_summary = parse_patient_summary(bundle)
            file_name = f"{resource_type}.ndjson"
            ndjson_lines = [resource.model_dump_json(by_alias=True, exclude_none=True) for resource in resource_list]
        
            # Join with newlines to create NDJSON
            ndjson_outputs = '\n'.join(ndjson_lines)
            try:
                zipf.writestr(file_name, ndjson_outputs)
            except Exception:
                logger.error(f"Unable to write NDJSON for {file_name}. Skipping.")
    
        zipf.writestr("meta_data.json", cohort_settings.model_dump_json(indent=2))

    zip_base64 = base64.b64encode(zip_buffer.getvalue()).decode('utf-8')
    generation_parameters = parse_generation_parameters(cohort_settings)
    return GenerationSummaryBinary.model_validate({
            "timeStamp": _get_time_as_utc_iso_string(),
            "generationParameters": generation_parameters,
            "generationSummary": patient_containers,
            "data": zip_base64
        })

def parse_patient_summary_from_obj(patient_record: list[FHIRResource]) -> PatientRecordSummary:
    patient_summary = {}
    _patient_resource = next(resource for resource in patient_record if resource.resource_type == "Patient")

    # patient_resource: FhirResource = patient_resource["resource"]
    patient_resource = Patient.model_validate(_patient_resource.model_dump(by_alias=True, exclude_none=True))
    patient_summary["name"] = parse_patient_name(patient_resource)
    patient_summary["birthDate"] = str(patient_resource.birth_date)
    patient_summary["sex"] = patient_resource.gender
    list_of_resource_types = [resource.resource_type for resource in patient_record]
    resource_counts = Counter(list_of_resource_types)
    patient_summary["resourceCounts"] = dict(resource_counts)
    return PatientRecordSummary.model_validate(patient_summary)