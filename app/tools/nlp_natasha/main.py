import re
from concurrent.futures import ThreadPoolExecutor
from natasha import NewsNERTagger, Doc, NewsEmbedding, Segmenter, NewsMorphTagger, NewsSyntaxParser, MorphVocab, \
    DatesExtractor, AddrExtractor
from app.tools.nlp_natasha.models import NatashaArtifactsModel, NatashaMeaningfulModel, NatashaWordFiltersModel


class NlpToolNatasha:
    """
        Класс предоставляет инструменты для обработки текста на русском языке с использованием библиотеки Natasha.

        Атрибуты:
            embedding (NewsEmbedding): Модель эмбеддингов для новостей.
            segmenter (Segmenter): Сегментатор текста.
            morph_tagger (NewsMorphTagger): Морфологический тэггер.
            morph_vocab (MorphVocab): Морфологический словарь.
            ner_tagger (NewsNERTagger): Тэггер именованных сущностей.
            syntax_parser (NewsSyntaxParser): Синтаксический парсер.
            dates_extractor (DatesExtractor): Экстрактор дат.
            address_extractor (AddrExtractor): Экстрактор адресов.
        """

    __instance = {}
    embedding = NewsEmbedding()
    segmenter = Segmenter()
    morph_tagger = NewsMorphTagger(embedding)
    morph_vocab = MorphVocab()
    ner_tagger = NewsNERTagger(embedding)
    syntax_parser = NewsSyntaxParser(embedding)
    dates_extractor = DatesExtractor(morph_vocab)
    address_extractor = AddrExtractor(morph_vocab)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(NlpToolNatasha, cls).__new__(cls)
        return cls.__instance

    @classmethod
    def _process_order_first(cls, text) -> Doc:
        """
        Выполняет обработку текста согласно первому порядку:
        1. Создает объект Doc для текста.
        2. Сегментирует текст.
        3. Морфологический анализ.

        Args:
            text (str): Текст для обработки.

        Returns:
            Doc: Объект Doc с выполненными этапами обработки.
        """

        doc = Doc(text)
        doc.segment(cls.segmenter)
        doc.tag_morph(cls.morph_tagger)
        return doc

    @classmethod
    def _process_order_second(cls, text) -> Doc:
        """
        Выполняет обработку текста согласно второму порядку:
        1. Создает объект Doc для текста.
        2. Сегментирует текст.
        3. Синтаксический анализ.
        4. Распознавание именованных сущностей.
        5. Морфологический анализ.

        Args:
            text (str): Текст для обработки.

        Returns:
            Doc: Объект Doc с выполненными этапами обработки.
        """

        doc = Doc(text)
        doc.segment(cls.segmenter)
        doc.parse_syntax(cls.syntax_parser)
        doc.tag_ner(cls.ner_tagger)
        doc.tag_morph(cls.morph_tagger)
        return doc

    @staticmethod
    def _extract_phone_numbers(text):
        phone_numbers = re.findall(r'\+?\d{1,3}[\s\d\-()]+\d{2,3}[\s\d\-()]+\d{2,3}', text)
        return phone_numbers

    @staticmethod
    def _extract_emails(text):
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        return emails

    @staticmethod
    def _extract_urls(text):
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        return urls

    @classmethod
    def artifacts(cls, text: str) -> NatashaArtifactsModel:
        """
            Метод для извлечения артефактов из текста, таких как именованные сущности,
            даты, адреса, телефоны, электронные адреса и ссылки.

            Args:
                text (str): Текст для анализа.

            Returns:
                NatashaArtifactsModel: извлеченные артефакты из текста
            """

        doc = cls._process_order_second(text)

        # Параллельная нормализация span'ов
        with ThreadPoolExecutor() as executor:
            executor.map(lambda span: span.normalize(cls.morph_vocab), doc.spans)

        # Более эффективная генерация записей с использованием списковых включений
        result = {record.type: set(record.normal for record in doc.spans if record.type) for record in doc.spans}

        # Параллельное извлечение дат и адресов
        with ThreadPoolExecutor() as executor:
            result["DATES"] = list(executor.map(lambda x: x.fact, cls.dates_extractor(text)))
            result["ADDR"] = list(executor.map(lambda x: x.fact, cls.address_extractor(text)))

        result["PHONES"] = cls._extract_phone_numbers(text)
        result["EMAILS"] = cls._extract_emails(text)
        result["LINKS"] = cls._extract_urls(text)

        result = {key: value for key, value in result.items() if value}

        return NatashaArtifactsModel(**result)

    @classmethod
    def word_filters(cls, text: str, filters: list) -> NatashaWordFiltersModel:
        """
            Метод для фильтрации текста на основе заданных фильтров по леммам.

            Args:
                text (str): Текст для фильтрации.
                filters (list): Список фильтров.

            Returns:
                NatashaWordFiltersModel: Результат фильтрации, содержащий информацию о прохождении и непрошедших токенах.
            """

        forbidden_lemmas = []
        for word in filters:
            doc = cls._process_order_second(word)

            for token in doc.tokens:
                token.lemmatize(cls.morph_vocab)

            forbidden_lemmas.append(doc.tokens[0].lemma)

        doc = cls._process_order_second(text)

        for token in doc.tokens:
            token.lemmatize(cls.morph_vocab)

        forbidden = []

        for token in doc.tokens:
            if token.lemma in forbidden_lemmas:
                forbidden.append(token.text)

        return NatashaWordFiltersModel(passed=len(forbidden) == 0, tokens=set(forbidden))

    @classmethod
    def meaningful_text(cls, text: str) -> NatashaMeaningfulModel:
        """
            Метод для проверки, содержит ли текст хотя бы одно смысловое слово.

            Args:
                text (str): Текст для проверки.

            Returns:
                NatashaMeaningfulModel: True, если текст содержит смысловые слова, False в противном случае.
            """

        words = text.split()
        for word in words:
            if any(cls.morph_vocab.word_is_known(w) for w in word.split()):
                return NatashaMeaningfulModel(meaningful=True)
        return NatashaMeaningfulModel(meaningful=False)
