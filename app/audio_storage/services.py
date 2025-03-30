from audio_storage.models import AudioFile
from auth.models import User
from config.general import conf
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def save_file(file, filename):
    filepath = conf.UPLOADS_PATH / filename
    with open(filepath, "wb") as f:
        while chunk := await file.read(conf.CHUNK_SIZE):
            f.write(chunk)
    return filepath


async def get_file_from_db(file_id: int, db: AsyncSession, user: User):
    file = ((await
             db.execute(select(AudioFile).where(AudioFile.id == int(file_id))
                        )).scalars().first())
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Файл не найден")
    if file.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет доступа к этому файлу",
        )
    return file
