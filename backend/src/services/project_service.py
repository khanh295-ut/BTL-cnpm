from sqlalchemy.orm import Session
from backend.src.models.project import Project


class ProjectService:

    def create_project(self, db: Session, title: str, description: str):

        project = Project(
            title=title,
            description=description
        )

        db.add(project)
        db.commit()
        db.refresh(project)

        return project

    def list_projects(self, db: Session):
        return db.query(Project).all()

    def update_project(self, db: Session, project_id: str, title=None, description=None):

        project = db.query(Project).filter(Project.id == project_id).first()

        if title:
            project.title = title

        if description:
            project.description = description

        db.commit()
        db.refresh(project)

        return project

    def change_status(self, db: Session, project_id: str, status: str):

        project = db.query(Project).filter(Project.id == project_id).first()
        project.status = status

        db.commit()
        return project