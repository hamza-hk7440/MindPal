from ingestion.application.services.slice_document_into_chunks_service import ISliceDocumentIntoChunksService
from llama_index.core.node_parser import TokenTextSplitter
class SliceDocumentIntoChunksService(ISliceDocumentIntoChunksService):
    async def slice_document_into_chunks(self, document: str) -> list[str]:
        splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=64)
        return splitter.split_text(document)