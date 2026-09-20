from fastapi import APIRouter

from assessment.quiz.presentation.routes.quiz_routes import router as quiz_router

api_router = APIRouter()
api_router.include_router(quiz_router)