# backend/src/services/dashboard_service.py

from sqlalchemy.orm import Session
from sqlalchemy import text

def _try_import_user():
    """
    Thử import User từ các file model phổ biến.
    Trả về class User hoặc None nếu không tìm thấy.
    """
    try:
        from backend.src.models.user import User
        return User
    except Exception:
        pass
    try:
        from backend.src.models.auth import User
        return User
    except Exception:
        pass
    try:
        from backend.src.models.register import User
        return User
    except Exception:
        return None

def _try_import_model(module_name, class_name):
    """
    Hàm helper để import model theo tên module và class.
    """
    try:
        module = __import__(f"backend.src.models.{module_name}", fromlist=[class_name])
        return getattr(module, class_name)
    except Exception:
        return None


class DashboardService:
    def get_dashboard(self, db: Session):
        # Import các model cần thiết
        User = _try_import_user()
        Project = _try_import_model("project", "Project")
        Expert = _try_import_model("expert", "Expert")
        Proposal = _try_import_model("proposal", "Proposal")
        Contract = _try_import_model("contract", "Contract")
        Enterprise = _try_import_model("enterprise", "Enterprise")  # thêm Enterprise

        # Hàm helper để đếm an toàn
        def safe_count_model(model, table_name):
            if model is not None:
                try:
                    return db.query(model.id).count()
                except Exception:
                    pass
            try:
                res = db.execute(text(f"SELECT COUNT(id) FROM {table_name}"))
                count = res.scalar()
                return int(count or 0)
            except Exception:
                return 0

        # Đếm số lượng các entity
        users_count = safe_count_model(User, "users")
        projects_count = safe_count_model(Project, "projects")
        experts_count = safe_count_model(Expert, "experts")
        proposals_count = safe_count_model(Proposal, "proposals")
        contracts_count = safe_count_model(Contract, "contracts")
        enterprises_count = safe_count_model(Enterprise, "enterprises")

        # Trả về dữ liệu dashboard đầy đủ
        return {
            "users": users_count,
            "projects": projects_count,
            "experts": experts_count,
            "proposals": proposals_count,
            "contracts": contracts_count,
            "enterprises": enterprises_count,
        }

    def recent_projects(self, db: Session, limit: int = 5):
        Project = _try_import_model("project", "Project")
        if Project is None:
            return []
        q = db.query(Project).order_by(Project.created_at.desc()).limit(limit)
        return [
            {
                "id": str(getattr(p, "id", "")),
                "title": getattr(p, "title", None),
                "budget": getattr(p, "budget", 0),
                "status": getattr(p, "status", None),
            }
            for p in q
        ]

    def recent_proposals(self, db: Session, limit: int = 5):
        Proposal = _try_import_model("proposal", "Proposal")
        if Proposal is None:
            return []
        q = db.query(Proposal).order_by(Proposal.created_at.desc()).limit(limit)
        return [
            {
                "id": str(getattr(p, "id", "")),
                "project_id": str(getattr(p, "project_id", "")),
                "expert_id": str(getattr(p, "expert_id", "")),
                "bid_amount": getattr(p, "bid_amount", 0),
                "status": getattr(p, "status", None),
            }
            for p in q
        ]

    def recent_reviews(self, db: Session, limit: int = 5):
        Review = _try_import_model("review", "Review")
        if Review is None:
            return []
        q = db.query(Review).order_by(Review.created_at.desc()).limit(limit)
        return [
            {
                "id": str(getattr(r, "id", "")),
                "project_id": str(getattr(r, "project_id", "")),
                "rating": getattr(r, "rating", None),
                "comment": getattr(r, "comment", None),
            }
            for r in q
        ]
