from fastapi import APIRouter, Depends, status

from user_management.users.application.services.profile_service import UserProfileService
from user_management.users.presentation.controllers.user_controller import UserController
from user_management.users.presentation.schemas.user_schema import UpdateProfileRequest

router = APIRouter(prefix="/profile", tags=["User Profiles"])
_profile_service = UserProfileService()


def get_user_controller() -> UserController:
    return UserController(_profile_service)


@router.get("/status")
async def health(controller: UserController = Depends(get_user_controller)) -> dict[str, str | int]:
    return await controller.health()


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_profile(controller: UserController = Depends(get_user_controller)) -> dict:
    return await controller.get_profile()


@router.patch("/me", status_code=status.HTTP_200_OK)
async def update_profile(
    request: UpdateProfileRequest,
    controller: UserController = Depends(get_user_controller),
) -> dict:
    return await controller.update_profile(request)


@router.get("/members", status_code=status.HTTP_200_OK)
async def list_members(controller: UserController = Depends(get_user_controller)) -> list[dict]:
    return await controller.list_members()