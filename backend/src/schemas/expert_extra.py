from pydantic import BaseModel
from typing import Optional


# =========================
# SKILL
# =========================
class SkillCreate(BaseModel):
    name: str


class SkillResponse(BaseModel):
    id: str
    name: str


# =========================
# EXPERIENCE
# =========================
class ExperienceCreate(BaseModel):
    company: str
    position: str
    start_date: str
    end_date: Optional[str] = None


class ExperienceResponse(BaseModel):
    id: str
    company: str
    position: str


# =========================
# PORTFOLIO
# =========================
class PortfolioCreate(BaseModel):
    title: str
    description: Optional[str] = None
    link: Optional[str] = None


class PortfolioResponse(BaseModel):
    id: str
    title: str