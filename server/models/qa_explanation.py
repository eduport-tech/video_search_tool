from pydantic import BaseModel

class Option(BaseModel):
    value: str
    option: int

class QuestionNAnswer(BaseModel):
    question_id: int = None
    question: str
    options: list[Option] = []
    answer : str

class ExplanationResponse(BaseModel):
    explanation: str
