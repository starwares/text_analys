from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel


class NlpToolDostoevsky:
    """
        Класс для анализа текста с использованием модели FastTextSocialNetworkModel из библиотеки Dostoevsky.

        Атрибуты:
        ----------
        model : FastTextSocialNetworkModel
            Экземпляр модели FastTextSocialNetworkModel для анализа текста.

        """

    __instance = {}
    model = FastTextSocialNetworkModel(tokenizer=RegexTokenizer())

    def __new__(cls):
        """
                Возвращает единственный экземпляр класса NlpToolDostoevsky.

                Используется паттерн Singleton для создания единственного экземпляра класса.

                Возвращает:
                ----------
                NlpToolDostoevsky
                    Единственный экземпляр класса NlpToolDostoevsky.
                """

        if not hasattr(cls, 'instance'):
            cls.instance = super(NlpToolDostoevsky, cls).__new__(cls)
        return cls.__instance

    @classmethod
    def analyze_str(cls, text: str, k=5):
        """
                Анализирует одиночный текст на предмет социальных аспектов.

                Параметры:
                ----------
                text : str
                    Текст для анализа.
                k : int, optional
                    Количество наиболее вероятных классов для возврата (по умолчанию 5).

                Возвращает:
                ----------
                dict
                    Словарь с результатами анализа, содержащий вероятности для каждого класса.
                """

        return cls.model.predict([text], k)[0]

    @classmethod
    def analyze_list(cls, data: list, k=5):
        """
                Анализирует список текстов на предмет социальных аспектов.

                Параметры:
                ----------
                data : list
                    Список текстов для анализа.
                k : int, optional
                    Количество наиболее вероятных классов для возврата (по умолчанию 5).

                Возвращает:
                ----------
                list
                    Список словарей с результатами анализа для каждого текста, содержащий вероятности для каждого класса.
                """

        return cls.model.predict(data, k)


