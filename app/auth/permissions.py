from audio_storage.models import AudioFile
from auth.models import User
from auth.services import get_current_user
from fastapi import Depends, HTTPException, status


def require_role(role: str):

    def role_checker(user: User = Depends(get_current_user)):
        if user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав",
            )
        return user

    return role_checker


def is_owner_permission(file: AudioFile):

    def ownership_checker(user: User = Depends(get_current_user)):
        if file.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав",
            )
        return user

    return ownership_checker
