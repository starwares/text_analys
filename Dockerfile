FROM python:3.12.3-slim-bookworm

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN apt-get update
RUN apt-get install gcc make g++ -y

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

RUN cd /code
RUN python -m dostoevsky download fasttext-social-network-model

RUN apt-get auto-remove -y linux-libc-dev libaom3 gcc make g++ libheif1 libtiff6 binutils

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8668"]