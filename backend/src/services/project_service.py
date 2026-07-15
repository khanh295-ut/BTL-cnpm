from sqlalchemy.orm import Session
from src.models.project import Project
from src.schemas.project import ProjectCreate


def create_project(db: Session, data: ProjectCreate):
    project = Project(
        title=data.title,
        description=data.description,
        status="OPEN"
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_projects(db: Session):
    return db.query(Project).all()


def update_project(db: Session, project_id: int, data: ProjectCreate):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return None

    project.title = data.title
    project.description = data.description

    db.commit()
    db.refresh(project)
    return project


def change_status(db: Session, project_id: int, status: str):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return None

    project.status = status

    db.commit()
    db.refresh(project)
    return project