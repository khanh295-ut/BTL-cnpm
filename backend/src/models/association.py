from sqlalchemy import Column, ForeignKey, Integer, Table

# ĐÃ SỬA: Thêm 'backend.' vào trước đường dẫn để đồng nhất với toàn bộ hệ thống
from backend.src.config.database import Base

# =====================================================
# USER <-> ROLE (Many-to-Many)
# =====================================================
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "role_id",
        Integer,
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

# =====================================================
# ROLE <-> PERMISSION (Many-to-Many)
# =====================================================
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column(
        "role_id",
        Integer,
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        Integer,
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)