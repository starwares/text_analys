from fastapi.testclient import TestClient
from app.main import app
import time

client = TestClient(app)


def log_execution_time(file_path):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            with open(file_path, 'a') as file:
                file.write(f'Время выполнения {func.__name__}: {execution_time:.6f} секунд\n')
            return result
        return wrapper
    return decorator


@log_execution_time('post_time_log.txt')
def test_post_item():
    for i in list(range(1,10000)):
        response = client.post("/", json={'message': "wef3egf34g", 'filters': ["ghbdtn"]})
        assert response.status_code == 200
        response_json = response.json()
        assert response_json, "Ответ не является JSON"

        # Проверяем, что поле "execution" присутствует в ответе
        assert "execution" in response_json, "Поле 'execution' отсутствует в ответе"

        # Выводим значение поля "execution" на экран
        print(f"Execution: {response_json['execution']}")


@log_execution_time('post_collection_time_log.txt')
def test_post_collections():
    for i in list(range(1, 10000)):
        response = client.post("/collection", json={'messages': ["wef3egf34g", "ewfwertg"], 'filters': ["ghbdtn"]})
        assert response.status_code == 200
        response_json = response.json()
        assert response_json, "Ответ не является JSON"

        # Проверяем, что поле "execution" присутствует в ответе
        assert "execution" in response_json, "Поле 'execution' отсутствует в ответе"

        # Выводим значение поля "execution" на экран
        print(f"Execution: {response_json['execution']}")


@log_execution_time('post_summary_time_log.txt')
def test_post_summary():
    for i in list(range(1, 10000)):
        response = client.post("/summary", json={'messages': ["wef3egf34g", "ewfwertg"], 'filters': ["ghbdtn"]})
        assert response.status_code == 200
        response_json = response.json()
        assert response_json, "Ответ не является JSON"

        # Проверяем, что поле "execution" присутствует в ответе
        assert "execution" in response_json, "Поле 'execution' отсутствует в ответе"

        # Выводим значение поля "execution" на экран
        print(f"Execution: {response_json['execution']}")

