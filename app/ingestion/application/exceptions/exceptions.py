"""Exceptions what we will need in the use cases of the ingestion module."""

class IngestionException(Exception):
    """
    Base class for all ingestion-related exceptions.
    """
    def __init__(self, message: str, error_code: str = "INGESTION_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
class InvalidIngestionDataException(IngestionException):
    """
    Raised when the ingestion data is invalid.
    """
    def __init__(self, message: str):
        super().__init__(message, error_code="INVALID_INGESTION_DATA")
class IngestionProcessFailureException(IngestionException):
    """
    Raised when the ingestion process fails.
    """
    def __init__(self, message: str):
        super().__init__(message, error_code="INGESTION_PROCESS_FAILURE")
class UnauthorizedIngestionActionException(IngestionException):
    """
    Raised when a user attempts an unauthorized action during ingestion.
    """
    def __init__(self, message: str):
        super().__init__(message, error_code="UNAUTHORIZED_INGESTION_ACTION")
class ResourceNotFoundException(IngestionException):
    """
    Raised when a required resource is not found during ingestion.
    """
    def __init__(self, message: str):
        super().__init__(message, error_code="RESOURCE_NOT_FOUND")
class IngestionTimeoutException(IngestionException):
    """
    Raised when the ingestion process times out.
    """
    def __init__(self, message: str):
        super().__init__(message, error_code="INGESTION_TIMEOUT")
class IngestionValidationException(IngestionException):
    """
    Raised when there is a validation error during ingestion.
    """
    def __init__(self, message: str):
        super().__init__(message, error_code="INGESTION_VALIDATION_ERROR")
