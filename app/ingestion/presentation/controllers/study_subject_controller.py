from typing import List, Optional
from uuid import UUID
from fastapi import status, HTTPException

# Presentation Layer Schema Context
from ingestion.presentation.schemas.study_subject_schema import (
    StudySubjectResponse, 
    CreateStudySubjectRequest
)
# Application Layer Use Case Contracts
from ingestion.application.use_cases.commands.create_study_subject_uc import CreateStudySubjectUseCase
from ingestion.application.use_cases.commands.delete_study_subject_uc import DeleteStudySubjectUseCase
from ingestion.application.use_cases.queries.fetch_study_subject_uc import FetchStudySubjectUseCase
# Application Layer Structural Exception Boundaries
from ingestion.application.exceptions.exceptions import (
    ResourceNotFoundException, 
    IngestionValidationException
)

class StudySubjectController:
    def __init__(
        self, 
        create_study_subject_uc: CreateStudySubjectUseCase, 
        delete_study_subject_uc: DeleteStudySubjectUseCase, 
        fetch_study_subject_uc: FetchStudySubjectUseCase
    ):
        self._create_uc = create_study_subject_uc
        self._delete_uc = delete_study_subject_uc
        self._fetch_uc = fetch_study_subject_uc

    async def create_study_subject(self, request: CreateStudySubjectRequest) -> StudySubjectResponse:
        """
        Coordinates the orchestration payload for provisioning a new domain entity.
        Maps inbound application layer DTO models down to Pydantic representation layers.
        """
        try:
            study_subject_dto = await self._create_uc.execute(
                name=request.name,
                created_at=request.created_at
            )
            # Upgraded from from_orm to standard modern Pydantic v2 model validation
            return StudySubjectResponse.model_validate(study_subject_dto)
            
        except IngestionValidationException as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc)
            )

    async def delete_study_subject(self, subject_id: UUID) -> None:
        """
        Dispatches target ID coordinates to the application command line.
        Enforces UUID type safety at the route boundary wrapper layer.
        """
        try:
            await self._delete_uc.execute(subject_id=subject_id)
            
        except ResourceNotFoundException as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deletable context target missing: {str(exc)}"
            )

    async def fetch_study_subjects(self) -> List[StudySubjectResponse]:
        """
        Queries application read layer collections. 
        Safely serializes domain core structural arrays into clear interface contracts.
        """
        study_subjects_dto = await self._fetch_uc.fetch_all()
        
        return [
            StudySubjectResponse.model_validate(subject) 
            for subject in study_subjects_dto
        ]