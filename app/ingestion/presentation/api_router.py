from fastapi import APIRouter
from ingestion.presentation.routes.chunks_routes import router as chunks_router
from ingestion.presentation.routes.study_subject_routes import router as study_subject_router
from ingestion.presentation.routes.resource_routes import router as resource_router

api_router = APIRouter()
api_router.include_router(chunks_router)
api_router.include_router(study_subject_router)
api_router.include_router(resource_router)