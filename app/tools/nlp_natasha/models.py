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
    natasha_model_count_tokens: int


class NatashaModel(BaseModel):
    artifacts: NatashaArtifactsModel
    filters: NatashaWordFiltersModel
    meaningful: bool
    natasha_model_count_tokens: int

