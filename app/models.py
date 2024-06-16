from pydantic import BaseModel
from app.tools.nlp_natasha.models import NatashaModel
from app.tools.nlp_torch.models import ToxicModel, ToxicContentModel
from app.tools.nlp_dostoevsky.models import MoodModel, MoodContentModel
from app.utils import calculate_average


class InputItemModel(BaseModel):
    message: str
    filters: list = []

    class Config:
        schema_extra = {
            'example': {
                'message': 'Это пример для анализа текста',
                'filters': ['фильтр 1', 'Фильтр 2']
            }
        }


class InputItemsModel(BaseModel):
    messages: list
    filters: list = []

    class Config:
        schema_extra = {
            'example': {
                'messages': ['Это пример для анализа текста 1', 'Это пример для анализа текста 2'],
                'filters': ['фильтр 1', 'Фильтр 2']
            }
        }


class BaseOutputModel(ToxicModel, MoodModel):
    pass


class OutputItemModel(BaseOutputModel, NatashaModel):
    execution: str | None


class OutputItemsModel(BaseModel):
    results: list[BaseOutputModel]
    execution: str | None


class OutputAverageModel(BaseOutputModel):
    execution: str | None

    @classmethod
    def calculate_average(cls, mood: list[MoodContentModel],
                          toxicity: list[ToxicContentModel],
                          execution: str | None = None):
        calculate_moods = calculate_average(models=mood)
        calculate_toxics = calculate_average(models=toxicity)
        return cls(mood=MoodContentModel(**calculate_moods),
                   toxicity=ToxicContentModel(**calculate_toxics),
                   execution=execution)
