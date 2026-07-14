import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:123456@localhost:5432/aitasker",
)

engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "False").lower() == "true",
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
)

Base = declarative_base()


def init_db():
    """
    Import tất cả models để SQLAlchemy đăng ký mapper
    trước khi tạo bảng.
    """

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

    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Dependency dùng trong FastAPI.
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()