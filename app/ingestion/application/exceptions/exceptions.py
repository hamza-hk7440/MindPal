class IngestionException(Exception):
    """
    Base class for all ingestion-related exceptions.
    """
    def __init__(self, message: str, error_code: str = "INGESTION_ERROR", status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)


class IngestionValidationException(IngestionException):
    """Raised for general validation errors like missing required payload keys."""
    def __init__(self, message: str):
        super().__init__(message, error_code="INGESTION_VALIDATION_ERROR", status_code=400)


class UnsupportedResourceFormatException(IngestionValidationException):
    """Raised when an uploaded file is not an allowed mime-type (e.g., trying to parse a .exe instead of .pdf)."""
    def __init__(self, message: str):
        super().__init__(message, error_code="UNSUPPORTED_RESOURCE_FORMAT", status_code=415)


class ResourceSizeExceededException(IngestionValidationException):
    """Raised when a file or video length exceeds the configured bounds for your ingestion/chunking limits."""
    def __init__(self, message: str):
        super().__init__(message, error_code="RESOURCE_SIZE_EXCEEDED", status_code=413)


class UnauthorizedIngestionActionException(IngestionException):
    """Raised when a user attempts to interact with or upload to a Study Subject they do not own."""
    def __init__(self, message: str):
        super().__init__(message, error_code="UNAUTHORIZED_INGESTION_ACTION", status_code=403)


class ResourceNotFoundException(IngestionException):
    """Raised when a specific document, video, or subject ID cannot be located in storage/database."""
    def __init__(self, message: str):
        super().__init__(message, error_code="RESOURCE_NOT_FOUND", status_code=404)


class IngestionProcessFailureException(IngestionException):
    """Base class for runtime processing failures."""
    def __init__(self, message: str, error_code: str = "INGESTION_PROCESS_FAILURE"):
        super().__init__(message, error_code=error_code, status_code=422)


class ExtractionFailureException(IngestionProcessFailureException):
    """Raised when text extractors (PDF Reader, OCR, or YouTube transcript downloaders) fail structurally."""
    def __init__(self, message: str):
        super().__init__(message, error_code="EXTRACTION_FAILURE")


class ChunkingFailureException(IngestionProcessFailureException):
    """Raised if structural splitting rules break (e.g., tokenizers misbehaving on corrupt character sets)."""
    def __init__(self, message: str):
        super().__init__(message, error_code="CHUNKING_FAILURE")



class IngestionExternalServiceException(IngestionException):
    """Raised when downstream AI models (Embedding API, Grok/Gemini transcription) fail or refuse to respond."""
    def __init__(self, message: str):
        super().__init__(message, error_code="EXTERNAL_SERVICE_FAILURE", status_code=502)


class IngestionTimeoutException(IngestionException):
    """Raised when network operations, token calculations, or embedding generation calls drag past limits."""
    def __init__(self, message: str):
        super().__init__(message, error_code="INGESTION_TIMEOUT", status_code=504)