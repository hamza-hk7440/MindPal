from ingestion.domain.interfaces.chunks_repo import IChunksRepository


class DeleteChunkByResourceUseCase:
    def __init__(self, chunks_repo: IChunksRepository):
        self.chunks_repo = chunks_repo

    async def execute(self, resource_id: str) -> int:
        """
        Deletes all chunks associated with a given resource ID.

        Args:
            resource_id (str): The ID of the resource whose chunks are to be deleted.

        Returns:
            int: The number of chunks deleted.
        """
        deleted_count = await self.chunks_repo.delete_all_chunks_by_resource(resource_id)
        return deleted_count
    