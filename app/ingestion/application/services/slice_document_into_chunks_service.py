from abc import ABC, abstractmethod

class ISliceDocumentIntoChunksService(ABC):
    @abstractmethod
    async def slice_document_into_chunks(self, document: str) -> list[str]:
        pass