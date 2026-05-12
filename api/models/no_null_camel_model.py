from fastapi_camelcase import CamelModel
from pydantic import model_serializer
from typing import Any, Dict
from datetime import datetime

class NoNullCamelModel(CamelModel):
    """Base model that excludes None values in JSON and properly outputs dates as ISO strings."""
    @model_serializer(mode='wrap', when_used='json')
    def _exclude_none(self, serializer: Any, info: Any) -> Dict[str, Any]:
        data = serializer(self)
        return {
            k: v.isoformat() if isinstance(v, datetime) else v 
            for k, v in data.items() 
            if v is not None
        }