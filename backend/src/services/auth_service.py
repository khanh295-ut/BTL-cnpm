from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import bcrypt

from backend.src.config.security import SECRET_KEY, ALGORITHM
from backend.src.infrastructure.repositories import SQLAlchemyAuthRepository
from backend.src.models.auth import User
from backend.src.schemas.auth import UserCreate, LoginRequest
from backend.src.models.token_blacklist import RevokedToken
from datetime import datetime

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7


class AuthService:
    
    # ==========================================
    # CÁC HÀM HỖ TRỢ (HELPER METHODS)
    # ==========================================
    def get_password_hash(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

    def create_jwt_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
            
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    # ==========================================
    # LOGIC CHÍNH ĐƯỢC GỌI TỪ ROUTER
    # ==========================================
    def register(self, db: Session, data: UserCreate):
        repo = SQLAlchemyAuthRepository(db)

        if repo.get_user_by_username(data.username):
            raise ValueError("Username này đã được đăng ký.")

        if repo.get_user_by_email(data.email):
            raise ValueError("Email này đã được đăng ký.")

        user = User(
            username=data.username.strip(),
            email=data.email.lower().strip(),
        )

        user.set_password(data.password)
        user.full_name = data.full_name.strip() if data.full_name else None
        user.bio = data.bio.strip() if data.bio else None

        default_role = repo.ensure_role("User", "Standard user role")
        user.roles.append(default_role)

        repo.save_user(user)
        repo.commit()
        db.refresh(user)

        return user

    def login(self, db: Session, data: LoginRequest):
        user = (
            db.query(User)
            .filter(
                or_(
                    User.email == data.login.lower().strip(),
                    User.username == data.login.strip(),
                )
            )
            .first()
        )

        if not user or not user.check_password(data.password):
            return None

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "roles": [role.name for role in user.roles],
        }

        access_token = self.create_jwt_token(
            data=token_data,
            expires_delta=access_token_expires,
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "full_name": getattr(user, "full_name", None),
                "bio": getattr(user, "bio", None),
                "roles": [role.name for role in user.roles],
            },
        }

    def forgot_password(self, db: Session, email: str):
        # 1. Kiểm tra user có tồn tại không
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None

        # 2. Tạo một Token đặc biệt để reset password (chỉ sống 15 phút)
        reset_token_expires = timedelta(minutes=15)
        reset_token = self.create_jwt_token(
            data={"sub": str(user.id), "purpose": "reset_password"},
            expires_delta=reset_token_expires
        )
        
        # LƯU Ý: Ở ứng dụng thực tế, bạn sẽ gọi EmailService ở đây để gửi reset_token đi
        
        return reset_token

    def reset_password(self, db: Session, token: str, new_password: str) -> bool:
        try:
            # 1. Giải mã token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            purpose = payload.get("purpose")
            
            if user_id is None or purpose != "reset_password":
                return False
                
        except JWTError:
            return False

        # 2. Tìm user trong DB
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False

        user.set_password(new_password)
        db.commit()
        
        return True

    def logout(self, db: Session, token: str) -> bool:
        """Blacklist the provided JWT token so it can no longer be used."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            return False

        exp = payload.get("exp")
        expires_at = None
        try:
            if exp is not None:
                # exp is a timestamp (int)
                expires_at = datetime.utcfromtimestamp(int(exp))
        except Exception:
            expires_at = None

        # store the raw token; unique constraint prevents duplicates
        revoked = RevokedToken(token=token, expires_at=expires_at)
        db.add(revoked)
        db.commit()

        return True