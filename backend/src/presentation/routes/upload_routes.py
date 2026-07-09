from fastapi import APIRouter, UploadFile, File, HTTPException, status

from backend.src.services.upload_service import UploadService

router = APIRouter(
    prefix="/uploads",
    tags=["Uploads"],
)

service = UploadService()


# =====================================================
# UPLOAD AVATAR
# =====================================================

@router.post(
    "/avatar",
    status_code=status.HTTP_201_CREATED,
)
def upload_avatar(
    file: UploadFile = File(...),
):

    try:

        path = service.upload_avatar(file)

        return {
            "message": "Avatar uploaded successfully.",
            "file_url": path,
        }

    except HTTPException as e:
        raise e


# =====================================================
# UPLOAD LOGO
# =====================================================

@router.post(
    "/logo",
    status_code=status.HTTP_201_CREATED,
)
def upload_logo(
    file: UploadFile = File(...),
):

    try:

        path = service.upload_logo(file)

        return {
            "message": "Logo uploaded successfully.",
            "file_url": path,
        }

    except HTTPException as e:
        raise e


# =====================================================
# UPLOAD CV
# =====================================================

@router.post(
    "/cv",
    status_code=status.HTTP_201_CREATED,
)
def upload_cv(
    file: UploadFile = File(...),
):

    try:

        path = service.upload_cv(file)

        return {
            "message": "CV uploaded successfully.",
            "file_url": path,
        }

    except HTTPException as e:
        raise e


# =====================================================
# UPLOAD PORTFOLIO
# =====================================================

@router.post(
    "/portfolio",
    status_code=status.HTTP_201_CREATED,
)
def upload_portfolio(
    file: UploadFile = File(...),
):

    try:

        path = service.upload_portfolio(file)

        return {
            "message": "Portfolio uploaded successfully.",
            "file_url": path,
        }

    except HTTPException as e:
        raise e