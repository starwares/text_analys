from pydantic import BaseModel


class ToxicContentModel(BaseModel):
    non_toxic: float
    insult: float
    obscenity: float
    threat: float
    dangerous: float

    @classmethod
    def from_list(cls, data: list):
        if len(data) < 4:
            raise ValueError("В этом массиве должно быть не меньше 5 элементов")
        return cls(non_toxic=cls._format_score(data[0]),
                   insult=cls._format_score(data[1]),
                   obscenity=cls._format_score(data[2]),
                   threat=cls._format_score(data[3]),
                   dangerous=cls._format_score(data[4]))

    @staticmethod
    def _format_score(score):
        return float(f"{score:.3f}")


class ToxicModel(BaseModel):
    toxicity: ToxicContentModel
