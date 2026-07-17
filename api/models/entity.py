"""
FHIR resource entity models for cohort generation.

This module defines the structure of entities (FHIR resources) used in use case
templates. Entities represent the clinical resources (Patient, Observation, etc.)
that will be generated, including their fields, relationships, and inheritance.
"""

from api.models.field import Field
from fastapi_camelcase import CamelModel
from pydantic import Field as PyField
from typing import Optional

class EntityReference(CamelModel):
    """
    Static reference from one entity to another.
    
    Defines a fixed relationship between resources that will be created
    during generation (e.g., Procedure.performer always references a Practitioner).
    The reference_path specifies where in the resource the reference appears.

    Example (in JSON camel case):
                {
                    "referencePath": "reasonReference",
                    "targetEntity": "PrimaryCondition"
                }
    """
    reference_path: str = PyField(
        ...,
        description="FHIR path where the reference appears in the source resource (e.g., 'Observation.subject')."
    )
    target_entity: str = PyField(
        ...,
        description="Entity ID of the target resource being referenced (e.g., 'PrimaryCondition')."
    )

class DynamicReference(CamelModel):
    """
    Template for dynamic references resolved at generation time.
    
    Used for references that depend on runtime context, such as linking
    to provider entities from a database. The link_identifier matches
    an entry in the common entity's dynamic_references to resolve the
    actual target entity.
    """
    reference_path: str = PyField(
        ...,
        description="FHIR path where the reference will be inserted (e.g., 'DiagnosticReport.performer')."
    )
    link_identifier: str = PyField(
        ...,
        description="Identifier used to match and resolve the target entity at generation time."
    )


class Entity(CamelModel):
    """
    FHIR resource template defining structure and generation rules.
    
    Represents a single FHIR resource (Patient, Observation, Condition, etc.)
    in a use case, including its fields, values, and relationships to other
    resources. Entities can inherit from base entities for reusability.
    
    Attributes:
        entity_id: Unique identifier for this entity within the use case.
        abstract: If true, this entity serves only as a base for inheritance
            and will not be directly generated.
        resource_type: FHIR resource type (e.g., 'Patient', 'Observation').
        fields: List of Field definitions specifying what data to generate.
        base_entity: Optional entity_id to inherit fields from.
        profile: Optional FHIR profile URL this entity conforms to.
        reference_path: Path where this entity is referenced by parent resources.
        static_references: Fixed references this entity makes to other entities.
        dynamic_references: Runtime-resolved references (e.g., to providers).
    
    Examples:
        A Patient entity with demographic fields:
        ```
        Entity(
            entity_id="patient-1",
            abstract=False,
            resource_type="Patient",
            fields=[...],
            profile="http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"
        )
        ```
        
        An Observation inheriting from a base:
        ```
        Entity(
            entity_id="observation-lab",
            abstract=False,
            resource_type="Observation",
            base_entity="observation-base",
            fields=[...]  # Additional fields beyond base
        )
        ```
    """
    entity_id: str = PyField(
        ...,
        description="Unique identifier for this entity within the use case. Used for references and inheritance."
    )
    abstract: bool = PyField(
        ...,
        description="Whether this entity is abstract (serves only as a base for inheritance, not directly generated)."
    )
    resource_type: str = PyField(
        ...,
        description="FHIR resource type this entity represents (e.g., 'Patient', 'Observation', 'Condition')."
    )
    fields: Optional[list[Field]] = PyField(
        default=None,
        description="List of field definitions specifying the data elements to generate for this resource."
    )
    base_entity: Optional[str] = PyField(
        default=None,
        description="Entity ID to inherit fields from. Allows reuse of common field sets across similar resources."
    )
    profile: Optional[str] = PyField(
        default=None,
        description="FHIR profile URL this entity conforms to (e.g., US Core profiles). Added to resource.meta.profile."
    )
    reference_path: Optional[str] = PyField(
        default=None,
        description="FHIR path where parent resources reference this entity (e.g., 'subject' for Patient)."
    )
    static_references: Optional[list[EntityReference]] = PyField(
        default=None,
        description="Fixed references this entity makes to other entities in the use case."
    )
    dynamic_references: Optional[list[DynamicReference]] = PyField(
        default=None,
        description="Template references resolved at generation time (e.g., linking to provider entities from database)."
    )