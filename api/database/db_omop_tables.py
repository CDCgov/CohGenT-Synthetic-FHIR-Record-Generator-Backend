"""Module defining OMOP v5.4 ORM models and helper utilities.

This module declares SQLAlchemy DeclarativeBase and mapped classes representing
the OMOP CDM tables and views used by the application. It also includes
helper enums and a utility to verify presence of required tables in a target
database connection.

NOTE: Code originally from broader work with the OMOP CDM and may not be succinct to the needs of this codebase.
"""

import enum
import logging
from datetime import date, datetime
from typing import Annotated

from sqlalchemy import Connection, ForeignKey, Inspector, String, inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, RelationshipProperty, mapped_column, registry, relationship

logger: logging.Logger = logging.getLogger("src.models.db_omop_models")

concept_concept_id: str = "concept.concept_id"
str_1 = Annotated[str, 1]
str_20 = Annotated[str, 20]
str_50 = Annotated[str, 50]
str_255 = Annotated[str, 255]


class BaseOMOP54(DeclarativeBase):
    """Declarative base for OMOP v5.4 models with custom type mappings.

    Configures __allow_unmapped__ and a registry that maps Annotated str types
    to SQLAlchemy String columns of the appropriate length.
    """

    __allow_unmapped__ = True
    registry = registry(type_annotation_map={str_255: String(255), str_1: String(1), str_20: String(20), str_50: String(50)})


metadata_omop54 = BaseOMOP54.metadata


class Concept(BaseOMOP54):
    """ORM for the concept table.

    Attributes map to columns in the OMOP concept table including relationships
    to ConceptClass, Domain, and Vocabulary.
    """

    __tablename__: str = "concept"

    concept_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    concept_name: Mapped[str_255]
    domain_id: Mapped[str] = mapped_column(ForeignKey("domain.domain_id"), index=True)
    vocabulary_id: Mapped[str] = mapped_column(ForeignKey("vocabulary.vocabulary_id"), index=True)
    concept_class_id: Mapped[str] = mapped_column(ForeignKey("concept_class.concept_class_id"), index=True)
    standard_concept: Mapped[str_1 | None]
    concept_code: Mapped[str] = mapped_column(String(50), index=True)
    valid_start_date: Mapped[date]
    valid_end_date: Mapped[date]
    invalid_reason: Mapped[str_1 | None]

    concept_class: RelationshipProperty = relationship("ConceptClass", primaryjoin="Concept.concept_class_id == ConceptClass.concept_class_id")
    domain: RelationshipProperty = relationship("Domain", primaryjoin="Concept.domain_id == Domain.domain_id")
    vocabulary: RelationshipProperty = relationship("Vocabulary", primaryjoin="Concept.vocabulary_id == Vocabulary.vocabulary_id")


class ConceptClass(BaseOMOP54):
    """ORM for the concept_class table.

    Provides concept class metadata and foreign key to the representative concept.
    """

    __tablename__: str = "concept_class"

    concept_class_id: Mapped[str_20] = mapped_column(primary_key=True, index=True)
    concept_class_name: Mapped[str_255]
    concept_class_concept_id: Mapped[int] = mapped_column(ForeignKey(concept_concept_id))

    concept_class_concept: RelationshipProperty = relationship("Concept", primaryjoin="ConceptClass.concept_class_concept_id == Concept.concept_id")


class ConceptRelationship(BaseOMOP54):
    """ORM for the concept_relationship table.

    Models relationships between concept ids and includes dates and invalid reason.
    """

    __tablename__: str = "concept_relationship"

    concept_id_1: Mapped[int] = mapped_column(ForeignKey(concept_concept_id), primary_key=True, index=True)
    concept_id_2: Mapped[int] = mapped_column(ForeignKey(concept_concept_id), primary_key=True, index=True)
    relationship_id: Mapped[str] = mapped_column(ForeignKey("relationship.relationship_id"), primary_key=True, index=True)
    valid_start_date: Mapped[date]
    valid_end_date: Mapped[date]
    invalid_reason: Mapped[str_1 | None]

    concept: RelationshipProperty = relationship("Concept", primaryjoin="ConceptRelationship.concept_id_1 == Concept.concept_id")
    concept1: RelationshipProperty = relationship("Concept", primaryjoin="ConceptRelationship.concept_id_2 == Concept.concept_id")
    relationship: RelationshipProperty = relationship("Relationship")


