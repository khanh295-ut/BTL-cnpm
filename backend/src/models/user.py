from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.src.config.database import Base
from backend.src.models.association import user_roles


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100))
    hashed_password = Column(String(255))

    roles = relationship("Role", secondary=user_roles, back_populates="users")