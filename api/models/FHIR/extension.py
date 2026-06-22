from typing import Any, Dict, Optional
from pydantic import Field
from api.models.no_null_camel_model import NoNullCamelModel

class Extension(NoNullCamelModel):
    """
    FHIR Extension data type.
    
    Optional Extensions Element - found in all resources.
    """
    
    url: str = Field(..., description="Identifies the meaning of the extension")
    
    # Value[x] - only one of these should be set
    value: Optional[str] = Field(None, description="Value of extension")
    value_string: Optional[str] = Field(None, description="Value of extension")
    value_boolean: Optional[bool] = Field(None, description="Value of extension")
    value_integer: Optional[int] = Field(None, description="Value of extension")
    value_decimal: Optional[float] = Field(None, description="Value of extension")
    value_uri: Optional[str] = Field(None, description="Value of extension")
    value_url: Optional[str] = Field(None, description="Value of extension")
    value_code: Optional[str] = Field(None, description="Value of extension")
    value_date: Optional[str] = Field(None, description="Value of extension")
    value_date_time: Optional[str] = Field(None, description="Value of extension")
    value_codeable_concept: Optional[Dict[str, Any]] = Field(None, description="Value of extension")
    value_coding: Optional[Dict[str, Any]] = Field(None, description="Value of extension")
    value_reference: Optional[Dict[str, Any]] = Field(None, description="Value of extension")
    
    # Nested extensions (for complex extensions)
    extension: Optional[list['Extension']] = Field(None, description="Additional content defined by implementations")
    
    model_config = {"extra": "allow"}
    
    # @model_validator(mode='after')
    # def validate_value_choice(self) -> 'Extension':
        # """Validate that either a value[x] OR nested extensions are present, not both."""
        # value_fields = [
        #     self.value_string, self.value_boolean, self.value_integer, 
        #     self.value_decimal, self.value_uri, self.value_url,
        #     self.value_code, self.value_date, self.value_date_time,
        #     self.value_codeable_concept, self.value_coding, self.value_reference, self.value
        # ]
        
        # has_value = any(v is not None for v in value_fields)
        # has_nested = self.extension is not None and len(self.extension) > 0
        
        # if not has_value and not has_nested:
        #     raise ValueError('Extension must have either a value[x] or nested extensions')
        
        # if has_value and has_nested:
        #     raise ValueError('Extension cannot have both a value[x] and nested extensions')
        
        # # Check only one value[x] is set
        # if sum(v is not None for v in value_fields) > 1:
        #     raise ValueError('Only one value[x] field can be set in an extension')
        
        # return self
    
    def get_value(self) -> Optional[Any]:
        """Get the value regardless of which value[x] field is set."""
        value_fields = [
            'value_string', 'value_boolean', 'value_integer', 'value_decimal',
            'value_uri', 'value_url', 'value_code', 'value_date', 'value_date_time',
            'value_codeable_concept', 'value_coding', 'value_reference', "value"
        ]
        
        for field in value_fields:
            value = getattr(self, field)
            if value is not None:
                return value
        return None