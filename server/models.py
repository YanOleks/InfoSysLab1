from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(String, nullable=False, default=lambda: datetime.utcnow().isoformat())

class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String, nullable=False)
    extension = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False, default=0)
    storage_path = Column(String, nullable=False)
    created_at = Column(String, nullable=False, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, nullable=False, default=lambda: datetime.utcnow().isoformat())
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    last_modified_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    __table_args__ = (UniqueConstraint("owner_id", "filename"),)

    owner = relationship("User", foreign_keys=[owner_id])
    uploader = relationship("User", foreign_keys=[uploaded_by])
    modifier = relationship("User", foreign_keys=[last_modified_by])
