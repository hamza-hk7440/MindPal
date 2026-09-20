from fastapi import APIRouter, Depends, status

from assessment.quiz.application.services.quiz_catalog_service import QuizCatalogService
from assessment.quiz.presentation.controllers.quiz_controller import QuizController
from assessment.quiz.presentation.schemas.quiz_schema import QuizAttemptRequest

router = APIRouter(prefix="/quiz", tags=["Assessment Quiz"])


def get_quiz_controller() -> QuizController:
    return QuizController(QuizCatalogService())


@router.get("/status")
async def health(controller: QuizController = Depends(get_quiz_controller)) -> dict[str, str]:
    return await controller.health()


@router.get("/quizzes", status_code=status.HTTP_200_OK)
async def list_quizzes(controller: QuizController = Depends(get_quiz_controller)) -> list[dict]:
    return await controller.list_quizzes()


@router.get("/quizzes/{quiz_code}", status_code=status.HTTP_200_OK)
async def get_quiz(quiz_code: str, controller: QuizController = Depends(get_quiz_controller)) -> dict:
    return await controller.get_quiz(quiz_code)


@router.post("/quizzes/{quiz_code}/attempts", status_code=status.HTTP_200_OK)
async def score_quiz(
    quiz_code: str,
    request: QuizAttemptRequest,
    controller: QuizController = Depends(get_quiz_controller),
) -> dict:
    return await controller.score_quiz(quiz_code, request)