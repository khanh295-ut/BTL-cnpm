# backend/src/presentation/routes/upload_routes.py

from fastapi import APIRouter, File, UploadFile, status

from backend.src.services.upload_service import UploadService


# ==========================================================
# ROUTER
# Prefix /upload hoặc /uploads được thêm trong all_routes.py.
# Prefix /api được thêm trong app.py.
# ==========================================================

router = APIRouter(
    tags=["Uploads"],
)

service = UploadService()


# ==========================================================
# UPLOAD AVATAR
# ==========================================================

@router.post(
    "/avatar",
    status_code=status.HTTP_201_CREATED,
)
def upload_avatar(
    file: UploadFile = File(...),
):
    path = service.upload_avatar(file)

    return {
        "message": "Avatar uploaded successfully.",
        "file_url": path,
    }


# ==========================================================
# UPLOAD LOGO
# ==========================================================

@router.post(
    "/logo",
    status_code=status.HTTP_201_CREATED,
)
def upload_logo(
    file: UploadFile = File(...),
):
    path = service.upload_logo(file)

    return {
        "message": "Logo uploaded successfully.",
        "file_url": path,
    }


# ==========================================================
# UPLOAD CV
# ==========================================================

@router.post(
    "/cv",
    status_code=status.HTTP_201_CREATED,
)
def upload_cv(
    file: UploadFile = File(...),
):
    path = service.upload_cv(file)

    return {
        "message": "CV uploaded successfully.",
        "file_url": path,
    }


# ==========================================================
# UPLOAD PORTFOLIO
# ==========================================================

@router.post(
    "/portfolio",
    status_code=status.HTTP_201_CREATED,
)
def upload_portfolio(
    file: UploadFile = File(...),
):
    path = service.upload_portfolio(file)

    return {
        "message": "Portfolio uploaded successfully.",
        "file_url": path,
    }