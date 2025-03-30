from audio_storage.models import AudioFile
from config.db_session import Base
from sqlalchemy import Column, Enum, Integer, String
from sqlalchemy.orm import relationship


class RoleEnum(str, Enum):
    USER = "user"
    SUPERUSER = "superuser"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    yandex_id = Column(String, unique=True, index=True)
    username = Column(String, unique=True)
    role = Column(
        Enum(RoleEnum.USER, RoleEnum.SUPERUSER, name="roleenum"),
        default=RoleEnum.USER,
        nullable=False,
    )
    files = relationship(AudioFile, back_populates="owner")
