from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.schemas.project import ProjectCreate
from src.services.project_service import (
    create_project,
    get_projects,
    update_project,
)

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/")
def create(data: ProjectCreate, db: Session = Depends(get_db)):
    return create_project(db, data)


@router.get("/")
def get_all(db: Session = Depends(get_db)):
    return get_projects(db)


@router.put("/{project_id}")
def update(project_id: int, data: ProjectCreate, db: Session = Depends(get_db)):
    project = update_project(db, project_id, data)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project