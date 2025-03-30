from pathlib import Path
from typing import Annotated

from audio_storage.models import AudioFile
from audio_storage.services import get_file_from_db, save_file
from auth.models import User
from auth.services import get_current_user
from config.db_session import get_db
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/audio_storage")


@router.get("/")
async def list_files(user: User = Depends(get_current_user),
                     db: AsyncSession = Depends(get_db)):
    return ((await db.execute(
        select(AudioFile).where(AudioFile.owner_id == user.id)
    )).scalars().all())


@router.get("/{file_id}")
async def retrieve_file(
        file_id: str,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    file = await get_file_from_db(file_id, db, user)
    return {"file": file}


@router.post("/upload")
async def upload_file(
        filename: Annotated[str, Form()],
        file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    filepath = await save_file(file, filename)
    new_file = AudioFile(filename=filename,
                         filepath=filepath.as_posix(),
                         owner_id=user.id)
    db.add(new_file)
    await db.commit()
    return {"message": "Файл успешно загружен"}


@router.patch("/rename/{file_id}")
async def rename_file(
        file_id: str,
        filename: str = Form(...),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    file = await get_file_from_db(file_id, db, user)
    filepath: Path = Path(file.filepath)
    new_filepath = filepath.with_name(filename)
    try:
        if filepath.exists():
            filepath.rename(new_filepath)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Файл не найден на диске")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при переименовании файла: {str(e)}",
        )
    file.filename = filename
    file.filepath = new_filepath.as_posix()
    await db.commit()
    await db.refresh(file)
    return {
        "message": "Файл переименован",
        "file": {
            "id": file.id,
            "filename": file.filename
        },
    }


@router.delete("/delete/{file_id}")
async def delete_file(
        file_id: str,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    file = await get_file_from_db(file_id, db, user)
    try:
        await file.delete_file(db)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Файл на диске не найден")
    return {"message": "Файл успешно удален"}
