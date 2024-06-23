import time
from pydantic import BaseModel
import re
import string


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


def remove_emojis_and_punctuation(text):
    """
    Удаляет смайлики и знаки пунктуации из текста.

    Параметры:
    ----------
    text : str
        Текст для обработки.

    Возвращает:
    ----------
    str
        Текст без смайликов и знаков пунктуации.
    """
    # Удаляем смайлики
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # смайлики лиц
                               u"\U0001F300-\U0001F5FF"  # символы и пиктограммы
                               u"\U0001F680-\U0001F6FF"  # транспорт и символы
                               u"\U0001F700-\U0001F77F"  # дополнительные символы и пиктограммы
                               u"\U0001F780-\U0001F7FF"  # еще больше символов и пиктограмм
                               u"\U0001F800-\U0001F8FF"  # другое
                               u"\U0001F900-\U0001F9FF"  # еще немного символов
                               u"\U0001FA00-\U0001FA6F"  # пиктограммы и символы
                               u"\U0001FA70-\U0001FAFF"  # доп. символы и пиктограммы
                               u"\U00002702-\U000027B0"  # разные символы
                               u"\U000024C2-\U0001F251"  # другие символы
                               "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)

    # Удаляем знаки пунктуации
    text = text.translate(str.maketrans('', '', string.punctuation))

    return text
