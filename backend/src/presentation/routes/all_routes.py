"""
Router tổng của AITasker.

Quy ước:
- app.py thêm prefix "/api" đúng một lần.
- all_routes.py thêm prefix tài nguyên đúng một lần.
- các file *_routes.py KHÔNG khai báo prefix.
"""

from fastapi import APIRouter

from backend.src.presentation.routes.ai_service_routes import (
    router as ai_service_router,
)
from backend.src.presentation.routes.analytics_routes import (
    router as analytics_router,
)
from backend.src.presentation.routes.auth_routes import (
    router as auth_router,
)
from backend.src.presentation.routes.category_routes import (
    router as category_router,
)
from backend.src.presentation.routes.chat_routes import (
    router as chat_router,
)
from backend.src.presentation.routes.contract_routes import (
    router as contract_router,
)
from backend.src.presentation.routes.deliverable_routes import (
    router as deliverable_router,
)
from backend.src.presentation.routes.dispute_routes import (
    router as dispute_router,
)
from backend.src.presentation.routes.enterprise_routes import (
    router as enterprise_router,
)
from backend.src.presentation.routes.escrow_routes import (
    router as escrow_router,
)
from backend.src.presentation.routes.expert_routes import (
    router as expert_router,
)
from backend.src.presentation.routes.job_assistant_routes import (
    router as job_assistant_router,
)
from backend.src.presentation.routes.milestone_routes import (
    router as milestone_router,
)
from backend.src.presentation.routes.notification_routes import (
    router as notification_router,
)
from backend.src.presentation.routes.payment_routes import (
    router as payment_router,
)
from backend.src.presentation.routes.project_routes import (
    router as project_router,
)
from backend.src.presentation.routes.proposal_routes import (
    router as proposal_router,
)
from backend.src.presentation.routes.recommendation_routes import (
    router as recommendation_router,
)
from backend.src.presentation.routes.review_routes import (
    router as review_router,
)
from backend.src.presentation.routes.service_order_routes import (
    router as service_order_router,
)
from backend.src.presentation.routes.skill_routes import (
    router as skill_router,
)
from backend.src.presentation.routes.statistics_routes import (
    router as statistics_router,
)
from backend.src.presentation.routes.upload_routes import (
    router as upload_router,
)
from backend.src.presentation.routes.user_routes import (
    router as user_router,
)
from backend.src.presentation.routes.wallet_routes import (
    router as wallet_router,
)
from backend.src.presentation.routes.wallet_transaction_routes import (
    router as wallet_transaction_router,
)
from backend.src.presentation.routes.withdrawal_routes import (
    router as withdrawal_router,
)


router = APIRouter()


# ==========================================================
# AUTHENTICATION
# Endpoint cuối: /api/auth/*
# ==========================================================

router.include_router(
    auth_router,
    prefix="/auth",
)


# ==========================================================
# USERS
# Endpoint cuối: /api/users/*
# ==========================================================

router.include_router(
    user_router,
    prefix="/users",
)


# ==========================================================
# CATEGORIES
# Endpoint cuối: /api/categories/*
# ==========================================================

router.include_router(
    category_router,
    prefix="/categories",
)


# ==========================================================
# ENTERPRISES
# Endpoint cuối: /api/enterprises/*
# ==========================================================

router.include_router(
    enterprise_router,
    prefix="/enterprises",
)


# ==========================================================
# EXPERTS
# Endpoint cuối: /api/experts/*
# ==========================================================

router.include_router(
    expert_router,
    prefix="/experts",
)


# ==========================================================
# SKILLS
# Endpoint cuối: /api/skills/*
# ==========================================================

router.include_router(
    skill_router,
    prefix="/skills",
)


# ==========================================================
# PROJECTS
# Endpoint cuối: /api/projects/*
# ==========================================================

router.include_router(
    project_router,
    prefix="/projects",
)


