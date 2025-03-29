from fastapi import APIRouter

router = APIRouter(prefix='/storage')


@router.get('/')
def list_files():
    pass


@router.get('/{file_id}')
def get_file(file_id: str):
    pass


@router.post('/upload')
def upload_file():
    pass


@router.patch('/rename/{file_id}')
def rename_file(file_id: str):
    pass


@router.delete('/delete/{file_id}')
def delete_file(file_id: str):
    pass
