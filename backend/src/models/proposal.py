from sqlalchemy import Column, Integer, String, ForeignKey
from src.config.database import Base

class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    expert_id = Column(Integer)
    price = Column(Integer)
    status = Column(String, default="PENDING")