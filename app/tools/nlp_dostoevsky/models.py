from pydantic import BaseModel


class MoodContentModel(BaseModel):
    positive: float
    neutral: float
    negative: float
    skip: float
    speech: float


class MoodModel(BaseModel):
    mood: MoodContentModel
