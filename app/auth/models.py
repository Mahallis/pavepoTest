from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .config.db_session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    yandex_id = Column(String, unique=True, index=True)
    username = Column(String, unique=True)
    files = relationship("AudioFile", back_populates="owner")
