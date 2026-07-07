from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from backend.src.config.database import Base


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)

    roles = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
    )