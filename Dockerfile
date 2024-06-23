FROM python:3.10.12-slim-bookworm

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN apt-get update
RUN apt-get install gcc make g++ -y
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN apt-get auto-remove -y linux-libc-dev libaom3 gcc make g++ libheif1 libtiff6 binutils

RUN python -m dostoevsky download fasttext-social-network-model
RUN python -c 'from transformers import AutoTokenizer, AutoModelForSequenceClassification; AutoTokenizer.from_pretrained("cointegrated/rubert-tiny-toxicity"); AutoModelForSequenceClassification.from_pretrained("cointegrated/rubert-tiny-toxicity").eval();'

COPY ./app /code/app

EXPOSE 8668
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8668"]