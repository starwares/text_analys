from fastapi import FastAPI


def create_app():
    app = FastAPI(title="Анализатор Текста",
                  description="микросервис для анализа семантики / тональности текста.",
                  version="1.0",
                  docs_url='/docs',
                  openapi_url='/openapi.json',
                  redoc_url=None)

    @app.on_event('startup')
    def startup():
        pass

    return app
