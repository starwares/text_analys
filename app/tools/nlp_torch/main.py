from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


# Установка количества потоков
torch.set_num_threads(4)


class NlpToolTorch:
    """
    Класс для обработки текста и предсказания вероятностей с использованием модели Transformer.

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

        #Квантование модели для ускорения инференса
        self.model = torch.quantization.quantize_dynamic(
            self.model, {torch.nn.Linear}, dtype=torch.qint8)

    def predict_probabilities(self, text):
        """
        Предсказывает вероятности для текста или списка текстов.

        Параметры:
        ----------
        text : str или list
            Текст или список текстов для предсказания.

        Возвращает:
        ----------
        tuple
            - numpy.ndarray или list of numpy.ndarray: Вероятности для каждого текста.
            - int: Количество токенов в тексте.
        """

        if isinstance(text, str):
            proba, num_tokens = self._split_for_token(text=text)
            return proba, num_tokens
        elif isinstance(text, list):
            num_tokens = 0
            all_proba = []
            for item in text:
                item_result, num_tokens = self._split_for_token(text=item)
                all_proba.append(item_result)
            return all_proba, num_tokens

    def _process_chunk(self, text: str):
        """
        Обрабатывает один фрагмент текста и возвращает вероятности .

        Параметры:
        ----------
        text : str
            Фрагмент текста для обработки.

        Возвращает:
        ----------
        numpy.ndarray
            Вероятности для фрагмента текста.
        """

        with torch.no_grad():
            inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True).to(self.model.device)
            proba = torch.sigmoid(self.model(**inputs).logits).cpu().numpy()
            proba = proba[0]
            return proba

    def _split_for_token(self, text: str, max_length=112):
        """
        Разбивает текст на фрагменты, если он превышает максимальную длину, и предсказывает вероятности для каждого фрагмента.

        Параметры:
        ----------
        text : str
            Текст для обработки.
        max_length : int, optional
            Максимальная длина текста в токенах (по умолчанию 112).

        Возвращает:
        ----------
        tuple
            - numpy.ndarray или list of numpy.ndarray: Вероятности для текста.
            - int: Количество токенов в тексте.
        """

        tokens = self.tokenizer.encode(text)
        num_tokens = len(tokens)

        if num_tokens <= max_length:

            return self._process_chunk(text), num_tokens
        else:
            num_chunks = (num_tokens + max_length - 1) // max_length  # Вычисляем количество частей
            chunk_size = num_tokens // num_chunks  # Определяем размер каждой части
            remainder = num_tokens % num_chunks  # Оставшийся остаток

            # Определяем индексы для деления
            split_indices = []
            start = 0
            for i in range(num_chunks):
                end = start + chunk_size + (1 if i < remainder else 0)
                split_indices.append((start, end))
                start = end

            chunks = [tokens[start:end] for start, end in split_indices]
            chunk_texts = [self.tokenizer.decode(chunk, skip_special_tokens=True) for chunk in chunks]

            proba = [self._process_chunk(chunk_text) for chunk_text in chunk_texts]

            return proba, num_tokens
