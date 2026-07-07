from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID


# =========================
# EXPERT
# =========================
class ExpertCreate(BaseModel):
    full_name: str
    title: Optional[str] = None
    bio: Optional[str] = None
    hourly_rate: Optional[float] = 0
    location: Optional[str] = None


class ExpertUpdate(BaseModel):
    full_name: Optional[str] = None
    title: Optional[str] = None
    bio: Optional[str] = None
    hourly_rate: Optional[float] = None
    location: Optional[str] = None


class ExpertResponse(BaseModel):
    id: UUID
    full_name: str
    title: Optional[str]
    bio: Optional[str]
    hourly_rate: float
    location: Optional[str]

    class Config:
        orm_mode = True


# =========================
# SKILL
# =========================
class SkillCreate(BaseModel):
    name: str


class SkillResponse(BaseModel):
    id: UUID
    name: str

    class Config:
        orm_mode = True


# =========================
# EXPERIENCE
# =========================
class ExperienceCreate(BaseModel):
    company: str
    position: str
    start_date: str
    end_date: Optional[str] = None


class ExperienceUpdate(BaseModel):
    company: Optional[str]
    position: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]


class ExperienceResponse(BaseModel):
    id: UUID
    company: str
    position: str
    start_date: str
    end_date: Optional[str]

    class Config:
        orm_mode = True


# =========================
# PORTFOLIO
# =========================
class PortfolioCreate(BaseModel):
    title: str
    description: Optional[str] = None
    link: Optional[str] = None


class PortfolioUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    link: Optional[str]


class PortfolioResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    link: Optional[str]

    class Config:
        orm_mode = True