# backend/src/presentation/routes/all_routes.py
from fastapi import APIRouter

router = APIRouter()

# Helper để import router an toàn
def _safe_import(module_path: str, attr: str = "router"):
    try:
        mod = __import__(module_path, fromlist=[attr])
        return getattr(mod, attr)
    except Exception:
        return None

# Danh sách module router cần include (theo thứ tự mong muốn)
_routes = [
    "backend.src.presentation.routes.auth_routes",
    "backend.src.presentation.routes.user_routes",
    "backend.src.presentation.routes.admin_routes",
    "backend.src.presentation.routes.dashboard_routes",
    "backend.src.presentation.routes.statistics_routes",
    "backend.src.presentation.routes.upload_routes",
    "backend.src.presentation.routes.category_routes",
    "backend.src.presentation.routes.enterprise_routes",
    "backend.src.presentation.routes.expert_routes",
    "backend.src.presentation.routes.skill_routes",
    "backend.src.presentation.routes.project_routes",
    "backend.src.presentation.routes.proposal_routes",
    "backend.src.presentation.routes.review_routes",
    "backend.src.presentation.routes.contract_routes",
    "backend.src.presentation.routes.payment_routes",
    # analytics_routes có thể trùng với dashboard_routes; giữ nếu bạn có file riêng
    "backend.src.presentation.routes.analytics_routes",
]

for module_path in _routes:
    r = _safe_import(module_path)
    if r is not None:
        router.include_router(r)
