
from app.utils import execution_time
from app.handlers import MoodHandler, ToxicHandler, ToxicModel, MoodModel, NatashaHandler, NatashaModel
from app.models import OutputItemModel, OutputItemsModel, BaseOutputModel


@execution_time
def process_with_string(text: str, filters: list) -> OutputItemModel:
    mood: MoodModel = MoodHandler.get_analyze(data=text)
    toxic: ToxicModel = ToxicHandler.get_analyze(data=text)
    natasha: NatashaModel = NatashaHandler.get_analyze(data=text, filters=filters)
    return OutputItemModel(**mood.dict(), **toxic.dict(), **natasha.dict())


@execution_time
def process_with_list(data: list) -> OutputItemsModel:
    toxic: list[ToxicModel] = ToxicHandler.get_analyze(data=data)
    mood: list[MoodModel] = MoodHandler.get_analyze(data=data)
    return OutputItemsModel(results=[BaseOutputModel(**mood_model.dict(), **toxic_model.dict()) for mood_model, toxic_model in zip(mood, toxic)])

