from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

# Import get_db và Model User của bạn
from backend.src.config.database import get_db
from backend.src.models.user import User

# Phải khớp với SECRET_KEY và ALGORITHM bên auth_service.py
SECRET_KEY = "your_super_secret_key_here_please_change_it" 
ALGORITHM = "HS256"

# Chỉ định đường dẫn login để Swagger UI hiện nút "Authorize" (ổ khóa)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Middleware: Giải mã token, lấy thông tin user từ DB
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token không hợp lệ hoặc đã hết hạn.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_admin(current_user: User = Depends(get_current_user)):
    """
    Middleware: Dành riêng cho Admin
    """
    # Giả sử trong bảng User bạn có trường role (ví dụ: role = "admin" hoặc "user")
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập (Yêu cầu quyền Admin)."
        )
    return current_user