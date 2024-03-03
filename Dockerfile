FROM python:3.11-slim-bookworm

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN apt-get update
RUN apt-get install build-essential python3-dev -y

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

RUN cd /code
RUN python -m dostoevsky download fasttext-social-network-model

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]