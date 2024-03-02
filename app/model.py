import re

import torch
from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel
from natasha import NewsNERTagger, Doc, NewsEmbedding, Segmenter, NewsMorphTagger, NewsSyntaxParser, MorphVocab, \
    DatesExtractor, AddrExtractor

from transformers import AutoTokenizer, AutoModelForSequenceClassification

model_checkpoint = 'cointegrated/rubert-tiny-toxicity'
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
model = AutoModelForSequenceClassification.from_pretrained(model_checkpoint)
if torch.cuda.is_available():
    model.cuda()

e = NewsEmbedding()
s = Segmenter()
vm = NewsMorphTagger(e)
vc = MorphVocab()
ner = NewsNERTagger(e)
syn = NewsSyntaxParser(e)

m = FastTextSocialNetworkModel(tokenizer=RegexTokenizer())

de = DatesExtractor(vc)
ae = AddrExtractor(vc)


def _mood(text: str):
    return m.predict([text], 5)[0]


def _toxicity(text: str):
    with torch.no_grad():
        inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True).to(model.device)
        p = torch.sigmoid(model(**inputs).logits).cpu().numpy()
    if isinstance(text, str):
        p = p[0]

    data = p.tolist()

    return {
        "non-toxic": float(format(data[0], '.3f')),
        "insult": float(format(data[1], '.3f')),
        "obscenity": float(format(data[2], '.3f')),
        "threat": float(format(data[3], '.3f')),
        "dangerous": float(format(data[4], '.3f')),
    }


def _extract_phone_numbers(text):
    phone_numbers = re.findall(r'\+?\d{1,3}[\s\d\-()]+\d{2,3}[\s\d\-()]+\d{2,3}', text)
    return phone_numbers


def _extract_emails(text):
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    return emails


def _extract_urls(text):
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    return urls


def _artifacts(text: str):
    doc = Doc(text)

    doc.segment(s)
    doc.parse_syntax(syn)
    doc.tag_ner(ner)
    doc.tag_morph(vm)

    for span in doc.spans:
        span.normalize(vc)

    result = {}

    for record in list(map(lambda x: {
        "text": x.normal,
        "type": x.type
    }, doc.spans)):
        if record["type"] not in result:
            result[record["type"]] = []

        result[record["type"]].append(record["text"])

    for k, v in result.items():
        result[k] = set(v)

    result["DATES"] = list(map(lambda x: x.fact, de(text)))
    result["ADDR"] = list(map(lambda x: x.fact, ae(text)))
    result["PHONES"] = _extract_phone_numbers(text)
    result["EMAILS"] = _extract_emails(text)
    result["LINKS"] = _extract_urls(text)

    result = {key: value for key, value in result.items() if value}

    return result


def _word_filters(text: str, filters: list):

    forbidden_lemmas = []
    for word in filters:
        doc = Doc(word)
        doc.segment(s)
        doc.tag_morph(vm)

        for token in doc.tokens:
            token.lemmatize(vc)

        forbidden_lemmas.append(doc.tokens[0].lemma)

    doc = Doc(text)
    doc.segment(s)
    doc.tag_morph(vm)

    for token in doc.tokens:
        token.lemmatize(vc)

    forbidden = []

    for token in doc.tokens:
        if token.lemma in forbidden_lemmas:
            forbidden.append(token.text)

    return {
        "passed": len(forbidden) == 0,
        "tokens": set(forbidden),
    }


def _is_meaningful_text(text: str):
    words = text.split()
    for word in words:
        if any(vc.word_is_known(w) for w in word.split()):
            return True
    return False


def process(text: str, filters: list):
    return {
        "mood": _mood(text),
        "toxicity": _toxicity(text),
        "artifacts": _artifacts(text),
        "filters": _word_filters(text, filters),
        "meaningful": _is_meaningful_text(text)
    }


def processCollections(text: str):
    return {
        "mood": _mood(text),
        "toxicity": _toxicity(text),
    }
