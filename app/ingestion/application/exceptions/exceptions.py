class IngestionException(Exception):
    def __init__(self, message: str, error_code: str = "INGESTION_ERROR", status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)


class IngestionValidationException(IngestionException):
    def __init__(self, message: str, error_code: str = "INGESTION_VALIDATION_ERROR", status_code: int = 400):
        super().__init__(message, error_code=error_code, status_code=status_code)


class UnsupportedResourceFormatException(IngestionValidationException):
    def __init__(self, message: str):
        super().__init__(message, error_code="UNSUPPORTED_RESOURCE_FORMAT", status_code=415)


class ResourceSizeExceededException(IngestionValidationException):
    def __init__(self, message: str):
        super().__init__(message, error_code="RESOURCE_SIZE_EXCEEDED", status_code=413)


class UnauthorizedIngestionActionException(IngestionException):
    def __init__(self, message: str):
        super().__init__(message, error_code="UNAUTHORIZED_INGESTION_ACTION", status_code=403)


class ResourceNotFoundException(IngestionException):
    def __init__(self, message: str):
        super().__init__(message, error_code="RESOURCE_NOT_FOUND", status_code=404)


class IngestionProcessFailureException(IngestionException):
    def __init__(self, message: str, error_code: str = "INGESTION_PROCESS_FAILURE", status_code: int = 422):
        super().__init__(message, error_code=error_code, status_code=status_code)


class ExtractionFailureException(IngestionProcessFailureException):
    def __init__(self, message: str):
        super().__init__(message, error_code="EXTRACTION_FAILURE")


class ChunkingFailureException(IngestionProcessFailureException):
    def __init__(self, message: str):
        super().__init__(message, error_code="CHUNKING_FAILURE")


class IngestionExternalServiceException(IngestionException):
    def __init__(self, message: str):
        super().__init__(message, error_code="EXTERNAL_SERVICE_FAILURE", status_code=502)


class IngestionTimeoutException(IngestionException):
    def __init__(self, message: str):
        super().__init__(message, error_code="INGESTION_TIMEOUT", status_code=504)