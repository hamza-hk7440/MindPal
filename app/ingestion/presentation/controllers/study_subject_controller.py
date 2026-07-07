from typing import List
from uuid import UUID
from fastapi import status, HTTPException
import logging

from ingestion.presentation.schemas.study_subject_schema import (
    StudySubjectResponse, 
    CreateStudySubjectRequest
)
from ingestion.application.use_cases.commands.create_study_subject_uc import CreateStudySubjectUseCase
from ingestion.application.use_cases.commands.delete_study_subject_uc import DeleteStudySubjectUseCase
from ingestion.application.use_cases.queries.fetch_study_subject_uc import FetchStudySubjectUseCase
from ingestion.application.exceptions.exceptions import (
    ResourceNotFoundException, 
    IngestionValidationException,
    StudySubjectNotFoundException
)

logger = logging.getLogger("mindpal.ingestion.presentation")

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
        logger.info(f"Initiating study subject provisioning: Name='{request.name}' for User='{request.user_id}'")
        try:
            study_subject_dto = await self._create_uc.execute(
                user_id=request.user_id,
                name=request.name
            )
            return self._map_to_response_schema(study_subject_dto)
            
        except (IngestionValidationException, ValueError) as exc:
            logger.warning(f"Validation constraints breached during entity creation: {str(exc)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc)
            )
        except Exception as exc:
            logger.error(f"Unhandled systemic exception during entity provisioning: {str(exc)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An internal structural error occurred while executing the transaction."
            )

    async def delete_study_subject(self, subject_id: UUID) -> None:
        logger.info(f"Requesting removal of context boundary target: SubjectID='{subject_id}'")
        try:
            await self._delete_uc.execute(subject_id=subject_id)
            logger.info(f"Successfully deleted study subject context target: ID='{subject_id}'")
            
        except (ResourceNotFoundException, StudySubjectNotFoundException) as exc:
            logger.warning(f"Target clear execution aborted. Resource absent: {str(exc)}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc)
            )
        except Exception as exc:
            logger.error(f"Lifecycle collapse during entity drop: {str(exc)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Transaction cancellation failed due to system exception."
            )

    async def fetch_study_subjects(self, user_id: UUID) -> List[StudySubjectResponse]:
        logger.info(f"Querying system data read layers for collection collection: User='{user_id}'")
        try:
            raw_collection = await self._fetch_uc.fetch_all_study_subjects(user_id=user_id)
            
            if raw_collection and isinstance(raw_collection[0], list):
                logger.debug("Normalizing multidimensional collection payload matrix down to flat stream array.")
                raw_collection = raw_collection[0]
            
            return [self._map_to_response_schema(subject) for subject in raw_collection]
            
        except IngestionValidationException as exc:
            logger.warning(f"Query payload rejected by core validation layer: {str(exc)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc)
            )
        except Exception as exc:
            logger.critical(f"Data layer mapping error or connectivity termination: {str(exc)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to compile and transform query collection results."
            )

    def _map_to_response_schema(self, domain_object) -> StudySubjectResponse:
        try:
            raw_name = domain_object.name.value if hasattr(domain_object.name, 'value') else domain_object.name
            
            return StudySubjectResponse(
                id=domain_object.id,
                user_id=domain_object.user_id,
                name=raw_name,
                created_at=domain_object.created_at
            )
        except AttributeError as mapping_exc:
            logger.error(f"Anti-corruption adapter structural mismatch error: {str(mapping_exc)}")
            raise ValueError("Target domain model signature is missing essential data properties.")