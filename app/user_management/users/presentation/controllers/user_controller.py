from user_management.users.application.services.profile_service import UserProfileService
from user_management.users.presentation.schemas.user_schema import UpdateProfileRequest


class UserController:
    def __init__(self, profile_service: UserProfileService) -> None:
        self.profile_service = profile_service

    async def health(self) -> dict[str, str | int]:
        return self.profile_service.get_status()

    async def get_profile(self) -> dict:
        return self.profile_service.get_profile()

    async def update_profile(self, request: UpdateProfileRequest) -> dict:
        return self.profile_service.update_profile(request.model_dump(exclude_unset=True))

    async def list_members(self) -> list[dict]:
        return self.profile_service.list_members()