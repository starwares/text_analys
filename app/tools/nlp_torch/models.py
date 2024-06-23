from pydantic import BaseModel, validator


class ToxicContentModel(BaseModel):
    non_toxic: float
    insult: float
    obscenity: float
    threat: float
    dangerous: float

    @validator('*', pre=True, always=True)
    def round_values(cls, v):
        return float(f"{v:.3f}")

    @classmethod
    def from_list(cls, data: list):
        if len(data) < 4:
            raise ValueError("В этом массиве должно быть не меньше 5 элементов")
        return cls(non_toxic=data[0],
                   insult=data[1],
                   obscenity=data[2],
                   threat=data[3],
                   dangerous=data[4])


class ToxicModel(BaseModel):
    toxicity: ToxicContentModel
    toxicity_count_tokens: int
