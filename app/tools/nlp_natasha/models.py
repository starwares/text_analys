from pydantic import BaseModel


class NatashaArtifactsModel(BaseModel):
    DATES: list = []
    ADDR: list = []
    PHONES: list = []
    LINKS: list = []


class NatashaWordFiltersModel(BaseModel):
    passed: bool
    tokens: list = []


class NatashaMeaningfulModel(BaseModel):
    meaningful: bool


class NatashaModel(BaseModel):
    artifacts: NatashaArtifactsModel
    filters: NatashaWordFiltersModel
    meaningful: bool

