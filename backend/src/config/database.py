import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Tải các biến môi trường từ file .dotenv
load_dotenv()

# Cấu hình URL kết nối Database (Ưu tiên lấy từ file .env, nếu không có sẽ dùng mặc định)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:123456@localhost:5432/aitasker",
)

# Khởi tạo Engine kết nối cơ sở dữ liệu
engine = create_engine(
    DATABASE_URL,
    echo=True,          # In các câu lệnh SQL ra Terminal để tiện debug
    pool_pre_ping=True, # Tự động kiểm tra và phục hồi kết nối nếu bị ngắt quãng
)

# Cấu hình bộ quản lý phiên làm việc (Session) với DB
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Lớp Base để các Model kế thừa nhằm đăng ký cấu trúc bảng
Base = declarative_base()


def init_db():
    """
    Import toàn bộ models để SQLAlchemy đăng ký mapper
    trước khi tạo bảng.
    
    Đã được đồng nhất tiền tố 'backend.' để tránh lỗi trùng lặp Registry.
    """
    # Import đồng nhất tất cả các Model trong hệ thống
    import backend.src.models.association
    import backend.src.models.auth
    import backend.src.models.category
    import backend.src.models.enterprise
    import backend.src.models.expert
    import backend.src.models.project
    import backend.src.models.proposal
    import backend.src.models.review
    import backend.src.models.skill
    import backend.src.models.contract

    # Tạo toàn bộ các bảng trong Database nếu chưa tồn tại
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Dependency cung cấp Session kết nối Database cho các API Routes.
    Đảm bảo Session luôn đóng lại sau khi request xử lý xong.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()