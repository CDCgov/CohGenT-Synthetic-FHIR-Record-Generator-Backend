import json
from pathlib import Path
from sqlalchemy.orm import Session
from api.database.db_other_tables import ProviderEntity
from loguru import logger


def seed_provider_entities(db: Session, force_reseed: bool = False):
    """Seed provider entities from JSON5 files"""
    
    # Check if data already exists
    existing_count = db.query(ProviderEntity).count()
    if existing_count > 0 and not force_reseed:
        logger.info(f"Provider entities already loaded ({existing_count} records), skipping...")
        return existing_count
    
    # Clear existing data if forcing reseed
    if force_reseed and existing_count > 0:
        logger.warning(f"Force reseed enabled - deleting {existing_count} existing provider entities")
        db.query(ProviderEntity).delete()
        db.commit()
    
    # Load all provider entity files
    provider_dir = Path(__file__).parent.parent.parent / "data" / "providerentities"
    provider_files = list(provider_dir.glob("*.json5"))
    
    providers = []
    errors = []
    
    for filepath in provider_files:
        if filepath.name == "README.md":
            continue
        
        try:
            # Read JSON5 file (strip comments)
            with open(filepath, 'r') as f:
                content = f.read()
                # Simple JSON5 to JSON conversion (remove comment lines)
                lines = [line for line in content.split('\n') 
                        if not line.strip().startswith('//')]
                json_content = '\n'.join(lines)
                entity_data = json.loads(json_content)
            
            # Extract display name from fields
            display_name = entity_data.get('entityId', 'Unknown')
            resource_type = entity_data.get('resourceType', '')
            
            # For Practitioners, build full name from given and family
            if resource_type == 'Practitioner':
                given_name = None
                family_name = None
                for field in entity_data.get('fields', []):
                    path = field.get('path', '')
                    if 'name.[0].given.[0]' in path:
                        given_name = field.get('value')
                    elif 'name.[0].family' in path:
                        family_name = field.get('value')
                
                if given_name and family_name:
                    display_name = f"{given_name} {family_name}"
                elif family_name:
                    display_name = family_name
                elif given_name:
                    display_name = given_name
            
            # For Organizations, look for .name field
            elif resource_type == 'Organization':
                for field in entity_data.get('fields', []):
                    path = field.get('path', '')
                    if path.endswith('.name') and field.get('value'):
                        display_name = str(field.get('value'))
                        break
            
            # For other resources, look for any name-related field
            else:
                for field in entity_data.get('fields', []):
                    path = field.get('path', '')
                    if 'name' in path.lower() and field.get('value'):
                        display_name = str(field.get('value'))
                        break
            
            provider = ProviderEntity(
                entity_id=entity_data['entityId'],
                resource_type=entity_data['resourceType'],
                display_name=display_name,
                entity_json=json.dumps(entity_data)
            )
            
            providers.append(provider)
            logger.debug(f"Loaded provider: {entity_data['entityId']}")
            
        except Exception as e:
            errors.append(f"{filepath.name}: {str(e)}")
            logger.error(f"Error loading {filepath.name}: {e}")
    
    # Report errors
    if errors:
        logger.error(f"Found {len(errors)} errors while loading providers:")
        for error in errors[:5]:  # Show first 5 errors
            logger.error(f"  - {error}")
        if len(errors) > 5:
            logger.error(f"  ... and {len(errors) - 5} more errors")
    
    # Insert valid records
    if providers:
        try:
            db.add_all(providers)
            db.commit()
            logger.info(f"✓ Successfully loaded {len(providers)} provider entities")
            return len(providers)
        except Exception as e:
            db.rollback()
            logger.error(f"Database error while loading providers: {e}")
            raise
    else:
        logger.warning("No valid provider entities found to load")
        return 0