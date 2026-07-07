from uuid import UUID
from fastapi import APIRouter, Depends, status
from typing import List

# Presentation Schema Primitives
from ingestion.presentation.schemas.study_subject_schema import CreateStudySubjectRequest, StudySubjectResponse
# Dependency Injection Components
from ingestion.presentation.schemas.dependencies import get_study_subject_controller
from ingestion.presentation.controllers.study_subject_controller import StudySubjectController

router = APIRouter(prefix="/study-subjects", tags=["Study Subjects"])

@router.post(
    "/", 
    response_model=StudySubjectResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new study subject"
)
async def create_study_subject(
    request: CreateStudySubjectRequest, 
    controller: StudySubjectController = Depends(get_study_subject_controller)
) -> StudySubjectResponse:
    return await controller.create_study_subject(request)


@router.delete(
    "/{study_subject_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a study subject by its UUID"
)
async def delete_study_subject(
    study_subject_id: UUID,  # Enforces true UUID validation directly at the route gateway
    controller: StudySubjectController = Depends(get_study_subject_controller)
) -> None:
    await controller.delete_study_subject(study_subject_id)


@router.get(
    "/{study_subject_id}", 
    response_model=StudySubjectResponse,
    summary="Fetch a specific study subject details"
)
async def fetch_study_subject(
    study_subject_id: UUID,  # Upgraded to strict UUID typing
    controller: StudySubjectController = Depends(get_study_subject_controller)
) -> StudySubjectResponse:
    return await controller.fetch_study_subjects(study_subject_id)


@router.get(
    "/", 
    response_model=List[StudySubjectResponse],
    summary="Fetch all available study subjects"
)
async def fetch_all_study_subjects(
    user_id: UUID,
    controller: StudySubjectController = Depends(get_study_subject_controller)
) -> List[StudySubjectResponse]:
    return await controller.fetch_study_subjects(user_id=user_id)


@router.get(
    "/user/{user_id}", 
    response_model=List[StudySubjectResponse],
    summary="Fetch study subjects assigned to a specific user"
)
async def fetch_study_subjects_by_user(
    user_id: UUID,  # Ensures the user identifier matches your database schema constraints
    controller: StudySubjectController = Depends(get_study_subject_controller)
) -> List[StudySubjectResponse]:
    return await controller.fetch_study_subjects_by_user(user_id)