from ingestion.domain.interfaces.chunks_repo import IChunksRepository

class DeleteChunkBySubjectIdUseCase:
    def __init__(self, chunks_repo: IChunksRepository):
        self.chunks_repo = chunks_repo

    async def execute(self, study_subject_id: str) -> int:
        """
        Deletes all chunks associated with a given study subject ID.

        Args:
            study_subject_id (str): The ID of the study subject whose chunks are to be deleted.

        Returns:
            int: The number of chunks deleted.
        """
        deleted_count = await self.chunks_repo.delete_all_chunks_by_study_subject(study_subject_id)
        return deleted_count