class ConceptConceptRelationship(BaseOMOP54):
    """View model for joined concept-concept relationship information.

    Typically used for search/indexing and read-only operations.
    """

    __tablename__: str = "concept_concept_relationship_vw"

    concept_id_1: Mapped[int] = mapped_column(primary_key=True)
    concept_name_1: Mapped[str_255 | None]
    concept_code_1: Mapped[str_50 | None]
    vocabulary_id_1: Mapped[str_20 | None]
    concept_id_2: Mapped[int] = mapped_column(primary_key=True)
    concept_name_2: Mapped[str_255 | None]
    concept_code_2: Mapped[str_50 | None]
    vocabulary_id_2: Mapped[str_20 | None]
    relationship_id: Mapped[str_20] = mapped_column(primary_key=True)
    valid_start_date: Mapped[date | None]
    valid_end_date: Mapped[date | None]
    invalid_reason: Mapped[str_1 | None]


class ConceptAncestor(BaseOMOP54):
    """ORM for concept_ancestor table mapping ancestor/descendant relationships."""

    __tablename__: str = "concept_ancestor"

    ancestor_concept_id: Mapped[int] = mapped_column(primary_key=True)
    descendant_concept_id: Mapped[int] = mapped_column(primary_key=True)
    min_levels_of_separation: Mapped[int]
    max_levels_of_separation: Mapped[int]


class ConceptConceptAncestor(BaseOMOP54):
    """View model for concept ancestor relationships with names and vocabularies."""

    __tablename__: str = "concept_concept_ancestor_vw"

    ancestor_concept_id: Mapped[int] = mapped_column(primary_key=True)
    ancestor_concept_name: Mapped[str]
    ancestor_concept_code: Mapped[str]
    ancestor_vocabulary_id: Mapped[str]
    descendant_concept_id: Mapped[int] = mapped_column(primary_key=True)
    descendant_concept_name: Mapped[str]
    descendant_concept_code: Mapped[str]
    descendant_vocabulary_id: Mapped[str]
    min_levels_of_separation: Mapped[int]
    max_levels_of_separation: Mapped[int]


class Domain(BaseOMOP54):
    """ORM for the domain table linking domain identifiers to domain concepts."""

    __tablename__: str = "domain"

    domain_id: Mapped[str_20] = mapped_column(primary_key=True, index=True)
    domain_name: Mapped[str_255]
    domain_concept_id: Mapped[int] = mapped_column(ForeignKey(concept_concept_id))

    domain_concept: RelationshipProperty = relationship("Concept", primaryjoin="Domain.domain_concept_id == Concept.concept_id")


class Relationship(BaseOMOP54):
    """ORM for relationship definitions including reverse relationship id."""

    __tablename__: str = "relationship"

    relationship_id: Mapped[str_20] = mapped_column(primary_key=True, index=True)
    relationship_name: Mapped[str_255]
    is_hierarchical: Mapped[str_1]
    defines_ancestry: Mapped[str_1]
    reverse_relationship_id: Mapped[str_20]
    relationship_concept_id: Mapped[int] = mapped_column(ForeignKey(concept_concept_id))

    relationship_concept: RelationshipProperty = relationship("Concept")


class Vocabulary(BaseOMOP54):
    """ORM for the vocabulary table and its link to a representative concept."""

    __tablename__: str = "vocabulary"

    vocabulary_id: Mapped[str_20] = mapped_column(primary_key=True, index=True)
    vocabulary_name: Mapped[str_255]
    vocabulary_reference: Mapped[str_255 | None]
    vocabulary_version: Mapped[str_255 | None]
    vocabulary_concept_id: Mapped[int] = mapped_column(ForeignKey(concept_concept_id))

    vocabulary_concept: RelationshipProperty = relationship("Concept", primaryjoin="Vocabulary.vocabulary_concept_id == Concept.concept_id")



