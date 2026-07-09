import os
import sys
import subprocess
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker, Session

# --- TỰ ĐỘNG KIỂM TRA VÀ CÀI ĐẶT THƯ VIỆN PHỤ THUỘC ---
try:
    from dotenv import load_dotenv
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv"])
    from dotenv import load_dotenv

try:
    from google import genai
    from google.genai import types
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-genai"])
    from google import genai
    from google.genai import types

# --- Nạp biến môi trường từ file .env ---
load_dotenv()

# ==========================================================
# 1. THIẾT LẬP ĐƯỜNG DẪN IMPORT MODULE HỆ THỐNG
# ==========================================================
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# ==========================================================
# 2. KHỞI TẠO FASTAPI APP
# ==========================================================
app = FastAPI(title="AITasker Backend", version="2.2.0")

# ==========================================================
# 3. CẤU HÌNH DATABASE & MODELS
# ==========================================================
from backend.src.config.database import Base, engine
from backend.src.domain.exceptions import AppError

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import Models để phục vụ khởi tạo bảng tự động
import backend.src.models.auth
import backend.src.models.category
import backend.src.models.enterprise
import backend.src.models.expert
import backend.src.models.skill
import backend.src.models.project
import backend.src.models.proposal
import backend.src.models.review

from backend.src.presentation import router

# ==========================================================
# 4. CẤU HÌNH GOOGLE GEMINI AI
# ==========================================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSy...")
ai_client = genai.Client(api_key=GEMINI_API_KEY)

# ĐÃ ĐỒNG BỘ: Đổi từ 'prompt' sang 'message' để khớp 100% với Frontend React
class ChatRequest(BaseModel):
    message: str

# ==========================================================
# 5. MIDDLEWARES & HÀM KHỞI CHẠY
# ==========================================================
@app.on_event("startup")
async def startup():
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    print("AITasker Backend started successfully.")

if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(SessionMiddleware, secret_key="change-me-secret-key")

# CẤU HÌNH CORS CHUẨN XÁC: Chỉ định rõ nguồn gốc từ Frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail},
    )

# ==========================================================
# 6. API CHATBOT (Đã cấu hình đồng bộ)
# ==========================================================
@app.post("/api/chat", tags=["Chatbot"])
async def chat_with_enterprise_data(request: ChatRequest, session: Session = Depends(get_db)):
    if not GEMINI_API_KEY or GEMINI_API_KEY == "AIzaSy...":
        raise HTTPException(
            status_code=503, 
            detail="Dịch vụ AI chưa sẵn sàng. Hãy cấu hình GEMINI_API_KEY hợp lệ trong file .env!"
        )

    try:
        context_prompt = f"""
        Bạn là 'AI Enterprise Assistant' - Trợ lý AI tối cao điều hành toàn bộ nền tảng hệ thống 'AI TASKER'.
        Hãy xưng hô lịch sự với người dùng là 'Admin Khanh'.

        Câu hỏi của Admin Khanh: {request.message}
        """

        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=context_prompt,
        )
        return {"reply": response.text}

    except Exception as e:
        print(f"❌ LỖI HỆ THỐNG CHATBOT: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"reply": "🤖 Hệ thống xử lý thông tin đang bận tối ưu cấu trúc dữ liệu. Xin hãy thử lại sau giây lát!"}
        )

# ==========================================================
# 7. ROUTERS KHÁC (Chứa các endpoint /projects, /experts thực tế)
# ==========================================================
# Thêm prefix="/api" để đồng bộ tuyệt đối với tệp axiosClient của Frontend
app.include_router(router, prefix="/api")

@app.get("/", tags=["Root"])
async def root():
    return {"status": "running", "message": "AITasker Backend API hoạt động hoàn hảo"}

# ==========================================================
# 8. KHỞI CHẠY SERVER
# ==========================================================
if __name__ == "__main__":
    import uvicorn
    # Giữ nguyên cổng 5000 ổn định hệ thống
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)