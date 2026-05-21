from fhir_sheets.core.model.cohort_data_entity import HeaderEntry
from fhir_sheets.core.model.resource_definition_entity import ResourceDefinition
from fhir_sheets.core.model.resource_link_entity import ResourceLink
from api.models.entity import Entity

'''
FHIR Sheets Input Builders
'''
def generate_all(entities: list[Entity], dynamic_links: list[tuple[str, str, str]] = []) -> tuple[list[ResourceDefinition], list[ResourceLink], list[HeaderEntry]]:
    '''
    Process Entities into FHIR Sheets Resource Definitions, Resource Links, and Header Entries
    '''
    return (generate_resource_definitions(entities), generate_resource_links(entities, dynamic_links), generate_header_entries(entities))

def generate_header_entries(entities: list[Entity]) -> list[HeaderEntry]:
    '''
    Process Entities into FHIR Sheets Header Entries
    '''
    header_entries: list[HeaderEntry] = []
    for entity in entities:
        for field in entity.fields or []:
            # TODO: Add special handler for identifier.
            if field.type == "Identifier":
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
            elif field.type == "ContactPoint":
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
        if entity.other_references:
            for reference in entity.other_references:
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
