from dataclasses import dataclass


@dataclass
class ApiErrorResponse:
    error: str
    success: bool = False


class ApiError(Exception):
    status_code: int = 400
    safe_message: str = "API error"

    def __init__(self, message: str | None = None):
        if message:
            self.safe_message = message
        super().__init__(self.safe_message)

    def to_response(self) -> dict[str, object]:
        return ApiErrorResponse(error=self.safe_message).__dict__


class ValidationError(ApiError):
    status_code = 400


class ServiceError(ApiError):
    status_code = 502


class BlockchainError(ServiceError):
    status_code = 503
