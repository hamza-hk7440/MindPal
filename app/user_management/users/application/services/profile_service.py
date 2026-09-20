from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4


class UserProfileService:
    def __init__(self) -> None:
        now = datetime.now(timezone.utc)
        self._profile = {
            "id": uuid4(),
            "display_name": "MindPal Admin",
            "email": "admin@mindpal.local",
            "role": "owner",
            "bio": "Demo profile used to showcase the user management module.",
            "favorite_subjects": ["Machine Learning", "Biology", "Software Design"],
            "updated_at": now,
        }
        self._members = [
            {
                "id": uuid4(),
                "display_name": "Amina Torres",
                "email": "amina@mindpal.local",
                "role": "editor",
            },
            {
                "id": uuid4(),
                "display_name": "Leo Martin",
                "email": "leo@mindpal.local",
                "role": "learner",
            },
            {
                "id": uuid4(),
                "display_name": "Sara Chen",
                "email": "sara@mindpal.local",
                "role": "analyst",
            },
        ]

    def get_status(self) -> dict:
        return {"status": "healthy", "module": "user_management", "member_count": len(self._members)}

    def get_profile(self) -> dict:
        return deepcopy(self._profile)

    def update_profile(self, payload: dict) -> dict:
        if payload.get("display_name") is not None:
            self._profile["display_name"] = payload["display_name"]
        if payload.get("bio") is not None:
            self._profile["bio"] = payload["bio"]
        if payload.get("favorite_subjects") is not None:
            self._profile["favorite_subjects"] = payload["favorite_subjects"]
        self._profile["updated_at"] = datetime.now(timezone.utc)
        return deepcopy(self._profile)

    def list_members(self) -> list[dict]:
        return deepcopy(self._members)