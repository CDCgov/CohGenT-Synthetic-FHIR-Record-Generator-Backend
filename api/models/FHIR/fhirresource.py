# NOTE: This file is for basic typing to format output only. It should not be considered a true representation of a FHIR Resource.

from api.models.no_null_camel_model import NoNullCamelModel
from pydantic import ConfigDict

class FHIRResource(NoNullCamelModel):
    """
    FHIR Resource with strict typing on resourceType.
    All other fields allowed via extra='allow'.
    """
    model_config = ConfigDict(extra='allow')

    resource_type: str