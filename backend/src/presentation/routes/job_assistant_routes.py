from __future__ import annotations

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from backend.src.schemas.job_assistant import (
    JobAssistantGenerateRequest,
    JobAssistantResult,
)
from backend.src.services.job_assistant_service import (
    job_assistant_service,
)


router = APIRouter(
    tags=["AI Job Assistant"],
)


# ==========================================================
# HEALTH
# ==========================================================

@router.get(
    "/health",
)
def health():
    """
    Kiểm tra trạng thái AI Job Assistant.
    """

    return job_assistant_service.health()


# ==========================================================
# GENERATE PROJECT
# ==========================================================

@router.post(
    "/generate",
    response_model=JobAssistantResult,
)
def generate_project(
    data: JobAssistantGenerateRequest,
):
    """
    AI sinh yêu cầu dự án từ ý tưởng doanh nghiệp.

    Input:
        - idea
        - budget_hint
        - timeline_hint
        - category_hint
        - preferred_skills

    Output:
        - Project suggestion
        - Budget
        - Timeline
        - Milestones
        - Acceptance criteria
        - Project payload
    """

    try:
        return job_assistant_service.generate(
            data
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "AI Job Assistant không thể tạo "
                "gợi ý dự án."
            ),
        )


# ==========================================================
# QUICK GENERATE
# ==========================================================

@router.post(
    "/quick-generate",
    response_model=JobAssistantResult,
)
def quick_generate(
    idea: str,
):
    """
    Sinh nhanh dự án chỉ từ ý tưởng.

    Ví dụ:

    POST /job-assistant/quick-generate?idea=Tôi muốn xây chatbot AI
    """

    request = JobAssistantGenerateRequest(
        idea=idea,
    )

    try:
        return job_assistant_service.generate(
            request
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Không thể sinh dự án."
            ),
        )


# ==========================================================
# PROJECT TEMPLATE
# ==========================================================

@router.get(
    "/template",
)
def template():
    """
    Trả về template để frontend hiển thị.
    """

    return {
        "idea": "",
        "category_hint": "",
        "budget_hint": None,
        "timeline_hint": None,
        "preferred_skills": [],
        "language": "vi",
        "detail_level": "STANDARD",
        "include_milestones": True,
        "include_risks": True,
        "include_acceptance_criteria": True,
    }


# ==========================================================
# SUPPORTED LANGUAGES
# ==========================================================

@router.get(
    "/languages",
)
def supported_languages():
    return {
        "languages": [
            {
                "code": "vi",
                "name": "Tiếng Việt",
            },
            {
                "code": "en",
                "name": "English",
            },
        ]
    }


# ==========================================================
# DETAIL LEVELS
# ==========================================================

@router.get(
    "/detail-levels",
)
def detail_levels():
    return {
        "levels": [
            "BASIC",
            "STANDARD",
            "DETAILED",
        ]
    }