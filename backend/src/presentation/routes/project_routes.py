from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.application.content_use_cases import (
    create_project,
    update_project,
    change_project_status,
    list_projects
)
from backend.src.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectStatusUpdate,
    ProjectResponse
)

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/", response_model=list[ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    return list_projects(db)


@router.post("/", response_model=ProjectResponse)
def create(data: ProjectCreate, db: Session = Depends(get_db)):
    return create_project(db, data.title, data.description)


@router.put("/{project_id}", response_model=ProjectResponse)
def update(project_id: str, data: ProjectUpdate, db: Session = Depends(get_db)):
    return update_project(db, project_id, data.title, data.description)


@router.patch("/{project_id}/status")
def update_status(project_id: str, data: ProjectStatusUpdate, db: Session = Depends(get_db)):
    return change_project_status(db, project_id, data.status)