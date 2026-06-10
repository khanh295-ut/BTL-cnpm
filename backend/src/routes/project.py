from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.models.project import Project
from src.schemas.project import ProjectCreate

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/")
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(**data.dict())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/")
def get_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()


@router.put("/{project_id}")
def update_project(project_id: int, data: ProjectCreate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return {"error": "Not found"}

    project.title = data.title
    project.description = data.description

    db.commit()
    db.refresh(project)
    return project


@router.patch("/{project_id}/status")
def change_status(project_id: int, status: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return {"error": "Not found"}

    project.status = status
    db.commit()
    db.refresh(project)
    return project