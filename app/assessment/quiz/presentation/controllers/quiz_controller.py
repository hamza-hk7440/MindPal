from assessment.quiz.application.services.quiz_catalog_service import QuizCatalogService
from assessment.quiz.presentation.schemas.quiz_schema import QuizAttemptRequest


class QuizController:
    def __init__(self, quiz_service: QuizCatalogService) -> None:
        self.quiz_service = quiz_service

    async def health(self) -> dict[str, str]:
        return {"status": "healthy", "module": "assessment"}

    async def list_quizzes(self) -> list[dict]:
        return self.quiz_service.list_quizzes()

    async def get_quiz(self, quiz_code: str) -> dict:
        return self.quiz_service.get_quiz(quiz_code)

    async def score_quiz(self, quiz_code: str, request: QuizAttemptRequest) -> dict:
        return self.quiz_service.score_quiz(quiz_code, request.answers)