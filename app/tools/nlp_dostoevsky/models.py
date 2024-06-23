from pydantic import BaseModel


class MoodContentModel(BaseModel):
    positive: float
    neutral: float
    negative: float
    skip: float
    speech: float

    def __init__(self, **kwargs):
        for key in kwargs:
            kwargs[key] = float(f"{kwargs[key]:.3f}")
        super().__init__(**kwargs)


class MoodModel(BaseModel):
    mood: MoodContentModel
