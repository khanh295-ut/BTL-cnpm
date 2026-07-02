from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from backend.src.config.database import Base


# =====================================================
# EXPERT (CORE PROFILE)
# =====================================================
class Expert(Base):
    __tablename__ = "experts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    full_name = Column(String(255), nullable=False)
    title = Column(String(255))
    bio = Column(String(500))

    hourly_rate = Column(Float, default=0)
    location = Column(String(255))

    # =========================
    # RELATIONSHIPS
    # =========================
    skills = relationship("Skill", back_populates="expert", cascade="all, delete-orphan")
    experiences = relationship("Experience", back_populates="expert", cascade="all, delete-orphan")
    portfolios = relationship("Portfolio", back_populates="expert", cascade="all, delete-orphan")


# =====================================================
# SKILL
# =====================================================
class Skill(Base):
    __tablename__ = "skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    expert_id = Column(UUID(as_uuid=True), ForeignKey("experts.id"), nullable=False)
    name = Column(String(100), nullable=False)

    expert = relationship("Expert", back_populates="skills")


# =====================================================
# EXPERIENCE
# =====================================================
class Experience(Base):
    __tablename__ = "experiences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    expert_id = Column(UUID(as_uuid=True), ForeignKey("experts.id"), nullable=False)

    company = Column(String(255), nullable=False)
    position = Column(String(255), nullable=False)

    start_date = Column(String(50), nullable=False)
    end_date = Column(String(50), nullable=True)

    expert = relationship("Expert", back_populates="experiences")


# =====================================================
# PORTFOLIO
# =====================================================
class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    expert_id = Column(UUID(as_uuid=True), ForeignKey("experts.id"), nullable=False)

    title = Column(String(255), nullable=False)
    description = Column(String(500))
    link = Column(String(255))

    expert = relationship("Expert", back_populates="portfolios")