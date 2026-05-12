from api.models.FHIR.patient import HumanName

def has_data_absent_reason_extension(fhir_field: HumanName) -> bool:
    if fhir_field.extension:
        return any(extension.url == "http://hl7.org/fhir/StructureDefinition/data-absent-reason" \
               for extension in fhir_field.extension)
    else:
        return False

def get_data_abasent_reason_value(fhir_field: HumanName) -> str:
    for extension in fhir_field.extension or []:
        if extension.url == "http://hl7.org/fhir/StructureDefinition/data-absent-reason":
            return extension.get_value()
    # TODO: Add actual error handling.
    return "ERROR - Data Absent Reason Value Not Found"