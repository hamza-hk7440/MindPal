class ChatException(Exception):
    """
    Base class for all chat-related exceptions.
    """
    def __init__(self, message: str, error_code: str = "CHAT_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
class InvalidMessageException(ChatException):
    """
    Raised when a chat message is invalid.
    """
    def __init__(self, message: str):
        super().__init__(message, error_code="INVALID_MESSAGE")
class InvalidConversationException(ChatException):
    """
    Raised when a conversation is invalid.
    """
    def __init__(self, message: str):
        super().__init__(message, error_code="INVALID_CONVERSATION")
class MessageSendFailureException(ChatException):
    """
    Raised when sending a message fails.
    """
    def __init__(self, message: str):
        super().__init__(message, error_code="MESSAGE_SEND_FAILURE")
class ConversationCreationFailureException(ChatException):
    """
    Raised when creating a conversation fails.
    """
    def __init__(self, message: str):
        super().__init__(message, error_code="CONVERSATION_CREATION_FAILURE")
class ConversationNotFoundException(ChatException):
    """
    Raised when a conversation is not found.
    """
    def __init__(self, message: str):
        super().__init__(message, error_code="CONVERSATION_NOT_FOUND")
class MessageNotFoundException(ChatException):
    """
    Raised when a message is not found.
    """
    def __init__(self, message: str):
        super().__init__(message, error_code="MESSAGE_NOT_FOUND")
class UnauthorizedActionException(ChatException):
    """
    Raised when a user attempts an unauthorized action.
    """
    def __init__(self, message: str):
        super().__init__(message, error_code="UNAUTHORIZED_ACTION")
