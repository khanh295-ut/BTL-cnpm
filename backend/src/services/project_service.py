from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from typing import List, Optional
from datetime import datetime

from backend.src.models.project import Project
from backend.src.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    def get_all(self, db: Session) -> List[Project]:
        """Lấy toàn bộ danh sách dự án"""
        return db.query(Project).all()

    def get_by_id(self, db: Session, project_id: UUID) -> Optional[Project]:
        """Lấy chi tiết một dự án theo ID"""
        return db.query(Project).filter(Project.id == project_id).first()

    def create(self, db: Session, payload: ProjectCreate) -> Project:
        """Tạo mới một dự án"""
        db_project = Project(
            id=uuid4(),
            title=payload.title,
            description=payload.description,
            budget=payload.budget,
            deadline=payload.deadline,
            enterprise_id=payload.enterprise_id,
            category_id=payload.category_id,
            status="OPEN",
            created_at=datetime.utcnow()
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project

    def update(self, db: Session, project_id: UUID, payload: ProjectUpdate) -> Optional[Project]:
        """Cập nhật thông tin dự án"""
        db_project = self.get_by_id(db, project_id)
        if not db_project:
            return None

        # Trích xuất dữ liệu được truyền lên từ Pydantic
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_project, key, value)

        db.commit()
        db.refresh(db_project)
        return db_project

    def delete(self, db: Session, project_id: UUID) -> bool:
        """Xóa một dự án"""
        db_project = self.get_by_id(db, project_id)
        if not db_project:
            return False

        db.delete(db_project)
        db.commit()
        return True