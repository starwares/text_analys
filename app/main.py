import time

from app import create_app

from app.models import InputItemModel, InputItemsModel, OutputItemModel, OutputItemsModel, OutputAverageModel
from app.text_analysis import process_with_list, process_with_string


app = create_app()


@app.post("/", response_model=OutputItemModel, description="Получение результата для одного поста")
def get_item(data: InputItemModel):
    result: OutputItemModel = process_with_string(text=data.message, filters=data.filters)
    return result


@app.post("/collection", response_model=OutputItemsModel, description="Получение результата для коллекции постов")
def get_collection(data: InputItemsModel):
    result: OutputItemsModel = process_with_list(data=data.messages)
    return result


@app.post("/summary", response_model=OutputAverageModel, description="Получение усредненного результата для коллекции постов")
def get_summary(data: InputItemsModel):
    result: OutputItemsModel = process_with_list(data=data.messages)
    mood = [item_result.mood for item_result in result.results]
    toxicity = [item_result.toxicity for item_result in result.results]
    return OutputAverageModel.calculate_average(mood=mood, toxicity=toxicity, execution=result.execution)
