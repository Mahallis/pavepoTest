from urllib.parse import urlencode

from auth.models import User
from auth.permissions import require_role
from auth.services import (
    create_internal_token,
    exchange_code_for_token,
    fetch_user_info,
    get_or_create_user,
    refresh_internal_token,
)
from config.db_session import get_db
from config.general import conf
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

auth_router = APIRouter(prefix="/auth")

AUTHORIZE_URL = "https://oauth.yandex.ru/authorize"


@auth_router.get("/login_yandex")
async def login_yandex():
    params = {
        "response_type": "code",
        "client_id": conf.YANDEX_CLIENT_ID,
    }
    auth_url = f"{AUTHORIZE_URL}?{urlencode(params)}"
    return RedirectResponse(auth_url)


@auth_router.get("/yandex_auth")
async def yandex_auth(code: str, db: AsyncSession = Depends(get_db)):
    access_token = await exchange_code_for_token(code)

    user_info = await fetch_user_info(access_token)
    yandex_id = user_info.get("id")
    username = user_info.get("login")
    if not yandex_id or not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректная информация о пользователе",
        )
    user = await get_or_create_user(db=db,
                                    yandex_id=yandex_id,
                                    username=username)
    internal_token = create_internal_token(user.username)

    return {"access_token": internal_token, "token_type": "bearer"}


@auth_router.post("/refresh_token")
async def refresh_token(token: str = Depends(conf.OAUTH2_SCHEME)):
    new_token = refresh_internal_token(token)

    return {"access_token": new_token, "token_type": "bearer"}


@auth_router.get("/list_users")
async def list_users(
        user: User = Depends(require_role("superuser")),
        db: AsyncSession = Depends(get_db),
):
    return (await db.execute(select(User))).scalars().all()


@auth_router.delete("/delete_user/{user_id}")
async def delete_user(
        user_id: int,
        user: User = Depends(require_role("superuser")),
        db: AsyncSession = Depends(get_db),
):
    user_to_delete = ((await
                       db.execute(select(User).where(User.id == user_id)
                                  )).scalars().first())
    if not user_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Пользователь не найден")
    await db.delete(user_to_delete)
    await db.commit()
