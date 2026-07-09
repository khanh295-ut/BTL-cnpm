from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt

# Import Model DB và Schema của bạn
from backend.src.models.auth import User
from backend.src.schemas.auth import UserCreate, LoginRequest

# Cấu hình bảo mật
# Trong thực tế, SECRET_KEY nên được đưa vào file .env
SECRET_KEY = "your_super_secret_key_here_please_change_it" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # Token sống 7 ngày

# Công cụ mã hóa mật khẩu bằng thuật toán bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    
    # ==========================================
    # CÁC HÀM HỖ TRỢ (HELPER METHODS)
    # ==========================================
    def get_password_hash(self, password: str) -> str:
        # Ép độ dài tối đa 72 ký tự để triệt tiêu hoàn toàn lỗi của thư viện passlib/bcrypt
        safe_password = password[:72]
        return pwd_context.hash(safe_password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        # Cắt 72 ký tự tương tự như lúc tạo mật khẩu để khớp mã hash
        safe_password = plain_password[:72]
        return pwd_context.verify(safe_password, hashed_password)

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
        # 1. Kiểm tra email đã tồn tại chưa
        existing_user = db.query(User).filter(User.email == data.email).first()
        if existing_user:
            raise ValueError("Email này đã được đăng ký.")

        # 2. Mã hóa mật khẩu
        hashed_password = self.get_password_hash(data.password)

        # 3. Lưu vào Database (SỬ DỤNG ĐÚNG TÊN CỘT: password_hash)
        new_user = User(
            username=data.username,
            email=data.email,
            password_hash=hashed_password,
            full_name=data.full_name,
            bio=data.bio
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user

    def login(self, db: Session, data: LoginRequest):
        # 1. Tìm user theo email
        user = db.query(User).filter(User.email == data.email).first()
        
        # 2. Nếu user không tồn tại hoặc sai mật khẩu -> Return None 
        # (SỬ DỤNG ĐÚNG TÊN CỘT: user.password_hash)
        if not user or not self.verify_password(data.password, user.password_hash):
            return None

        # 3. Tạo Access Token (JWT)
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        token_data = {"sub": str(user.id), "email": user.email} 
        
        access_token = self.create_jwt_token(
            data=token_data, 
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
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

        # 3. Cập nhật mật khẩu mới (SỬ DỤNG ĐÚNG TÊN CỘT: password_hash)
        user.password_hash = self.get_password_hash(new_password)
        db.commit()
        
        return True