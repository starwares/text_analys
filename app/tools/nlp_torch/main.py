from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


# Установка количества потоков
torch.set_num_threads(4)


class NlpToolTorch:
    """
        Класс для обработки текста и предсказания вероятностей токсичности с использованием модели Transformer.

        Атрибуты:
        ----------
        model_name_or_path : str
            Имя модели или путь к модели, используемой для предсказаний.
        tokenizer : AutoTokenizer
            Токенизатор, используемый для преобразования текста в токены.
        model : AutoModelForSequenceClassification
            Модель для классификации последовательностей, используемая для предсказаний.
        """

    def __init__(self, model_name_or_path):
        """
                Инициализирует экземпляр класса NlpToolTorch с заданной моделью.

                Параметры:
                ----------
                model_name_or_path : str
                    Имя модели или путь к модели, используемой для предсказаний.
                """

        self.model_name_or_path = model_name_or_path
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name_or_path)
        self.model.eval()

        # Квантование модели для ускорения инференса
        self.model = torch.quantization.quantize_dynamic(
            self.model, {torch.nn.Linear}, dtype=torch.qint8
        )

    def predict_probabilities(self, text):
        """
                Предсказывает вероятности токсичности для текста или списка текстов.

                Параметры:
                ----------
                text : str или list
                    Текст или список текстов для предсказания.

                Возвращает:
                ----------
                numpy.ndarray или list of numpy.ndarray
                    Вероятности токсичности для каждого текста.
                """

        if isinstance(text, str):
            proba = self._split_for_token(text=text)
            return proba
        elif isinstance(text, list):
            all_proba = []
            for item in text:
                all_proba.append(self._split_for_token(text=item))
            return  all_proba

    def _process_chunk(self, text: str):
        """
                Обрабатывает один фрагмент текста и возвращает вероятности токсичности.

                Параметры:
                ----------
                text : str
                    Фрагмент текста для обработки.

                Возвращает:
                ----------
                numpy.ndarray
                    Вероятности токсичности для фрагмента текста.
                """

        with torch.no_grad():
            inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True).to(self.model.device)
            proba = torch.sigmoid(self.model(**inputs).logits).cpu().numpy()
            proba = proba[0]
            return proba

    def _split_for_token(self, text: str, max_length=512):
        """
                Разбивает текст на фрагменты, если он превышает максимальную длину, и предсказывает вероятности для каждого фрагмента.

                Параметры:
                ----------
                text : str
                    Текст для обработки.
                max_length : int, optional
                    Максимальная длина текста в токенах (по умолчанию 512).

                Возвращает:
                ----------
                numpy.ndarray
                    Усредненные вероятности токсичности для текста.
                """

        if len(self.tokenizer.encode(text)) <= max_length:
            return self._process_chunk(text)
        else:
            chunks = [text[i:i + max_length] for i in range(0, len(text), max_length)]
            proba = sum([self._process_chunk(chunk) for chunk in chunks]) / len(chunks)
            return proba

