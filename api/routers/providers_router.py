from typing import Optional
from loguru import logger
from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from api.models.responses.jsonresponse import PrettyJSONResponse
from api.database.database_client import get_main_db
from api.database.db_other_tables import ProviderEntity
from pydantic import BaseModel, Field


router = APIRouter()


# Response Models
class ProviderEntityResponse(BaseModel):
    """
    Single provider entity record response.
    
    Represents a stored provider entity (Practitioner, Organization,
    PractitionerRole) that can be dynamically referenced during cohort
    generation for realistic provider attribution.
    """
    id: int = Field(
        ...,
        description="Database ID of this provider entity record"
    )
    entity_id: str = Field(
        ...,
        description="Unique identifier for this provider entity used in dynamic references"
    )
    resource_type: str = Field(
        ...,
        description="FHIR resource type (e.g., 'Practitioner', 'Organization', 'PractitionerRole')"
    )
    display_name: str = Field(
        ...,
        description="Human-readable display name for this provider"
    )
    entity_json: str = Field(
        ...,
        description="JSON string containing the complete Entity definition for this provider"
    )

    class Config:
        from_attributes = True


class ProviderEntityListResponse(BaseModel):
    """
    Response containing a list of provider entities with count.
    
    Used for listing all available provider entities, optionally filtered
    by resource type.
    """
    count: int = Field(
        ...,
        description="Number of provider entities in the response"
    )
    providers: list[ProviderEntityResponse] = Field(
        ...,
        description="List of provider entity records"
    )

class ProviderEntityCreateRequest(BaseModel):
    """
    Request body for creating a new provider entity.
    
    Defines all required fields for adding a provider entity to the
    database for use in dynamic references during generation.
    """
    entity_id: str = Field(
        ...,
        description="Unique identifier for this provider entity"
    )
    resource_type: str = Field(
        ...,
        description="FHIR resource type (e.g., 'Practitioner', 'Organization')"
    )
    display_name: str = Field(
        ...,
        description="Human-readable display name"
    )
    entity_json: str = Field(
        ...,
        description="JSON string containing the complete Entity definition"
    )

class ProviderEntityUpdateRequest(BaseModel):
    """
    Request body for updating an existing provider entity.
    
    All fields are optional - only provided fields will be updated.
    Enables partial updates to provider entity records.
    """
    resource_type: Optional[str] = Field(
        default=None,
        description="FHIR resource type to update"
    )
    display_name: Optional[str] = Field(
        default=None,
        description="Display name to update"
    )
    entity_json: Optional[str] = Field(
        default=None,
        description="Entity JSON definition to update"
    )

class DeleteResponse(BaseModel):
    """
    Response for delete operations on provider entities.
    
    Indicates success/failure of deletion with explanatory message.
    """
    success: bool = Field(
        ...,
        description="Whether the deletion succeeded"
    )
    message: str = Field(
        ...,
        description="Human-readable message describing the deletion result"
    )


@router.get("/providers", response_class=PrettyJSONResponse)
async def list_providers(
    resource_type: Optional[str] = None,
    db: Session = Depends(get_main_db)
):
    """
    List all provider entities, optionally filtered by resource type.
    
    Args:
        resource_type: Optional filter by resource type (e.g., 'Practitioner', 'Organization', 'PractitionerRole')
    """
    try:
        query = db.query(ProviderEntity)
        
        if resource_type:
            query = query.filter(ProviderEntity.resource_type == resource_type)
        
        providers = query.all()
        
        return ProviderEntityListResponse(
            count=len(providers),
            providers=[ProviderEntityResponse.model_validate(p) for p in providers]
        )
    except Exception as e:
        logger.error(f"Error listing providers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers/{provider_id}", response_class=PrettyJSONResponse)
async def get_provider(
    provider_id: int,
    db: Session = Depends(get_main_db)
):
    """
    Get a specific provider entity by ID.
    """
    try:
        provider = db.query(ProviderEntity).filter(
            ProviderEntity.id == provider_id
        ).first()
        
        if not provider:
            raise HTTPException(
                status_code=404,
                detail=f"Provider with ID {provider_id} not found"
            )
        
        return ProviderEntityResponse.model_validate(provider)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting provider {provider_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/providers", response_class=PrettyJSONResponse, status_code=status.HTTP_201_CREATED)
async def create_provider(
    request: ProviderEntityCreateRequest,
    db: Session = Depends(get_main_db)
):
    """
    Create a new provider entity.
    """
    try:
        # Check if entity_id already exists
        existing = db.query(ProviderEntity).filter(
            ProviderEntity.entity_id == request.entity_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Provider entity with entity_id '{request.entity_id}' already exists"
            )
        
        # Create new provider
        provider = ProviderEntity(
            entity_id=request.entity_id,
            resource_type=request.resource_type,
            display_name=request.display_name,
            entity_json=request.entity_json
        )
        
        db.add(provider)
        db.commit()
        db.refresh(provider)
        
        logger.info(f"Created provider entity: {request.entity_id} (ID: {provider.id})")
        return ProviderEntityResponse.model_validate(provider)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating provider: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/providers/{entity_id}", response_class=PrettyJSONResponse)
async def update_provider(
    entity_id: str,
    request: ProviderEntityUpdateRequest,
    db: Session = Depends(get_main_db)
):
    """
    Update an existing provider entity by entity_id.
    """
    try:
        provider = db.query(ProviderEntity).filter(
            ProviderEntity.entity_id == entity_id
        ).first()
        
        if not provider:
            raise HTTPException(
                status_code=404,
                detail=f"Provider entity '{entity_id}' not found"
            )
        
        # Update fields if provided (entity_id cannot be updated)
        if request.resource_type is not None:
            provider.resource_type = request.resource_type
        
        if request.display_name is not None:
            provider.display_name = request.display_name
        
        if request.entity_json is not None:
            provider.entity_json = request.entity_json
        
        db.commit()
        db.refresh(provider)
        
        logger.info(f"Updated provider entity: {entity_id}")
        return ProviderEntityResponse.model_validate(provider)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating provider {entity_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/providers/{provider_id}", response_class=PrettyJSONResponse)
async def delete_provider(
    provider_id: int,
    db: Session = Depends(get_main_db)
):
    """
    Delete a provider entity by ID.
    """
    try:
        provider = db.query(ProviderEntity).filter(
            ProviderEntity.id == provider_id
        ).first()
        
        if not provider:
            raise HTTPException(
                status_code=404,
                detail=f"Provider with ID {provider_id} not found"
            )
        
        entity_id = provider.entity_id
        db.delete(provider)
        db.commit()
        
        logger.info(f"Deleted provider ID {provider_id} (entity_id: {entity_id})")
        return DeleteResponse(
            success=True,
            message=f"Provider ID {provider_id} deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting provider {provider_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))