from audio_storage.router import router as storage_router
from fastapi import FastAPI

app = FastAPI()
app.include_router(storage_router)
