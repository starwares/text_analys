from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_app():
    app = FastAPI(title="Анализатор Текста",
                  description="микросервис для анализа семантики / тональности текста.",
                  version="1.0",
                  docs_url='/docs',
                  openapi_url='/openapi.json',
                  redoc_url=None)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event('startup')
    def startup():
        pass

    return app
