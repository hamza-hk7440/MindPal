from ingestion.presentation.schemas.study_subject_schema import StudySubjectResponse,CreateStudySubjectRequest
from ingestion.application.use_cases.commands.create_study_subject_uc import CreateStudySubjectUseCase
from ingestion.application.use_cases.commands.delete_study_subject_uc import DeleteStudySubjectUseCase
from ingestion.application.use_cases.queries.fetch_study_subject_uc import FetchStudySubjectUseCase

class StudySubjectController:
    def __init__(self, create_study_subject_uc: CreateStudySubjectUseCase, delete_study_subject_uc: DeleteStudySubjectUseCase, fetch_study_subject_uc: FetchStudySubjectUseCase):
        self.create_study_subject_uc = create_study_subject_uc
        self.delete_study_subject_uc = delete_study_subject_uc
        self.fetch_study_subject_uc = fetch_study_subject_uc

    async def create_study_subject(self, request: CreateStudySubjectRequest) -> StudySubjectResponse:
        study_subject_dto = await self.create_study_subject_uc.execute(
            name=request.name,
            created_at=request.created_at
        )
        return StudySubjectResponse.from_orm(study_subject_dto)

    async def delete_study_subject(self, subject_id: str):
        await self.delete_study_subject_uc.execute(subject_id=subject_id)

    async def fetch_study_subjects(self):
        study_subjects_dto = await self.fetch_study_subject_uc.fetch_all()
        return [StudySubjectResponse.from_orm(subject) for subject in study_subjects_dto]