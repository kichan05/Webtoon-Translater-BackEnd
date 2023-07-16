from pydantic import BaseModel


# class Point(BaseModel):
#     x: int
#     y: int

class Dialogue(BaseModel):
    # ocr_type : str
    point1: list[int]
    point2: list[int]
    text: str
    confidence: float

class Webtoon(BaseModel):
    time_stamp : str
    ocr : list[Dialogue]