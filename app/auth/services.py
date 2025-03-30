from datetime import datetime, timedelta

import httpx
from auth.models import User
from config.db_session import get_db
from config.general import conf
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

TOKEN_URL = "https://oauth.yandex.ru/token"
USER_INFO_URL = "https://login.yandex.ru/info"


def create_internal_token(username: str):
    data = {
        "sub":
        username,
        "exp":
        datetime.utcnow() +
        timedelta(minutes=conf.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(data, conf.APP_SECRET_KEY, algorithm=conf.ALGORITHM)


def refresh_internal_token(token: str):
    username = decode_access_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return create_internal_token(username)


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token,
                             conf.APP_SECRET_KEY,
                             algorithms=[conf.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise JWTError("Неверный токен")
        return username
    except JWTError as e:
        print(e)
        return None


async def get_current_user(token: str = Depends(conf.OAUTH2_SCHEME),
                           db: AsyncSession = Depends(get_db)):
    print(token)
    username = decode_access_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = ((await db.execute(select(User).filter(User.username == username)
                              )).scalars().first())
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Пользователь не найден")
    return user


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
        raise HTTPException(status_code=400,
                            detail="Ошибка обмена кода на токен Яндекса")
    return response.json().get("access_token")


async def fetch_user_info(access_token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            USER_INFO_URL, headers={"Authorization": f"OAuth {access_token}"})
    if response.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail="Не удалось получить информацию о пользователе")
    return response.json()
