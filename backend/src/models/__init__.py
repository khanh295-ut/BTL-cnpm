"""
Load all SQLAlchemy models.

File này chỉ dùng để đăng ký metadata,
không dùng để import chéo giữa các model.
"""

# ==========================================================
# ASSOCIATION TABLES
# ==========================================================

import backend.src.models.association

# ==========================================================
# AUTH
# ==========================================================

from backend.src.models.auth import (
    PasswordResetToken,
    Permission,
    Role,
    User,
)

# ==========================================================
# CORE MODELS
# ==========================================================

from backend.src.models.category import Category
from backend.src.models.enterprise import Enterprise
from backend.src.models.expert import Expert
from backend.src.models.project import Project
from backend.src.models.proposal import Proposal
from backend.src.models.review import Review
from backend.src.models.skill import Skill

# ==========================================================
# CONTRACT / PAYMENT / MILESTONE
# ==========================================================

from backend.src.models.contract import Contract
from backend.src.models.deliverable import Deliverable
from backend.src.models.dispute import Dispute
from backend.src.models.escrow import Escrow
from backend.src.models.milestone import Milestone
from backend.src.models.notification import Notification
from backend.src.models.payment import Payment
from backend.src.models.wallet import Wallet
from backend.src.models.wallet_transaction import WalletTransaction
from backend.src.models.withdrawal import Withdrawal

# ==========================================================
# AI / SERVICE MARKETPLACE
# ==========================================================

from backend.src.models.ai_service import AIService
from backend.src.models.recommendation import Recommendation
from backend.src.models.service_order import ServiceOrder

# ==========================================================
# REGISTER MODEL
# ==========================================================

try:
    from backend.src.models.register import UserRegisterRequest
except ImportError:
    UserRegisterRequest = None


__all__ = [
    "User",
    "Role",
    "Permission",
    "PasswordResetToken",
    "Enterprise",
    "Category",
    "Expert",
    "Skill",
    "Project",
    "Proposal",
    "Review",
    "Contract",
    "Payment",
    "Milestone",
    "Deliverable",
    "Notification",
    "Wallet",
    "WalletTransaction",
    "Withdrawal",
    "Dispute",
    "Escrow",
    "Recommendation",
    "AIService",
    "ServiceOrder",
    "UserRegisterRequest",
]