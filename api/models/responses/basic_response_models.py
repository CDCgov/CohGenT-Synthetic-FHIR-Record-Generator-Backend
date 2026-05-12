from api.models.no_null_camel_model import NoNullCamelModel
from api.models.use_case import UseCase

class FeatureStatus(NoNullCamelModel):
    terminology_search: str

class InfoResponse(NoNullCamelModel):
    application: str
    version: str
    features: FeatureStatus

class UseCaseCollectionResponse(NoNullCamelModel):
    count: int
    use_cases: list[UseCase]