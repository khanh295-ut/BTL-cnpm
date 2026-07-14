"""
AITasker Chat Routes

Endpoint cuối cùng:
POST /api/chat

Quy ước:
- app.py thêm prefix /api.
- all_routes.py thêm prefix /chat.
- File này không khai báo prefix.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Request, status
from google import genai
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.services.chatbot_service import ChatbotService


# ==========================================================
# ENVIRONMENT
# ==========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash",
)


# ==========================================================
# LOGGING
# ==========================================================

logger = logging.getLogger("AITasker.ChatRoutes")


# ==========================================================
# GEMINI CLIENT
# ==========================================================

ai_client: Optional[genai.Client] = None

if GEMINI_API_KEY:
    try:
        ai_client = genai.Client(
            api_key=GEMINI_API_KEY,
        )

        logger.info(
            "Gemini client for chatbot initialized successfully."
        )

    except Exception as exc:
        logger.exception(
            "Không thể khởi tạo Gemini chatbot client: %s",
            exc,
        )
else:
    logger.warning(
        "GEMINI_API_KEY chưa được cấu hình cho chatbot."
    )


# ==========================================================
# SERVICE
# ==========================================================

chatbot_service = ChatbotService(
    ai_client=ai_client,
    model_name=GEMINI_MODEL,
)


# ==========================================================
# ROUTER
# /api được thêm trong app.py.
# /chat được thêm trong all_routes.py.
# ==========================================================

router = APIRouter(
    tags=["AI Chatbot"],
)


# ==========================================================
# REQUEST AND RESPONSE SCHEMAS
# ==========================================================

class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=5000,
        description="Câu hỏi gửi tới trợ lý AI AITasker",
        examples=[
            "Dự án cao tốc có ngân sách bao nhiêu?",
        ],
    )


class ChatResponse(BaseModel):
    success: bool
    reply: str
    source: str = "database"
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None


# ==========================================================
# HELPER
# ==========================================================

def create_database_prompt(
    question: str,
    database_context: str,
) -> str:
    """
    Tạo prompt buộc Gemini chỉ trả lời theo dữ liệu
    được đọc từ PostgreSQL.
    """

    return f"""
Bạn là trợ lý AI nội bộ của nền tảng AITasker.

QUY TẮC BẮT BUỘC:

1. Chỉ được trả lời dựa trên dữ liệu AITasker cung cấp bên dưới.
2. Không được dùng kiến thức bên ngoài để thay thế dữ liệu hệ thống.
3. Không được tự tạo hoặc phỏng đoán số liệu.
4. Không được nhầm dữ liệu trong AITasker với sự kiện ngoài đời thực.
5. Nếu dữ liệu không tồn tại, hãy trả lời chính xác:
   "Tôi không tìm thấy thông tin này trong hệ thống AITasker."
6. Trả lời bằng tiếng Việt.
7. Trả lời ngắn gọn, rõ ràng và chính xác.
8. Số tiền trong hệ thống được hiểu là VNĐ.
9. Khi hỏi số lượng, phải đếm đúng dữ liệu được cung cấp.
10. Không được nói rằng bạn không thể truy cập database,
    vì dữ liệu database đã được cung cấp trong phần ngữ cảnh.

============================================================
DỮ LIỆU HIỆN TẠI TRONG DATABASE AITASKER
============================================================

{database_context}

============================================================
CÂU HỎI CỦA NGƯỜI DÙNG
============================================================

{question}
""".strip()


def normalize_service_response(
    result: dict[str, Any],
) -> ChatResponse:
    """
    Chuẩn hóa kết quả trả về từ ChatbotService.
    """

    return ChatResponse(
        success=bool(
            result.get("success", True)
        ),
        reply=str(
            result.get(
                "reply",
                "Tôi không tìm thấy thông tin này "
                "trong hệ thống AITasker.",
            )
        ),
        source=str(
            result.get(
                "source",
                "database",
            )
        ),
        entity_type=(
            str(result["entity_type"])
            if result.get("entity_type") is not None
            else None
        ),
        entity_id=(
            str(result["entity_id"])
            if result.get("entity_id") is not None
            else None
        ),
    )


# ==========================================================
# CHAT
# ==========================================================

@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Chat với trợ lý AI AITasker",
)
def chat(
    payload: ChatRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Quy trình xử lý:

    1. Đọc dữ liệu thật từ PostgreSQL.
    2. Thử trả lời trực tiếp bằng ChatbotService.
    3. Nếu câu hỏi phức tạp, tạo context database.
    4. Gửi context cho Gemini để diễn đạt câu trả lời.
    """

    question = payload.message.strip()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nội dung câu hỏi không được để trống.",
        )

    # ======================================================
    # LOAD DATABASE DATA
    # ======================================================

    try:
        system_data = chatbot_service.load_system_data(
            db
        )

    except Exception as exc:
        db.rollback()

        logger.exception(
            "Không thể đọc dữ liệu hệ thống cho chatbot: %s",
            exc,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Không thể đọc dữ liệu từ hệ thống AITasker."
            ),
        ) from exc

    # ======================================================
    # DIRECT DATABASE ANSWER
    # ======================================================

    try:
        direct_answer = chatbot_service.answer_directly(
            question=question,
            data=system_data,
            request=request,
        )

    except Exception as exc:
        db.rollback()

        logger.exception(
            "Lỗi xử lý câu trả lời trực tiếp từ database: %s",
            exc,
        )

        direct_answer = None

    if direct_answer is not None:
        return normalize_service_response(
            direct_answer
        )

    # ======================================================
    # GEMINI FALLBACK
    # ======================================================

    if ai_client is None:
        return ChatResponse(
            success=True,
            reply=(
                "Tôi không tìm thấy thông tin này "
                "trong hệ thống AITasker."
            ),
            source="database",
        )

    try:
        database_context = (
            chatbot_service.build_database_context(
                system_data
            )
        )

    except Exception as exc:
        logger.exception(
            "Không thể xây dựng database context: %s",
            exc,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Không thể xây dựng dữ liệu ngữ cảnh "
                "cho trợ lý AI."
            ),
        ) from exc

    prompt = create_database_prompt(
        question=question,
        database_context=database_context,
    )

    try:
        response = ai_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )

        answer = (
            getattr(response, "text", "")
            or (
                "Tôi không tìm thấy thông tin này "
                "trong hệ thống AITasker."
            )
        ).strip()

        return ChatResponse(
            success=True,
            reply=answer,
            source="database_and_gemini",
        )

    except Exception as exc:
        logger.exception(
            "Không thể gọi Gemini AI: %s",
            exc,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể kết nối tới Gemini AI.",
        ) from exc


# ==========================================================
# CHATBOT HEALTH
# ==========================================================

@router.get(
    "/health",
    summary="Kiểm tra trạng thái chatbot",
)
def chatbot_health(
    db: Session = Depends(get_db),
):
    try:
        system_data = chatbot_service.load_system_data(
            db
        )

        return {
            "success": True,
            "status": "available",
            "gemini": (
                "available"
                if ai_client is not None
                else "disabled"
            ),
            "database": "connected",
            "records": {
                key: len(value)
                for key, value in system_data.items()
            },
        }

    except Exception as exc:
        db.rollback()

        logger.exception(
            "Chatbot health check failed: %s",
            exc,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chatbot health check failed.",
        ) from exc