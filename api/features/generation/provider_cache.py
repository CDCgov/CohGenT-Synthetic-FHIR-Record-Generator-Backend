"""
Provider Entity Cache Module

Provides lazy-loading cache for provider entities from the database.
Only loads providers when needed to minimize memory usage.
"""
import json
from typing import Dict, Optional
from sqlalchemy.orm import Session
from loguru import logger
from api.database.db_other_tables import ProviderEntity
from api.models.entity import Entity


class ProviderCache:
    """Lazy-loading cache for provider entities"""
    
    def __init__(self, db: Session):
        self.db = db
        self._cache: Dict[str, Entity] = {}
    
    def get_provider_entity(self, entity_id: str) -> Entity:
        """
        Get a provider entity by entity_id.
        Loads from database on first access and caches for subsequent calls.
        
        Args:
            entity_id: The entity_id of the provider (e.g., "USCorePractitionerRole002")
            
        Returns:
            Entity object parsed from the database
            
        Raises:
            ValueError: If provider entity not found in database
        """
        # Check cache first
        if entity_id in self._cache:
            logger.debug(f"Provider entity {entity_id} found in cache")
            return self._cache[entity_id]
        
        # Query database
        logger.debug(f"Loading provider entity {entity_id} from database")
        provider = self.db.query(ProviderEntity).filter(
            ProviderEntity.entity_id == entity_id
        ).first()
        
        if not provider:
            raise ValueError(f"Provider entity '{entity_id}' not found in database")
        
        # Parse JSON and convert to Entity model
        entity_data = json.loads(provider.entity_json)
        entity = Entity.model_validate(entity_data)
        
        # Cache for future use
        self._cache[entity_id] = entity
        logger.debug(f"Cached provider entity {entity_id}")
        
        return entity
    
    def clear(self):
        """Clear the cache"""
        self._cache.clear()
        logger.debug("Provider cache cleared")
    
    def get_cache_size(self) -> int:
        """Get the number of cached providers"""
        return len(self._cache)