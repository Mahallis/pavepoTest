from audio_storage.services import save_file
from config.db_session import get_db
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/audio_storage")


@router.get("/")
def list_files():
    pass


@router.get("/{file_id}")
def get_file(file_id: str):
    pass


@router.post("/upload")
async def upload_file(
    filename: str, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)
):
    filepath = await save_file(file, filename)
    return {"message": "success", filepath: str(filepath)}


@router.patch("/rename/{file_id}")
def rename_file(file_id: str):
    pass


@router.delete("/delete/{file_id}")
def delete_file(file_id: str):
    pass
