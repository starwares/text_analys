import re
from concurrent.futures import ThreadPoolExecutor
from natasha import NewsNERTagger, Doc, NewsEmbedding, Segmenter, NewsMorphTagger, NewsSyntaxParser, MorphVocab, \
    DatesExtractor, AddrExtractor
from app.tools.nlp_natasha.models import NatashaArtifactsModel, NatashaMeaningfulModel, NatashaWordFiltersModel
from app.utils import remove_emojis_and_punctuation


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

    def __init__(self, text):

        """
        Инициализирует, и выполняет обработку текста :

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
        self.text = text

        self.doc = Doc(self.text)
        self.doc.segment(NlpToolNatasha.segmenter)
        self.doc.parse_syntax(NlpToolNatasha.syntax_parser)
        self.doc.tag_ner(NlpToolNatasha.ner_tagger)
        self.doc.tag_morph(NlpToolNatasha.morph_tagger)

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

    def artifacts(self) -> NatashaArtifactsModel:
        """
            Метод для извлечения артефактов из текста, таких как именованные сущности,
            даты, адреса, телефоны, электронные адреса и ссылки.

            Args:
                text (str): Текст для анализа.

            Returns:
                NatashaArtifactsModel: извлеченные артефакты из текста
            """

        # Параллельная нормализация span'ов
        with ThreadPoolExecutor() as executor:
            executor.map(lambda span: span.normalize(NlpToolNatasha.morph_vocab), self.doc.spans)

        # Более эффективная генерация записей с использованием списковых включений
        result = {record.type: set(record.normal for record in self.doc.spans if record.type) for record in self.doc.spans}

        # Параллельное извлечение дат и адресов
        with ThreadPoolExecutor() as executor:
            result["DATES"] = list(executor.map(lambda x: x.fact, NlpToolNatasha.dates_extractor(self.text)))
            result["ADDR"] = list(executor.map(lambda x: x.fact, NlpToolNatasha.address_extractor(self.text)))

        result["PHONES"] = NlpToolNatasha._extract_phone_numbers(self.text)
        result["EMAILS"] = NlpToolNatasha._extract_emails(self.text)
        result["LINKS"] = NlpToolNatasha._extract_urls(self.text)

        result = {key: value for key, value in result.items() if value}

        return NatashaArtifactsModel(**result)

    def word_filters(self, filters: list) -> NatashaWordFiltersModel:
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
            doc_for_filter = NlpToolNatasha(word).doc

            for token in doc_for_filter.tokens:
                token.lemmatize(NlpToolNatasha.morph_vocab)

            forbidden_lemmas.append(doc_for_filter.tokens[0].lemma)

        for token in self.doc.tokens:
            token.lemmatize(NlpToolNatasha.morph_vocab)

        forbidden = []

        for token in self.doc.tokens:
            if token.lemma in forbidden_lemmas:
                forbidden.append(token.text)

        return NatashaWordFiltersModel(passed=len(forbidden) == 0, tokens=set(forbidden))

    def meaningful_text(self) -> NatashaMeaningfulModel:
        """
        Метод для проверки, на смысловое предложение.

        Args:
            text (str): Текст для проверки.

        Returns:
            NatashaMeaningfulModel: True, если текст содержит смысловые слова, False в противном случае.
        """

        # Фильтрация известных слов и символов, убираем все дублирующиеся слова
        known_words = set([token.text for token in self.doc.tokens if NlpToolNatasha.morph_vocab.word_is_known(token.text)])

        # длина текста без знаков пунктуации и эмоджи, убираем все дублирующиеся слова
        len_text = len(set(remove_emojis_and_punctuation(self.text).split()))

        # Проверка что известных слов не меньше трех, и  количества значимых слов (простая эвристика) больше 70
        # процентов текста
        if len(known_words) < 3 or len(known_words) > len_text * 0.7:
            return NatashaMeaningfulModel(meaningful=False, natasha_model_count_tokens=len(self.doc.tokens))

        return NatashaMeaningfulModel(meaningful=True, natasha_model_count_tokens=len(self.doc.tokens))

