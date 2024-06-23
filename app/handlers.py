from app.tools.nlp_dostoevsky.main import NlpToolDostoevsky
from app.tools.nlp_natasha.main import NlpToolNatasha
from app.tools.nlp_torch.main import NlpToolTorch
from app.tools.nlp_torch.models import ToxicContentModel, ToxicModel
from app.tools.nlp_dostoevsky.models import MoodContentModel, MoodModel
from app.tools.nlp_natasha.models import NatashaModel


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

    nlp_dostoevsky = NlpToolDostoevsky

    @staticmethod
    def _get_analyze_from_str(text: str, **kwargs) -> MoodModel:
        return MoodModel(mood=MoodContentModel(**MoodHandler.nlp_dostoevsky.analyze_str(text)))

    @staticmethod
    def _get_analyze_from_list(data: list, **kwargs) -> list[MoodModel]:
        result: list = []
        proba = MoodHandler.nlp_dostoevsky.analyze_list(data)
        for pr in proba:
            result.append(MoodModel(mood=MoodContentModel(**pr)))
        return result


class ToxicHandler(Handler):
    """
        Класс для обработки и анализа токсичности текста с использованием модели Transformer.

        Атрибуты:
        ----------
        nlp_torch_toxic : NlpToolTorch
            Экземпляр класса NlpToolTorch, инициализированный с использованием модели 'cointegrated/rubert-tiny-toxicity'.
        """

    nlp_torch_toxic = NlpToolTorch('cointegrated/rubert-tiny-toxicity')

    @staticmethod
    def _data_averaging(data: list, toxicity_count_tokens: int):
        """
        Усредняет данные по токсичности для списка вероятностей и возвращает итоговую модель токсичности.

        Параметры:
        ----------
        data : list
            Список вероятностей токсичности.
        toxicity_count_tokens : int
            Количество токенов, использованных в анализе токсичности.

        Возвращает:
        ----------
        ToxicModel
            Итоговая модель токсичности.
        """

        result_toxic_model = None
        for item in data:
            res = item.tolist()
            if not result_toxic_model:
                result_toxic_model = ToxicModel(toxicity=ToxicContentModel.from_list(res),
                                                toxicity_count_tokens=toxicity_count_tokens)
            toxic_model = ToxicModel(toxicity=ToxicContentModel.from_list(res),
                                     toxicity_count_tokens=toxicity_count_tokens)
            if toxic_model.toxicity.insult > result_toxic_model.toxicity.insult:
                result_toxic_model.toxicity.insult = toxic_model.toxicity.insult
            if toxic_model.toxicity.dangerous > result_toxic_model.toxicity.dangerous:
                result_toxic_model.toxicity.dangerous = toxic_model.toxicity.dangerous

            result_toxic_model.toxicity.obscenity = (result_toxic_model.toxicity.obscenity
                                                     + toxic_model.toxicity.obscenity) / 2
            result_toxic_model.toxicity.threat = (result_toxic_model.toxicity.threat + toxic_model.toxicity.threat) / 2
        result_toxic_model.toxicity.non_toxic = 1 - result_toxic_model.toxicity.insult
        return result_toxic_model

    @staticmethod
    def _get_analyze_from_str(text: str, **kwargs) -> ToxicModel:

        proba, toxicity_count_tokens = ToxicHandler.nlp_torch_toxic.predict_probabilities(text)
        if isinstance(proba, list):
            return ToxicHandler._data_averaging(proba, toxicity_count_tokens)
        data = proba.tolist()
        return ToxicModel(toxicity=ToxicContentModel.from_list(data), toxicity_count_tokens=toxicity_count_tokens)

    @staticmethod
    def _get_analyze_from_list(data: list, **kwargs) -> list[ToxicModel]:
        result: list = []
        proba, toxicity_count_tokens = ToxicHandler.nlp_torch_toxic.predict_probabilities(data)
        for pr in proba:
            if isinstance(pr, list):
                result.append(ToxicHandler._data_averaging(pr, toxicity_count_tokens))
            else:
                res = pr.tolist()
                result.append(ToxicModel(toxicity=ToxicContentModel.from_list(res),
                                         toxicity_count_tokens=toxicity_count_tokens))
        return result


class NatashaHandler(Handler):

    @staticmethod
    def _get_analyze_from_str(text: str, filters=None) -> NatashaModel:
        nlp_natasha = NlpToolNatasha(text)
        if filters is None:
            filters = []

        return NatashaModel(artifacts=nlp_natasha.artifacts(), filters=nlp_natasha.word_filters(filters),
                            **nlp_natasha.meaningful_text().dict())

    @staticmethod
    def _get_analyze_from_list(data: list, **kwargs):
        raise ValueError("Не вызывается для списка")
