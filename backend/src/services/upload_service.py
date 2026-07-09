import os
import shutil
import uuid

from fastapi import HTTPException, UploadFile


class UploadService:

    ALLOWED_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".pdf",
        ".doc",
        ".docx",
    }

    def __init__(self):

        self.upload_folder = "static/uploads"

        os.makedirs(self.upload_folder, exist_ok=True)

    # =====================================================
    # VALIDATE FILE
    # =====================================================

    def validate_file(self, file: UploadFile):

        extension = os.path.splitext(file.filename)[1].lower()

        if extension not in self.ALLOWED_EXTENSIONS:

            raise HTTPException(
                status_code=400,
                detail="File type is not supported."
            )

    # =====================================================
    # SAVE FILE
    # =====================================================

    def save_file(
        self,
        file: UploadFile,
        folder: str,
    ):

        self.validate_file(file)

        upload_path = os.path.join(
            self.upload_folder,
            folder,
        )

        os.makedirs(upload_path, exist_ok=True)

        extension = os.path.splitext(file.filename)[1]

        filename = f"{uuid.uuid4()}{extension}"

        file_path = os.path.join(
            upload_path,
            filename,
        )

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer,
            )

        return file_path.replace("\\", "/")

    # =====================================================
    # USER AVATAR
    # =====================================================

    def upload_avatar(
        self,
        file: UploadFile,
    ):

        return self.save_file(
            file,
            "avatars",
        )

    # =====================================================
    # ENTERPRISE LOGO
    # =====================================================

    def upload_logo(
        self,
        file: UploadFile,
    ):

        return self.save_file(
            file,
            "logos",
        )

    # =====================================================
    # EXPERT CV
    # =====================================================

    def upload_cv(
        self,
        file: UploadFile,
    ):

        return self.save_file(
            file,
            "cv",
        )

    # =====================================================
    # PORTFOLIO
    # =====================================================

    def upload_portfolio(
        self,
        file: UploadFile,
    ):

        return self.save_file(
            file,
            "portfolio",
        )

    # =====================================================
    # DELETE FILE
    # =====================================================

    def delete_file(
        self,
        file_path: str,
    ):

        if os.path.exists(file_path):
            os.remove(file_path)

            return True

        return False