# ==========================================================
# PROPOSALS
# Endpoint cuối: /api/proposals/*
# ==========================================================

router.include_router(
    proposal_router,
    prefix="/proposals",
)


# ==========================================================
# CONTRACTS
# Endpoint cuối: /api/contracts/*
# ==========================================================

router.include_router(
    contract_router,
    prefix="/contracts",
)


# ==========================================================
# MILESTONES
# Endpoint cuối: /api/milestones/*
# ==========================================================

router.include_router(
    milestone_router,
    prefix="/milestones",
)


# ==========================================================
# DELIVERABLES
# Endpoint cuối: /api/deliverables/*
# ==========================================================

router.include_router(
    deliverable_router,
    prefix="/deliverables",
)


# ==========================================================
# PAYMENTS
# Endpoint cuối: /api/payments/*
# ==========================================================

router.include_router(
    payment_router,
    prefix="/payments",
)


# ==========================================================
# REVIEWS
# Endpoint cuối: /api/reviews/*
# ==========================================================

router.include_router(
    review_router,
    prefix="/reviews",
)


# ==========================================================
# ANALYTICS
# Endpoint cuối: /api/analytics/*
# ==========================================================

router.include_router(
    analytics_router,
    prefix="/analytics",
)


# ==========================================================
# STATISTICS
# Endpoint cuối: /api/statistics/*
# ==========================================================

router.include_router(
    statistics_router,
    prefix="/statistics",
)


# ==========================================================
# UPLOADS
# Endpoint cuối: /api/uploads/*
# ==========================================================

router.include_router(
    upload_router,
    prefix="/uploads",
)


# ==========================================================
# AI CHATBOT
# Endpoint cuối:
# POST /api/chat
# GET  /api/chat/health
# ==========================================================

router.include_router(
    chat_router,
    prefix="/chat",
)


# ==========================================================
# NOTIFICATIONS
# Endpoint cuối: /api/notifications/*
# ==========================================================

router.include_router(
    notification_router,
    prefix="/notifications",
)


# ==========================================================
# WALLETS
# Endpoint cuối: /api/wallets/*
# ==========================================================

router.include_router(
    wallet_router,
    prefix="/wallets",
)


# ==========================================================
# WALLET TRANSACTIONS
# Endpoint cuối: /api/wallet-transactions/*
# ==========================================================

router.include_router(
    wallet_transaction_router,
    prefix="/wallet-transactions",
)


# ==========================================================
# WITHDRAWALS
# Endpoint cuối: /api/withdrawals/*
# ==========================================================

router.include_router(
    withdrawal_router,
    prefix="/withdrawals",
)


# ==========================================================
# DISPUTES
# Endpoint cuối: /api/disputes/*
# ==========================================================

router.include_router(
    dispute_router,
    prefix="/disputes",
)


# ==========================================================
# ESCROWS
# Endpoint cuối: /api/escrows/*
# ==========================================================

router.include_router(
    escrow_router,
    prefix="/escrows",
)


# ==========================================================
# RECOMMENDATIONS
# Endpoint cuối: /api/recommendations/*
# ==========================================================

router.include_router(
    recommendation_router,
    prefix="/recommendations",
)


# ==========================================================
# AI SERVICES
# Endpoint cuối: /api/ai-services/*
# ==========================================================

router.include_router(
    ai_service_router,
    prefix="/ai-services",
)


# ==========================================================
# SERVICE ORDERS
# Endpoint cuối: /api/service-orders/*
# ==========================================================

router.include_router(
    service_order_router,
    prefix="/service-orders",
)


# ==========================================================
# JOB ASSISTANT
# Endpoint cuối:
# GET /api/job-assistant/health
# GET /api/job-assistant/languages
# GET /api/job-assistant/detail-levels
# GET /api/job-assistant/template
# ==========================================================

router.include_router(
    job_assistant_router,
    prefix="/job-assistant",
)