# Запуск проекта в Docker контейнере

Этот репозиторий содержит Dockerfile для сборки Docker образа и инструкции по запуску контейнера на различных операционных системах.

## Требования

- Установленный Docker на вашем компьютере:
  - [Docker Desktop для Windows и macOS](https://www.docker.com/products/docker-desktop)
  - [Docker для Linux](https://docs.docker.com/engine/install/)

## Использование Dockerfile

### Сборка Docker образа

1. Откройте терминал или командную строку.

2. Перейдите в директорию с Dockerfile (пример: `cd path/to/your/project`).

3. Выполните следующую команду для сборки Docker образа (замените `<image_name>` по вашему усмотрению):

   ```bash
   docker build -t <image_name> .

## Запуск контейнера из Docker образа

### На Windows:

1. Откройте PowerShell или командную строку.

2. Запустите контейнер, используя созданный Docker образ (замените `<image_name>` по вашему усмотрению):
   
   ```bash
   docker run -d -p 8668:8668 --name my-container <image_name>
   
### На MacOS или Linux:

1. Откройте терминал.

2. Запустите контейнер, используя созданный Docker образ (замените `<image_name>` по вашему усмотрению):
   
   ```bash
   docker run -d -p 8668:8668 --name my-container <image_name>
   
# Установка и запуск приложения локально

## Требования

- Python 3.10.12
- Установленные системные пакеты: gcc, make, g++
- Виртуальное окружение (рекомендуется)

## Шаги установки

1. Клонируйте репозиторий:

    ```bash
    git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ>
    cd <ИМЯ_ВАШЕГО_РЕПОЗИТОРИЯ>

2. Создайте и активируйте виртуальное окружение:

    ```bash

    python3 -m venv venv
    source venv/bin/activate

3. Установите зависимости:

    ```bash
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

4. Установите системные зависимости:

- Для Ubuntu/Debian:

    ```bash
    
    sudo apt-get update
    sudo apt-get install gcc make g++ -y

5. Скачайте модели для приложения:

    ```bash
    
    python -m dostoevsky download fasttext-social-network-model
    python -c 'from transformers import AutoTokenizer, AutoModelForSequenceClassification; AutoTokenizer.from_pretrained("cointegrated/rubert-tiny-toxicity"); AutoModelForSequenceClassification.from_pretrained("cointegrated/rubert-tiny-toxicity").eval();'

6. Запустите приложение:

    ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8668

Теперь приложение должно быть доступно по адресу http://0.0.0.0:8668.

## Дополнительные сведения

    Порт по умолчанию: 8668
    Основной файл приложения: app/main.py

Если у вас возникнут вопросы или проблемы, обратитесь к документации или откройте issue в репозитории.
