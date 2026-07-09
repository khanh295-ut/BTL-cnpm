"""
Load all SQLAlchemy models.

File này chỉ dùng để đăng ký metadata,
không dùng để import trong model khác.
"""

from backend.src.models.auth import (
    User,
    Role,
    Permission,
    PasswordResetToken,
)

from backend.src.models.enterprise import (
    Enterprise
)

from backend.src.models.category import (
    Category
)

from backend.src.models.project import (
    Project
)

from backend.src.models.proposal import (
    Proposal
)

from backend.src.models.review import (
    Review
)

from backend.src.models.expert import (
    Expert
)

# ĐÃ BỔ SUNG: Đăng ký thêm model từ file register.py vào metadata
from backend.src.models.register import (
    UserRegisterRequest
)

__all__ = [
    "User",
    "Role",
    "Permission",
    "PasswordResetToken",
    "Enterprise",
    "Category",
    "Project",
    "Proposal",
    "Review",
    "Expert",
    "UserRegisterRequest", # Đừng quên thêm chuỗi này vào __all__
]