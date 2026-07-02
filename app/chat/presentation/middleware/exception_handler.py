from fastapi import Request,status
from fastapi.responses import JSONResponse

from chat.application.exceptions.exception import ( ConversationNotFoundException,InvalidMessageException,ConversationCreationFailureException)

async def exception_handler(request: Request, exc: Exception):
    if isinstance(exc, InvalidMessageException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": exc.error_code, "message": exc.message},
        )
    elif isinstance(exc, ConversationNotFoundException):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": exc.error_code, "message": exc.message},
        )
    elif isinstance(exc, ConversationCreationFailureException):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": exc.error_code, "message": exc.message},
        )
    else:
        # For any other unhandled exceptions, return a generic error response
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "INTERNAL_SERVER_ERROR", "message": str(exc)},
        )
    