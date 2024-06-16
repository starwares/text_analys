import time
from pydantic import BaseModel


def execution_time(func):
    """
        Декоратор для измерения времени выполнения функции и добавления атрибута execution к возвращаемому результату.

        Args:
            func (callable): Функция, время выполнения которой нужно измерить.

        Returns:
            callable: Обёртка вокруг функции, добавляющая атрибут execution к результату.
        """

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        result.execution = str((time.time() - start_time) * 1000) + ' ms'
        return result

    return wrapper


def calculate_average(models: list[BaseModel]) -> dict:
    """
        Вычисляет среднее значение для списка моделей.

        Args:
            models (list[BaseModel]): Список моделей, для которых нужно вычислить среднее.

        Returns:
            dict: Словарь со средними значениями по полям моделей.
        """

    result = None
    model: BaseModel
    for model in models:
        if not result:
            result = model.dict()
        else:
            for field_name, field_type in model.__annotations__.items():
                result[field_name] += getattr(model, field_name)

    for key, value in result.items():
        result[key] = value / len(models)
    return result
