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


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)

service = ProjectService()


# =====================================
# GET ALL PROJECTS
# =====================================

@router.get(
    "",
    response_model=list[ProjectResponse],
)
def get_projects(
    db: Session = Depends(get_db),
):

    return service.get_projects(db)


# =====================================
# GET PROJECT BY ID
# =====================================

@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
):

    project = service.get_project(db, project_id)

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return project


# =====================================
# CREATE PROJECT
# =====================================

@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
):

    return service.create_project(db, payload)


# =====================================
# UPDATE PROJECT
# =====================================

@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
)
def update_project(
    project_id: UUID,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
):

    project = service.update_project(
        db,
        project_id,
        payload,
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return project


# =====================================
# DELETE PROJECT
# =====================================

@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
):

    success = service.delete_project(
        db,
        project_id,
    )

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )


# =====================================
# CHANGE STATUS
# =====================================

@router.patch(
    "/{project_id}/status",
    response_model=ProjectResponse,
)
def change_status(
    project_id: UUID,
    status_value: str,
    db: Session = Depends(get_db),
):

    project = service.change_status(
        db,
        project_id,
        status_value,
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return project