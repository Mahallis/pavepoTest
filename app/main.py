import uvicorn
from audio_storage.router import router as storage_router
from auth.router import auth_router
from config.general import conf
from fastapi import FastAPI

app = FastAPI()
app.include_router(storage_router)
app.include_router(auth_router)

conf.UPLOADS_PATH.mkdir(exist_ok=True)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
