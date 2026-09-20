from typing import Any

from pydantic import BaseModel, Field


class QuizChoice(BaseModel):
    id: str
    label: str


class QuizQuestion(BaseModel):
    id: str
    prompt: str
    choices: list[QuizChoice]
    answer: str
    explanation: str


class QuizSummaryResponse(BaseModel):
    code: str
    title: str
    description: str
    question_count: int = Field(..., ge=0)


class QuizTemplateResponse(BaseModel):
    code: str
    title: str
    description: str
    questions: list[QuizQuestion]


class QuizAttemptRequest(BaseModel):
    answers: dict[str, str]


class QuizAttemptResponse(BaseModel):
    quiz_code: str
    score: int
    total: int
    passed: bool
    feedback: list[dict[str, Any]]