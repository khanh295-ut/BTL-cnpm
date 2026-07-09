from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime
from backend.src.config.database import Base


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(Text, nullable=False, unique=True)
    revoked_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
