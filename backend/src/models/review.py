from sqlalchemy import Column, Integer, String, ForeignKey
from src.config.database import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    expert_id = Column(Integer)  
    rating = Column(Integer)
    comment = Column(String)