from os import path, remove

from config.db_session import Base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship


class AudioFile(Base):
    __tablename__ = "audio_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    filepath = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="files")

    async def delete_file(self, db: AsyncSession):
        if path.exists(self.filepath):
            remove(self.filepath)
        else:
            raise FileNotFoundError()
        await db.delete(self)
        await db.commit()
