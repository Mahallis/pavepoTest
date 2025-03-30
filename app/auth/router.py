from urllib.parse import urlencode

from auth.services import (
    create_internal_token,
    exchange_code_for_token,
    fetch_user_info,
    get_or_create_user,
)
from config.db_session import get_db
from config.general import conf
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

auth_router = APIRouter(prefix="/auth")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="yandex_auth")

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
            status_code=400, detail="Некорректная информация о пользователе"
        )
    user = await get_or_create_user(db=db, yandex_id=yandex_id, username=username)
    internal_token = create_internal_token(user.id)

    return {"access_token": internal_token, "token_type": "bearer"}
