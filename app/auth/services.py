from datetime import datetime, timedelta

import httpx
from auth.models import User
from config.general import conf
from fastapi import HTTPException
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

TOKEN_URL = "https://oauth.yandex.ru/token"
USER_INFO_URL = "https://login.yandex.ru/info"


def create_internal_token(user_id: int):
    data = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=conf.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(data, conf.SECRET_KEY, algorithm=conf.ALGORITHM)


async def get_or_create_user(db: AsyncSession, yandex_id: str, username: str):
    result = await db.execute(select(User).filter_by(yandex_id=yandex_id))
    user = result.scalars().first()
    if not user:
        user = User(yandex_id=yandex_id, username=username)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


async def exchange_code_for_token(code: str):
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": conf.YANDEX_CLIENT_ID,
        "client_secret": conf.YANDEX_CLIENT_SECRET,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(TOKEN_URL, data=data)
    if response.status_code != 200:
        raise HTTPException(
            status_code=400, detail="Ошибка обмена кода на токен Яндекса"
        )
    return response.json().get("access_token")


async def fetch_user_info(access_token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            USER_INFO_URL, headers={"Authorization": f"OAuth {access_token}"}
        )
    if response.status_code != 200:
        raise HTTPException(
            status_code=400, detail="Не удалось получить информацию о пользователе"
        )
    return response.json()