class ConceptRelationshipStaged(BaseOMOP54):
    """ORM for staged concept relationships pending commit or deletion."""

    __tablename__ = "concept_relationship_staged"

    concept_id_1: Mapped[int] = mapped_column(ForeignKey(concept_concept_id), primary_key=True, index=True)
    concept_id_2: Mapped[int] = mapped_column(ForeignKey(concept_concept_id), primary_key=True, index=True)
    relationship_id: Mapped[str] = mapped_column(ForeignKey("relationship.relationship_id"), primary_key=True, index=True)
    valid_start_date: Mapped[date]
    valid_end_date: Mapped[date]
    invalid_reason: Mapped[str_1 | None]


class CRStagingStatus(enum.Enum):
    """Enum for staging lifecycle statuses: staged, committed, deleted."""

    staged = "staged"
    committed = "committed"
    deleted = "deleted"


class CRStagedStatus(BaseOMOP54):
    """ORM for staging status rows tracking state and last update time."""

    __tablename__ = "cr_staged_status"

    concept_id_1: Mapped[int] = mapped_column(primary_key=True)
    concept_id_2: Mapped[int] = mapped_column(primary_key=True)
    relationship_id: Mapped[str_20] = mapped_column(primary_key=True)
    status: Mapped[CRStagingStatus]
    date_updated: Mapped[datetime]


class StagedView(BaseOMOP54):
    """View model exposing staged relationships and their metadata."""

    __tablename__ = "staged_view_vw"

    concept_id_1: Mapped[int] = mapped_column(primary_key=True)
    concept_name_1: Mapped[str_255 | None]
    concept_code_1: Mapped[str_50 | None]
    vocabulary_id_1: Mapped[str_20 | None]
    concept_id_2: Mapped[int] = mapped_column(primary_key=True)
    concept_name_2: Mapped[str_255 | None]
    concept_code_2: Mapped[str_50 | None]
    vocabulary_id_2: Mapped[str_20 | None]
    relationship_id: Mapped[str_20] = mapped_column(primary_key=True)
    valid_start_date: Mapped[date]
    valid_end_date: Mapped[date]
    status: Mapped[CRStagingStatus]
    date_updated: Mapped[datetime]


class Users(BaseOMOP54):
    """ORM for users table storing basic user identity information."""

    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_email: Mapped[str_255]
    user_name: Mapped[str_255]
    user_sub_claim: Mapped[str]


class CommentType(enum.Enum):
    """Enum for comment types used in the comments table."""

    CONCEPT = "concept"
    CONCEPT_RELATIONSHIP = "concept_relationship"


class Comments(BaseOMOP54):
    """ORM for comments associated with concepts or concept relationships.

    Stores author, text, timestamps and deletion flag.
    """

    __tablename__ = "comments"

    comment_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped[CommentType]
    concept_id: Mapped[int]
    concept_id_2: Mapped[int | None]
    relationship_id: Mapped[str | None]
    author_user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    text: Mapped[str_255]
    date: Mapped[datetime]
    last_updated: Mapped[datetime]
    deleted: Mapped[bool]


def check_existence_of_omop_tables(conn: Connection) -> dict[str, bool]:
    """Verify required OMOP tables/views exist in the given database connection.

    Args:
        conn: SQLAlchemy Connection instance to inspect.

    Returns:
        A dictionary mapping table/view names to booleans indicating presence.
    """

    table_list = [
        Concept,
        ConceptClass,
        ConceptRelationship,
        ConceptConceptRelationship,
        ConceptAncestor,
        ConceptConceptAncestor,
        Domain,
        Relationship,
        Vocabulary,
        ConceptRelationshipStaged,
        CRStagedStatus,
        StagedView,
        Users,
        Comments,
    ]
    output_dict: dict[str, bool] = {}

    insp: Inspector = inspect(conn)

    for table in table_list:
        tablename = table.__tablename__
        output_dict[tablename] = insp.has_table(table_name=tablename)

    return output_dict
