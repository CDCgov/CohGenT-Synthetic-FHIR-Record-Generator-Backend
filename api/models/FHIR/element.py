from api.models.no_null_camel_model import NoNullCamelModel
from api.models.FHIR.extension import Extension
from typing import Optional

class Element(NoNullCamelModel):
    id: Optional[str] = None
    extension: Optional[list[Extension]] = None