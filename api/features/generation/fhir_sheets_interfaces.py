from fhir_sheets.core.model.cohort_data_entity import HeaderEntry
from fhir_sheets.core.model.resource_definition_entity import ResourceDefinition
from fhir_sheets.core.model.resource_link_entity import ResourceLink
from api.models.entity import Entity
from api.features.generation.constants import FhirResourceTypes, FhirType
'''
FHIR Sheets Input Builders
'''
def generate_all(entities: list[Entity], dynamic_links: list[tuple[str, str, str]] = [], mask_pii_enabled: bool = False) -> tuple[list[ResourceDefinition], list[ResourceLink], list[HeaderEntry]]:
    '''
    Process Entities into FHIR Sheets Resource Definitions, Resource Links, and Header Entries
    '''
    return (generate_resource_definitions(entities), generate_resource_links(entities, dynamic_links), generate_header_entries(entities, mask_pii_enabled))

def generate_header_entries(entities: list[Entity], mask_pii_enabled: bool = False) -> list[HeaderEntry]:
    '''
    Process Entities into FHIR Sheets Header Entries
    '''
    header_entries: list[HeaderEntry] = []

    # FHIR Sheets uses an index for extensions to differentiate them, so must be tracked.
    extension_index = 2 # TODO: CHANGE ONCE FHIR SHEETS BUG WITH EXTENSIONS RESOLVED -- CHANGE BOTH LOCATIONS

    for entity in entities:
        for field in entity.fields or []:
            # TODO: Add special handler for identifier.
            if field.type == FhirType.IDENTIFIER.value:
                header_entry_value = HeaderEntry(
                    entity.entity_id,
                    f"{entity.entity_id}/{field.path}/Value",
                    f"{entity.resource_type}.identifier.[0].value",
                    "string",
                    None)
                header_entry_system = HeaderEntry(
                    entity.entity_id,
                    f"{entity.entity_id}/{field.path}/System",
                    f"{entity.resource_type}.identifier.[0].system",
                    "string",
                    None
                )
                header_entries.append(header_entry_value)
                header_entries.append(header_entry_system)
            elif field.type == FhirType.CONTACT_POINT.value:
                # NOTE: Telecom assumes a chance of only email and/or phone.
                for i in range(2):
                    header_entry_telecom_value = HeaderEntry(
                        entity.entity_id,
                        f"{entity.entity_id}/{field.path}[{i}]/Value",
                        f"{field.path}.[{i}].value",
                        "string",
                        None)
                    header_entry_telecom_system = HeaderEntry(
                        entity.entity_id,
                        f"{entity.entity_id}/{field.path}[{i}]/System",
                        f"{field.path}.[{i}].system",
                        "string",
                        None
                    )
                    header_entries.append(header_entry_telecom_value)
                    header_entries.append(header_entry_telecom_system)
            elif field.type == FhirType.EXTENSION.value:
                extension_uri_header_entry = HeaderEntry(
                    entity.entity_id,
                    f"{entity.entity_id}/{field.path}.[{extension_index}]/Uri",
                    f"{entity.resource_type}.extension.[{extension_index}].url",
                    "string",
                    None)
                header_entries.append(extension_uri_header_entry)
                
                assert field.extension_details # Extension must always have extension details.
                
                if field.extension_details.value_type == "Complex": #field.extension_details.sub_extensions is not None:
                    # TODO ITERATE OVER SUB EXT, MUST EXIST IF TYPE IS COMPLEX
                    # TODO: This should be turned into a recursive function if needed for more than 1 layer of complexity, but that is rare.
                    # NOTE: In the main generation, only Tribal Affiliation is currently supported, though this structure should work for headers universally.
                    sub_extension_index = 0
                    for sub_ext in field.extension_details.sub_extensions or []:
                        sub_ext_value_header_entry = HeaderEntry(
                            entity.entity_id,
                            f"{entity.entity_id}/{field.path}.[{extension_index}].extension.[{sub_extension_index}]/Value",
                            f"{entity.resource_type}.extension.[{extension_index}].extension.[{sub_extension_index}].value{sub_ext.value_type[0].upper() + sub_ext.value_type[1:]}",
                            sub_ext.value_type,
                            None                            
                        )
                        sub_ext_uri_header_entry = HeaderEntry(
                            entity.entity_id,
                            f"{entity.entity_id}/{field.path}.[{extension_index}].extension.[{sub_extension_index}]/Uri",
                            f"{entity.resource_type}.extension.[{extension_index}].extension.[{sub_extension_index}].url",
                            "string",
                            None                            
                        )                       
                        header_entries.append(sub_ext_value_header_entry)
                        header_entries.append(sub_ext_uri_header_entry)

                else:
                    extension_value_header_entry = HeaderEntry(
                        entity.entity_id,
                        f"{entity.entity_id}/{field.path}.[{extension_index}]/Value",
                        f"{entity.resource_type}.extension.[{extension_index}].value{field.extension_details.value_type.capitalize()}",
                        field.extension_details.value_type,
                        None
                    )
                    header_entries.append(extension_value_header_entry)
                
                extension_index = extension_index + 1
            else:
                header_entry = HeaderEntry(
                    entity.entity_id,
                    f"{entity.entity_id}/{field.path}",
                    field.path,
                    field.type,
                    None)
                header_entries.append(header_entry)
    return header_entries

def generate_resource_links(entities: list[Entity], dynamic_links: list[tuple[str,str,str]] = [], subject_entity_name: str = "PrimaryPatient") -> list[ResourceLink]:
    '''
    Process Entities into FHIR Sheets Resource Links
    '''
    resource_links: list[ResourceLink] = []
    for entity in entities:
        if entity.reference_path:
            link = ResourceLink(entity.entity_id, entity.reference_path, subject_entity_name)
            resource_links.append(link)
        if entity.static_references:
            for reference in entity.static_references:
                link = ResourceLink(entity.entity_id, reference.reference_path, reference.target_entity)
                resource_links.append(link)
    
    for item in dynamic_links:
        link = ResourceLink(*item)
        resource_links.append(link)

    return resource_links
    

def generate_resource_definitions(entities: list[Entity]) -> list[ResourceDefinition]:
    '''
    Process Entities into FHIR Sheets Resource Definitions
    '''
    resource_definitions: list[ResourceDefinition] = []
    for entity in entities:
        resource_definitions.append(ResourceDefinition(
                entity.entity_id,
                entity.resource_type,
                [entity.profile] if entity.profile is not None else []
        ))
    return resource_definitions
