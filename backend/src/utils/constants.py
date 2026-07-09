"""
Application constants
"""

# =====================================
# USER ROLES
# =====================================

ROLE_ADMIN = "ADMIN"
ROLE_ENTERPRISE = "ENTERPRISE"
ROLE_EXPERT = "EXPERT"
ROLE_USER = "USER"

# =====================================
# PROJECT STATUS
# =====================================

PROJECT_OPEN = "OPEN"
PROJECT_IN_PROGRESS = "IN_PROGRESS"
PROJECT_COMPLETED = "COMPLETED"
PROJECT_CANCELLED = "CANCELLED"

# =====================================
# PROPOSAL STATUS
# =====================================

PROPOSAL_PENDING = "PENDING"
PROPOSAL_ACCEPTED = "ACCEPTED"
PROPOSAL_REJECTED = "REJECTED"

# =====================================
# REVIEW
# =====================================

MIN_RATING = 1
MAX_RATING = 5

# =====================================
# JWT
# =====================================

ACCESS_TOKEN_EXPIRE_MINUTES = 60

# =====================================
# FILE UPLOAD
# =====================================

UPLOAD_FOLDER = "static/uploads"

ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
}

ALLOWED_DOCUMENT_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
}