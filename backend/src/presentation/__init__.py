from fastapi import APIRouter

from backend.src.presentation.routes.auth_routes import router as auth_router
from backend.src.presentation.routes.expert_routes import router as expert_router
from backend.src.presentation.routes.project_routes import router as project_router
from backend.src.presentation.routes.proposal_routes import router as proposal_router
from backend.src.presentation.routes.review_routes import router as review_router
from backend.src.presentation.routes.admin_routes import router as admin_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(expert_router)
router.include_router(project_router)
router.include_router(proposal_router)
router.include_router(review_router)
router.include_router(admin_router)