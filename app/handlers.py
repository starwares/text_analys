from app.tools.nlp_dostoevsky.main import NlpToolDostoevsky
from app.tools.nlp_natasha.main import NlpToolNatasha
from app.tools.nlp_torch.main import NlpToolTorch
from app.tools.nlp_torch.models import ToxicContentModel, ToxicModel
from app.tools.nlp_dostoevsky.models import MoodContentModel, MoodModel
from app.tools.nlp_natasha.models import NatashaModel

nlp_torch_toxic = NlpToolTorch('cointegrated/rubert-tiny-toxicity')
nlp_dostoevsky = NlpToolDostoevsky
nlp_natasha = NlpToolNatasha


class Handler:
    """
        Класс, предоставляющий методы для анализа данных, включая обработку строк и списков.

        Methods:
            get_analyze(data: str | list) -> Any:
                Вызывает соответствующий метод в зависимости от типа данных (строка или список).

        Static Methods:
            _get_analyze_from_str(text: str) -> Any:
                Внутренний статический метод для анализа данных типа str.

            _get_analyze_from_list(data: list) -> Any:
                Внутренний статический метод для анализа данных типа list.
        """

    @staticmethod
    def _get_analyze_from_str(text: str, **kwargs):
        """
        Внутренний статический метод для анализа данных типа str.

        Args:
            text (str): Входной текст для анализа.

        Returns:
            Any: Результат анализа данных.
        """

        # Ваша логика обработки данных типа str
        pass

    @staticmethod
    def _get_analyze_from_list(data: list, **kwargs):
        """
        Внутренний статический метод для анализа данных типа list.

        Args:
            data (list): Входной список для анализа.

        Returns:
            Any: Результат анализа данных.
        """

        # Ваша логика обработки данных типа list
        pass

    @classmethod
    def get_analyze(cls, data: str | list, **kwargs):
        """
        Вызывает соответствующий метод в зависимости от типа данных (строка или список).

        Args:
            data (str | list): Входные данные для анализа.

        Returns:
            Any: Результат анализа данных.
        """

        if isinstance(data, str):
            return cls._get_analyze_from_str(data, **kwargs)
        else:
            return cls._get_analyze_from_list(data, **kwargs)


class MoodHandler(Handler):

    @staticmethod
    def _get_analyze_from_str(text: str, **kwargs) -> MoodModel:
        return MoodModel(mood=MoodContentModel(**nlp_dostoevsky.analyze_str(text)))

    @staticmethod
    def _get_analyze_from_list(data: list, **kwargs) -> list[MoodModel]:
        result: list = []
        proba = nlp_dostoevsky.analyze_list(data)
        for pr in proba:
            result.append(MoodModel(mood=MoodContentModel(**pr)))
        return result


class ToxicHandler(Handler):

    @staticmethod
    def _get_analyze_from_str(text: str, **kwargs) -> ToxicModel:
        proba = nlp_torch_toxic.predict_probabilities(text)
        data = proba.tolist()
        return ToxicModel(toxicity=ToxicContentModel.from_list(data))

    @staticmethod
    def _get_analyze_from_list(data: list, **kwargs) -> list[ToxicModel]:
        result: list = []
        proba = nlp_torch_toxic.predict_probabilities(data)
        for pr in proba:
            res = pr.tolist()
            result.append(ToxicModel(toxicity=ToxicContentModel.from_list(res)))
        return result


class NatashaHandler(Handler):

    @staticmethod
    def _get_analyze_from_str(text: str, filters=None) -> NatashaModel:

        if filters is None:
            filters = []

        return NatashaModel(artifacts=nlp_natasha.artifacts(text), filters=nlp_natasha.word_filters(text, filters),
                            **nlp_natasha.meaningful_text(text).dict())

    @staticmethod
    def _get_analyze_from_list(data: list, **kwargs):
        raise ValueError("Не вызывается для списка")
