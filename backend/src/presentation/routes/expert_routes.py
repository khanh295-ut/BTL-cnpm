from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.models.expert import Expert, Skill, Experience, Portfolio

from backend.src.schemas.expert import (
    ExpertCreate,
    ExpertUpdate,
    ExpertResponse,
    SkillCreate,
    SkillResponse,
    ExperienceCreate,
    ExperienceUpdate,
    ExperienceResponse,
    PortfolioCreate,
    PortfolioUpdate,
    PortfolioResponse
)

router = APIRouter(prefix="/experts", tags=["Experts"])


# =====================================================
# EXPERT CRUD CORE
# =====================================================

@router.post("/", response_model=ExpertResponse)
def create_expert(data: ExpertCreate, db: Session = Depends(get_db)):
    expert = Expert(**data.dict())
    db.add(expert)
    db.commit()
    db.refresh(expert)
    return expert


@router.get("/", response_model=list[ExpertResponse])
def list_experts(db: Session = Depends(get_db)):
    return db.query(Expert).all()


@router.get("/{expert_id}", response_model=ExpertResponse)
def get_expert(expert_id: str, db: Session = Depends(get_db)):
    expert = db.query(Expert).filter(Expert.id == expert_id).first()
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")
    return expert


@router.put("/{expert_id}", response_model=ExpertResponse)
def update_expert(expert_id: str, data: ExpertUpdate, db: Session = Depends(get_db)):
    expert = db.query(Expert).filter(Expert.id == expert_id).first()
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")

    for k, v in data.dict(exclude_unset=True).items():
        setattr(expert, k, v)

    db.commit()
    db.refresh(expert)
    return expert


@router.delete("/{expert_id}")
def delete_expert(expert_id: str, db: Session = Depends(get_db)):
    expert = db.query(Expert).filter(Expert.id == expert_id).first()
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")

    db.delete(expert)
    db.commit()
    return {"message": "Deleted"}


# =====================================================
# SKILLS
# =====================================================

@router.post("/{expert_id}/skills", response_model=SkillResponse)
def add_skill(expert_id: str, data: SkillCreate, db: Session = Depends(get_db)):
    skill = Skill(expert_id=expert_id, **data.dict())
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


@router.delete("/skills/{skill_id}")
def delete_skill(skill_id: str, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Not found")

    db.delete(skill)
    db.commit()
    return {"message": "Deleted"}


# =====================================================
# EXPERIENCE (FULL CRUD FIX)
# =====================================================

@router.post("/{expert_id}/experiences", response_model=ExperienceResponse)
def add_experience(expert_id: str, data: ExperienceCreate, db: Session = Depends(get_db)):
    exp = Experience(expert_id=expert_id, **data.dict())
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return exp


@router.put("/experiences/{exp_id}", response_model=ExperienceResponse)
def update_experience(exp_id: str, data: ExperienceUpdate, db: Session = Depends(get_db)):
    exp = db.query(Experience).filter(Experience.id == exp_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Not found")

    for k, v in data.dict(exclude_unset=True).items():
        setattr(exp, k, v)

    db.commit()
    db.refresh(exp)
    return exp


@router.delete("/experiences/{exp_id}")
def delete_experience(exp_id: str, db: Session = Depends(get_db)):
    exp = db.query(Experience).filter(Experience.id == exp_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Not found")

    db.delete(exp)
    db.commit()
    return {"message": "Deleted"}


# =====================================================
# PORTFOLIO (FIX MISSING PUT/DELETE)
# =====================================================

@router.post("/{expert_id}/portfolios", response_model=PortfolioResponse)
def add_portfolio(expert_id: str, data: PortfolioCreate, db: Session = Depends(get_db)):
    p = Portfolio(expert_id=expert_id, **data.dict())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.put("/portfolios/{portfolio_id}", response_model=PortfolioResponse)
def update_portfolio(portfolio_id: str, data: PortfolioUpdate, db: Session = Depends(get_db)):
    p = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Not found")

    for k, v in data.dict(exclude_unset=True).items():
        setattr(p, k, v)

    db.commit()
    db.refresh(p)
    return p


@router.delete("/portfolios/{portfolio_id}")
def delete_portfolio(portfolio_id: str, db: Session = Depends(get_db)):
    p = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Not found")

    db.delete(p)
    db.commit()
    return {"message": "Deleted"}