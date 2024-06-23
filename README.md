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