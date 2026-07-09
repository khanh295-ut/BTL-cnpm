from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
)
from backend.src.services.project_service import ProjectService

# SỬA: prefix thành /api/projects và cho phép redirect_slashes True (mặc định)
router = APIRouter(
    prefix="/api/projects",
    tags=["Projects"],
    redirect_slashes=True
)

service = ProjectService()

@router.get("", response_model=List[ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    return service.get_all(db)

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: UUID, db: Session = Depends(get_db)):
    project = service.get_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    return service.create(db, payload)

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: UUID, payload: ProjectUpdate, db: Session = Depends(get_db)):
    project = service.update(db, project_id, payload)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: UUID, db: Session = Depends(get_db)):
    deleted = service.delete(db, project_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return None
