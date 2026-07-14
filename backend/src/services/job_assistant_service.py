# backend/src/services/job_assistant_service.py

from __future__ import annotations

import json
import logging
import os
import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any

from backend.src.schemas.job_assistant import (
    JobAssistantBudgetSuggestion,
    JobAssistantGenerateRequest,
    JobAssistantGenerateResponse,
    JobAssistantMilestone,
    JobAssistantProjectPayload,
    JobAssistantResult,
    JobAssistantTimelineSuggestion,
)


logger = logging.getLogger(
    "AITasker.JobAssistantService"
)


class JobAssistantService:
    """
    AI Job Assistant của hệ thống AITasker.

    Chức năng:

    - Nhận ý tưởng dự án từ doanh nghiệp.
    - Sinh tiêu đề và mô tả dự án.
    - Đề xuất ngân sách.
    - Đề xuất thời gian thực hiện.
    - Xác định kỹ năng và công nghệ.
    - Sinh milestones.
    - Sinh tiêu chí nghiệm thu.
    - Phân tích rủi ro.
    - Tạo payload dùng để tạo Project.

    Service ưu tiên gọi Gemini.

    Nếu:
    - chưa cài google-genai,
    - chưa cấu hình GEMINI_API_KEY,
    - Gemini không phản hồi,
    - Gemini trả JSON sai,

    thì service sử dụng dữ liệu fallback để API không bị lỗi 500.
    """

    DEFAULT_MODEL = os.getenv(
        "GEMINI_MODEL",
        "gemini-2.5-flash",
    )

    DEFAULT_CURRENCY = "VND"

    MAX_DESCRIPTION_LENGTH = 10_000

    # ======================================================
    # INITIALIZATION
    # ======================================================

    def __init__(self) -> None:
        self.api_key = (
            os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
        )

        self.model_name = self.DEFAULT_MODEL
        self.client: Any | None = None
        self.genai_types: Any | None = None

        self._initialize_gemini_client()

    def _initialize_gemini_client(self) -> None:
        """
        Khởi tạo Gemini client.

        Không làm backend dừng khởi động nếu:
        - thiếu package;
        - thiếu API key;
        - cấu hình Gemini lỗi.
        """

        if not self.api_key:
            logger.warning(
                "GEMINI_API_KEY hoặc GOOGLE_API_KEY chưa được cấu hình. "
                "Job Assistant sẽ sử dụng fallback."
            )
            return

        try:
            from google import genai
            from google.genai import types

            self.client = genai.Client(
                api_key=self.api_key,
            )

            self.genai_types = types

            logger.info(
                "Gemini client for Job Assistant initialized "
                "successfully with model %s.",
                self.model_name,
            )

        except ImportError:
            logger.warning(
                "Package google-genai chưa được cài đặt. "
                "Job Assistant sẽ sử dụng fallback."
            )

        except Exception:
            logger.exception(
                "Không thể khởi tạo Gemini client cho Job Assistant. "
                "Service sẽ sử dụng fallback."
            )

            self.client = None
            self.genai_types = None

    # ======================================================
    # BASIC HELPERS
    # ======================================================

    @staticmethod
    def _clean_text(
        value: Any,
        default: str = "",
    ) -> str:
        if value is None:
            return default

        cleaned = str(value).strip()

        return cleaned or default

    @staticmethod
    def _normalize_language(
        value: str | None,
    ) -> str:
        normalized = str(
            value or "vi"
        ).strip().lower()

        if normalized not in {
            "vi",
            "en",
        }:
            return "vi"

        return normalized

    @staticmethod
    def _normalize_detail_level(
        value: str | None,
    ) -> str:
        normalized = str(
            value or "STANDARD"
        ).strip().upper()

        if normalized not in {
            "BASIC",
            "STANDARD",
            "DETAILED",
        }:
            return "STANDARD"

        return normalized

    @staticmethod
    def _decimal(
        value: Any,
        default: Decimal = Decimal("0.00"),
    ) -> Decimal:
        if value is None:
            return default

        if isinstance(value, Decimal):
            return value

        try:
            normalized = str(value).replace(
                ",",
                "",
            ).strip()

            return Decimal(normalized)

        except (
            InvalidOperation,
            TypeError,
            ValueError,
        ):
            return default

    @staticmethod
    def _round_money(
        value: Decimal,
    ) -> Decimal:
        """
        Làm tròn tiền VND đến hàng nghìn.
        """

        if value <= Decimal("0"):
            return Decimal("0")

        return (
            value
            / Decimal("1000")
        ).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        ) * Decimal("1000")

    @staticmethod
    def _clamp_int(
        value: Any,
        minimum: int,
        maximum: int,
        default: int,
    ) -> int:
        try:
            number = int(value)
        except (
            TypeError,
            ValueError,
        ):
            number = default

        return max(
            minimum,
            min(number, maximum),
        )

    @staticmethod
    def _unique_strings(
        values: Any,
        *,
        maximum_items: int = 30,
    ) -> list[str]:
        if values is None:
            return []

        if isinstance(values, str):
            values = re.split(
                r"[,;\n|]+",
                values,
            )

        if not isinstance(
            values,
            (
                list,
                tuple,
                set,
            ),
        ):
            values = [
                values
            ]

        result: list[str] = []
        seen: set[str] = set()

        for raw_value in values:
            if isinstance(
                raw_value,
                dict,
            ):
                raw_value = (
                    raw_value.get("name")
                    or raw_value.get("title")
                    or raw_value.get("value")
                    or ""
                )

            item = str(
                raw_value or ""
            ).strip()

            if not item:
                continue

            normalized = item.casefold()

            if normalized in seen:
                continue

            seen.add(normalized)
            result.append(item)

            if len(result) >= maximum_items:
                break

        return result

    @staticmethod
    def _truncate(
        value: str,
        maximum_length: int,
    ) -> str:
        cleaned = value.strip()

        if len(cleaned) <= maximum_length:
            return cleaned

        return cleaned[
            : maximum_length - 3
        ].rstrip() + "..."

    # ======================================================
    # PROMPT
    # ======================================================

    def _build_prompt(
        self,
        data: JobAssistantGenerateRequest,
    ) -> str:
        language = self._normalize_language(
            data.language
        )

        detail_level = self._normalize_detail_level(
            data.detail_level
        )

        preferred_skills = (
            ", ".join(data.preferred_skills)
            if data.preferred_skills
            else "Không có"
        )

        budget_hint = (
            str(data.budget_hint)
            if data.budget_hint is not None
            else "Không có"
        )

        timeline_hint = (
            str(data.timeline_hint)
            if data.timeline_hint is not None
            else "Không có"
        )

        category_hint = (
            data.category_hint
            if data.category_hint
            else "Không có"
        )

        output_language = (
            "Tiếng Việt"
            if language == "vi"
            else "English"
        )

        milestone_instruction = (
            "Sinh danh sách milestones hợp lý."
            if data.include_milestones
            else "Trả milestones là danh sách rỗng."
        )

        risk_instruction = (
            "Phân tích các rủi ro chính."
            if data.include_risks
            else "Trả risks là danh sách rỗng."
        )

        acceptance_instruction = (
            "Sinh tiêu chí nghiệm thu rõ ràng, kiểm chứng được."
            if data.include_acceptance_criteria
            else "Trả acceptance_criteria là danh sách rỗng."
        )

        return f"""
Bạn là AI Job Assistant của nền tảng AITasker, chuyên hỗ trợ
doanh nghiệp mô tả dự án tự động hóa bằng AI.

Hãy phân tích ý tưởng dưới đây và chuyển thành một yêu cầu dự án
chuyên nghiệp, thực tế, rõ ràng và có thể đăng lên marketplace.

NGÔN NGỮ ĐẦU RA:
{output_language}

MỨC ĐỘ CHI TIẾT:
{detail_level}

Ý TƯỞNG DỰ ÁN:
{data.idea}

THÔNG TIN GỢI Ý:
- Danh mục: {category_hint}
- Ngân sách gợi ý: {budget_hint} VND
- Thời gian gợi ý: {timeline_hint} ngày
- Kỹ năng ưu tiên: {preferred_skills}

YÊU CẦU NGHIỆP VỤ:
1. Không đưa ra nội dung chung chung.
2. Ngân sách phải thực tế đối với thị trường phát triển phần mềm AI.
3. Tiền tệ phải là VND.
4. Timeline phải nằm trong khoảng hợp lý.
5. Kỹ năng phải là tên kỹ năng cụ thể.
6. Milestones phải bao phủ toàn bộ timeline.
7. Tổng percentage của milestones phải bằng 100.
8. Acceptance criteria phải đo lường hoặc kiểm tra được.
9. Không dùng markdown.
10. Không thêm giải thích bên ngoài JSON.
11. {milestone_instruction}
12. {risk_instruction}
13. {acceptance_instruction}

Trả về duy nhất một JSON object có chính xác cấu trúc:

{{
  "title": "Tên dự án",
  "short_description": "Mô tả ngắn",
  "description": "Mô tả dự án chi tiết",
  "category": "Danh mục phù hợp",
  "objectives": [
    "Mục tiêu 1"
  ],
  "scope_included": [
    "Nội dung nằm trong phạm vi"
  ],
  "scope_excluded": [
    "Nội dung ngoài phạm vi"
  ],
  "required_skills": [
    "Python"
  ],
  "recommended_technologies": [
    "FastAPI"
  ],
  "budget": {{
    "minimum": 10000000,
    "recommended": 15000000,
    "maximum": 22000000,
    "currency": "VND",
    "explanation": "Giải thích ngân sách"
  }},
  "timeline": {{
    "minimum_days": 20,
    "recommended_days": 30,
    "maximum_days": 45,
    "explanation": "Giải thích timeline"
  }},
  "milestones": [
    {{
      "title": "Phân tích yêu cầu",
      "description": "Mô tả",
      "duration_days": 5,
      "percentage": 15,
      "deliverables": [
        "Tài liệu yêu cầu"
      ]
    }}
  ],
  "acceptance_criteria": [
    "Tiêu chí nghiệm thu"
  ],
  "risks": [
    "Rủi ro"
  ],
  "assumptions": [
    "Giả định"
  ],
  "suggested_questions_for_expert": [
    "Câu hỏi dành cho chuyên gia"
  ]
}}
""".strip()

    # ======================================================
    # GEMINI CALL
    # ======================================================

    def _call_gemini(
        self,
        prompt: str,
    ) -> str:
        if self.client is None:
            raise RuntimeError(
                "Gemini client is unavailable."
            )

        try:
            config = None

            if self.genai_types is not None:
                config = self.genai_types.GenerateContentConfig(
                    temperature=0.25,
                    top_p=0.9,
                    response_mime_type="application/json",
                )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config,
            )

            response_text = self._clean_text(
                getattr(
                    response,
                    "text",
                    None,
                )
            )

            if not response_text:
                raise ValueError(
                    "Gemini returned an empty response."
                )

            return response_text

        except Exception:
            logger.exception(
                "Gemini không thể sinh nội dung Job Assistant."
            )

            raise

    # ======================================================
    # JSON PARSING
    # ======================================================

    @staticmethod
    def _remove_code_fence(
        value: str,
    ) -> str:
        cleaned = value.strip()

        cleaned = re.sub(
            r"^```(?:json)?\s*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"\s*```$",
            "",
            cleaned,
        )

        return cleaned.strip()

    def _extract_json_object(
        self,
        value: str,
    ) -> dict[str, Any]:
        cleaned = self._remove_code_fence(
            value
        )

        try:
            parsed = json.loads(
                cleaned
            )

            if not isinstance(
                parsed,
                dict,
            ):
                raise ValueError(
                    "AI response must be a JSON object."
                )

            return parsed

        except json.JSONDecodeError:
            start_index = cleaned.find(
                "{"
            )

            end_index = cleaned.rfind(
                "}"
            )

            if (
                start_index == -1
                or end_index == -1
                or end_index <= start_index
            ):
                raise ValueError(
                    "Không tìm thấy JSON hợp lệ "
                    "trong phản hồi của AI."
                )

            json_text = cleaned[
                start_index : end_index + 1
            ]

            try:
                parsed = json.loads(
                    json_text
                )

            except json.JSONDecodeError as exc:
                raise ValueError(
                    "Gemini trả về JSON không hợp lệ."
                ) from exc

            if not isinstance(
                parsed,
                dict,
            ):
                raise ValueError(
                    "AI response must be a JSON object."
                )

            return parsed

    # ======================================================
    # PROJECT TYPE DETECTION
    # ======================================================

    def _detect_project_type(
        self,
        idea: str,
    ) -> str:
        normalized = idea.casefold()

        patterns: list[
            tuple[
                str,
                tuple[str, ...],
            ]
        ] = [
            (
                "Chatbot và trợ lý AI",
                (
                    "chatbot",
                    "trợ lý",
                    "assistant",
                    "tư vấn",
                    "hỏi đáp",
                    "llm",
                    "rag",
                ),
            ),
            (
                "Computer Vision",
                (
                    "camera",
                    "hình ảnh",
                    "nhận diện",
                    "computer vision",
                    "khuôn mặt",
                    "vật thể",
                    "ocr",
                ),
            ),
            (
                "Phân tích dữ liệu",
                (
                    "phân tích dữ liệu",
                    "dự báo",
                    "dashboard",
                    "business intelligence",
                    "data analytics",
                ),
            ),
            (
                "Tự động hóa quy trình",
                (
                    "tự động hóa",
                    "automation",
                    "quy trình",
                    "workflow",
                    "rpa",
                ),
            ),
            (
                "Xử lý ngôn ngữ tự nhiên",
                (
                    "nlp",
                    "văn bản",
                    "dịch",
                    "tóm tắt",
                    "phân loại nội dung",
                    "sentiment",
                ),
            ),
            (
                "Machine Learning",
                (
                    "machine learning",
                    "học máy",
                    "mô hình dự đoán",
                    "prediction",
                    "classification",
                ),
            ),
        ]

        for category, keywords in patterns:
            if any(
                keyword in normalized
                for keyword in keywords
            ):
                return category

        return "Giải pháp AI và tự động hóa"

    def _default_skills_for_category(
        self,
        category: str,
    ) -> list[str]:
        skill_map = {
            "Chatbot và trợ lý AI": [
                "Python",
                "FastAPI",
                "LLM",
                "RAG",
                "NLP",
                "PostgreSQL",
            ],
            "Computer Vision": [
                "Python",
                "PyTorch",
                "OpenCV",
                "Computer Vision",
                "FastAPI",
                "Docker",
            ],
            "Phân tích dữ liệu": [
                "Python",
                "Pandas",
                "SQL",
                "Machine Learning",
                "Data Visualization",
                "FastAPI",
            ],
            "Tự động hóa quy trình": [
                "Python",
                "FastAPI",
                "Workflow Automation",
                "API Integration",
                "PostgreSQL",
                "Docker",
            ],
            "Xử lý ngôn ngữ tự nhiên": [
                "Python",
                "NLP",
                "Transformers",
                "LLM",
                "FastAPI",
                "PostgreSQL",
            ],
            "Machine Learning": [
                "Python",
                "Scikit-learn",
                "Pandas",
                "Machine Learning",
                "FastAPI",
                "Docker",
            ],
        }

        return skill_map.get(
            category,
            [
                "Python",
                "FastAPI",
                "Artificial Intelligence",
                "API Integration",
                "PostgreSQL",
                "Docker",
            ],
        )

    # ======================================================
    # FALLBACK ESTIMATES
    # ======================================================

    def _estimate_complexity(
        self,
        data: JobAssistantGenerateRequest,
    ) -> str:
        idea_length = len(
            data.idea
        )

        idea_lower = data.idea.casefold()

        advanced_keywords = {
            "real-time",
            "thời gian thực",
            "nhiều người dùng",
            "microservice",
            "tích hợp",
            "doanh nghiệp",
            "bảo mật",
            "phân quyền",
            "rag",
            "llm",
            "fine-tuning",
            "computer vision",
            "dự báo",
        }

        keyword_count = sum(
            1
            for keyword in advanced_keywords
            if keyword in idea_lower
        )

        if (
            idea_length >= 500
            or keyword_count >= 4
        ):
            return "HIGH"

        if (
            idea_length >= 200
            or keyword_count >= 2
        ):
            return "MEDIUM"

        return "LOW"

    def _fallback_budget(
        self,
        data: JobAssistantGenerateRequest,
        complexity: str,
    ) -> JobAssistantBudgetSuggestion:
        if data.budget_hint is not None:
            recommended = self._decimal(
                data.budget_hint
            )
        else:
            default_budgets = {
                "LOW": Decimal("15000000"),
                "MEDIUM": Decimal("35000000"),
                "HIGH": Decimal("70000000"),
            }

            recommended = default_budgets[
                complexity
            ]

        recommended = max(
            recommended,
            Decimal("1000000"),
        )

        minimum = self._round_money(
            recommended
            * Decimal("0.75")
        )

        recommended = self._round_money(
            recommended
        )

        maximum = self._round_money(
            recommended
            * Decimal("1.40")
        )

        return JobAssistantBudgetSuggestion(
            minimum=minimum,
            recommended=recommended,
            maximum=maximum,
            currency=self.DEFAULT_CURRENCY,
            explanation=(
                "Ngân sách được ước tính dựa trên phạm vi, "
                "mức độ phức tạp, tích hợp hệ thống, kiểm thử "
                "và triển khai giải pháp AI."
            ),
        )

    def _fallback_timeline(
        self,
        data: JobAssistantGenerateRequest,
        complexity: str,
    ) -> JobAssistantTimelineSuggestion:
        if data.timeline_hint is not None:
            recommended_days = self._clamp_int(
                data.timeline_hint,
                1,
                365,
                30,
            )
        else:
            default_days = {
                "LOW": 21,
                "MEDIUM": 45,
                "HIGH": 90,
            }

            recommended_days = default_days[
                complexity
            ]

        minimum_days = max(
            1,
            int(
                recommended_days
                * 0.75
            ),
        )

        maximum_days = min(
            730,
            max(
                recommended_days,
                int(
                    recommended_days
                    * 1.40
                ),
            ),
        )

        return JobAssistantTimelineSuggestion(
            minimum_days=minimum_days,
            recommended_days=recommended_days,
            maximum_days=maximum_days,
            explanation=(
                "Timeline bao gồm phân tích yêu cầu, thiết kế, "
                "phát triển, tích hợp, kiểm thử và bàn giao."
            ),
        )

    # ======================================================
    # MILESTONE NORMALIZATION
    # ======================================================

    def _fallback_milestones(
        self,
        total_days: int,
        language: str,
    ) -> list[JobAssistantMilestone]:
        phases = [
            {
                "title_vi": "Phân tích yêu cầu",
                "title_en": "Requirements analysis",
                "description_vi": (
                    "Làm rõ nghiệp vụ, dữ liệu đầu vào, "
                    "phạm vi và tiêu chí nghiệm thu."
                ),
                "description_en": (
                    "Clarify business requirements, input data, "
                    "scope, and acceptance criteria."
                ),
                "percentage": Decimal("15"),
                "ratio": Decimal("0.15"),
                "deliverables_vi": [
                    "Tài liệu yêu cầu",
                    "Đặc tả phạm vi",
                ],
                "deliverables_en": [
                    "Requirements document",
                    "Scope specification",
                ],
            },
            {
                "title_vi": "Thiết kế giải pháp",
                "title_en": "Solution design",
                "description_vi": (
                    "Thiết kế kiến trúc, dữ liệu, API "
                    "và phương án AI."
                ),
                "description_en": (
                    "Design architecture, data flows, APIs, "
                    "and the AI approach."
                ),
                "percentage": Decimal("20"),
                "ratio": Decimal("0.20"),
                "deliverables_vi": [
                    "Thiết kế kiến trúc",
                    "Thiết kế cơ sở dữ liệu",
                ],
                "deliverables_en": [
                    "Architecture design",
                    "Database design",
                ],
            },
            {
                "title_vi": "Phát triển và tích hợp",
                "title_en": "Development and integration",
                "description_vi": (
                    "Xây dựng các chức năng chính và tích hợp "
                    "mô hình hoặc dịch vụ AI."
                ),
                "description_en": (
                    "Develop core features and integrate "
                    "AI models or services."
                ),
                "percentage": Decimal("40"),
                "ratio": Decimal("0.40"),
                "deliverables_vi": [
                    "Mã nguồn",
                    "API hoạt động",
                    "Mô-đun AI",
                ],
                "deliverables_en": [
                    "Source code",
                    "Working APIs",
                    "AI module",
                ],
            },
            {
                "title_vi": "Kiểm thử và hiệu chỉnh",
                "title_en": "Testing and refinement",
                "description_vi": (
                    "Kiểm thử chức năng, hiệu năng và "
                    "chất lượng kết quả AI."
                ),
                "description_en": (
                    "Test functionality, performance, "
                    "and AI output quality."
                ),
                "percentage": Decimal("15"),
                "ratio": Decimal("0.15"),
                "deliverables_vi": [
                    "Báo cáo kiểm thử",
                    "Phiên bản đã hiệu chỉnh",
                ],
                "deliverables_en": [
                    "Test report",
                    "Refined version",
                ],
            },
            {
                "title_vi": "Triển khai và bàn giao",
                "title_en": "Deployment and handover",
                "description_vi": (
                    "Triển khai hệ thống, hướng dẫn sử dụng "
                    "và bàn giao tài liệu."
                ),
                "description_en": (
                    "Deploy the system, provide user guidance, "
                    "and hand over documentation."
                ),
                "percentage": Decimal("10"),
                "ratio": Decimal("0.10"),
                "deliverables_vi": [
                    "Hệ thống triển khai",
                    "Tài liệu hướng dẫn",
                ],
                "deliverables_en": [
                    "Deployed system",
                    "User documentation",
                ],
            },
        ]

        result: list[JobAssistantMilestone] = []
        allocated_days = 0

        for index, phase in enumerate(
            phases
        ):
            if index == len(phases) - 1:
                duration_days = max(
                    1,
                    total_days
                    - allocated_days,
                )
            else:
                duration_days = max(
                    1,
                    int(
                        Decimal(total_days)
                        * phase["ratio"]
                    ),
                )

                allocated_days += duration_days

            if language == "en":
                title = phase["title_en"]
                description = phase[
                    "description_en"
                ]
                deliverables = phase[
                    "deliverables_en"
                ]
            else:
                title = phase["title_vi"]
                description = phase[
                    "description_vi"
                ]
                deliverables = phase[
                    "deliverables_vi"
                ]

            result.append(
                JobAssistantMilestone(
                    title=title,
                    description=description,
                    duration_days=duration_days,
                    percentage=phase[
                        "percentage"
                    ],
                    deliverables=deliverables,
                )
            )

        return result

    def _normalize_milestones(
        self,
        raw_milestones: Any,
        total_days: int,
        language: str,
        include_milestones: bool,
    ) -> list[JobAssistantMilestone]:
        if not include_milestones:
            return []

        if not isinstance(
            raw_milestones,
            list,
        ):
            return self._fallback_milestones(
                total_days,
                language,
            )

        milestones: list[
            JobAssistantMilestone
        ] = []

        for index, raw_item in enumerate(
            raw_milestones
        ):
            if not isinstance(
                raw_item,
                dict,
            ):
                continue

            title = self._clean_text(
                raw_item.get("title"),
                f"Milestone {index + 1}",
            )

            description = self._clean_text(
                raw_item.get(
                    "description"
                )
            ) or None

            duration_days = self._clamp_int(
                raw_item.get(
                    "duration_days"
                ),
                1,
                365,
                max(
                    1,
                    total_days
                    // max(
                        1,
                        len(raw_milestones),
                    ),
                ),
            )

            percentage = self._decimal(
                raw_item.get(
                    "percentage"
                ),
                Decimal("0"),
            )

            percentage = max(
                Decimal("0"),
                min(
                    percentage,
                    Decimal("100"),
                ),
            )

            milestones.append(
                JobAssistantMilestone(
                    title=self._truncate(
                        title,
                        255,
                    ),
                    description=(
                        self._truncate(
                            description,
                            2000,
                        )
                        if description
                        else None
                    ),
                    duration_days=duration_days,
                    percentage=percentage,
                    deliverables=(
                        self._unique_strings(
                            raw_item.get(
                                "deliverables"
                            ),
                            maximum_items=20,
                        )
                    ),
                )
            )

        if not milestones:
            return self._fallback_milestones(
                total_days,
                language,
            )

        self._normalize_milestone_percentages(
            milestones
        )

        return milestones

    def _normalize_milestone_percentages(
        self,
        milestones: list[
            JobAssistantMilestone
        ],
    ) -> None:
        if not milestones:
            return

        total_percentage = sum(
            (
                self._decimal(
                    item.percentage
                )
                for item in milestones
            ),
            Decimal("0"),
        )

        if total_percentage <= Decimal("0"):
            equal_value = (
                Decimal("100")
                / Decimal(
                    len(milestones)
                )
            )

            for item in milestones:
                item.percentage = equal_value.quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                )

        else:
            for item in milestones:
                normalized = (
                    self._decimal(
                        item.percentage
                    )
                    / total_percentage
                    * Decimal("100")
                )

                item.percentage = normalized.quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                )

        current_total = sum(
            (
                self._decimal(
                    item.percentage
                )
                for item in milestones
            ),
            Decimal("0"),
        )

        difference = (
            Decimal("100.00")
            - current_total
        )

        milestones[-1].percentage = (
            self._decimal(
                milestones[-1].percentage
            )
            + difference
        )

    # ======================================================
    # AI RESULT NORMALIZATION
    # ======================================================

    def _normalize_budget(
        self,
        raw_budget: Any,
        data: JobAssistantGenerateRequest,
        complexity: str,
    ) -> JobAssistantBudgetSuggestion:
        fallback = self._fallback_budget(
            data,
            complexity,
        )

        if not isinstance(
            raw_budget,
            dict,
        ):
            return fallback

        minimum = self._decimal(
            raw_budget.get("minimum"),
            fallback.minimum,
        )

        recommended = self._decimal(
            raw_budget.get(
                "recommended"
            ),
            fallback.recommended,
        )

        maximum = self._decimal(
            raw_budget.get("maximum"),
            fallback.maximum,
        )

        if data.budget_hint is not None:
            hint = self._decimal(
                data.budget_hint
            )

            if recommended <= Decimal("0"):
                recommended = hint

        minimum = max(
            Decimal("0"),
            minimum,
        )

        recommended = max(
            minimum,
            recommended,
        )

        maximum = max(
            recommended,
            maximum,
        )

        currency = self._clean_text(
            raw_budget.get("currency"),
            self.DEFAULT_CURRENCY,
        ).upper()

        explanation = self._clean_text(
            raw_budget.get(
                "explanation"
            )
        ) or fallback.explanation

        return JobAssistantBudgetSuggestion(
            minimum=self._round_money(
                minimum
            ),
            recommended=self._round_money(
                recommended
            ),
            maximum=self._round_money(
                maximum
            ),
            currency=currency[
                :10
            ],
            explanation=self._truncate(
                explanation,
                2000,
            ),
        )

    def _normalize_timeline(
        self,
        raw_timeline: Any,
        data: JobAssistantGenerateRequest,
        complexity: str,
    ) -> JobAssistantTimelineSuggestion:
        fallback = self._fallback_timeline(
            data,
            complexity,
        )

        if not isinstance(
            raw_timeline,
            dict,
        ):
            return fallback

        minimum_days = self._clamp_int(
            raw_timeline.get(
                "minimum_days"
            ),
            1,
            365,
            fallback.minimum_days,
        )

        recommended_days = self._clamp_int(
            raw_timeline.get(
                "recommended_days"
            ),
            1,
            365,
            fallback.recommended_days,
        )

        maximum_days = self._clamp_int(
            raw_timeline.get(
                "maximum_days"
            ),
            1,
            730,
            fallback.maximum_days,
        )

        if data.timeline_hint is not None:
            hint = self._clamp_int(
                data.timeline_hint,
                1,
                365,
                fallback.recommended_days,
            )

            if not raw_timeline.get(
                "recommended_days"
            ):
                recommended_days = hint

        recommended_days = max(
            minimum_days,
            recommended_days,
        )

        maximum_days = max(
            recommended_days,
            maximum_days,
        )

        explanation = self._clean_text(
            raw_timeline.get(
                "explanation"
            )
        ) or fallback.explanation

        return JobAssistantTimelineSuggestion(
            minimum_days=minimum_days,
            recommended_days=recommended_days,
            maximum_days=maximum_days,
            explanation=self._truncate(
                explanation,
                2000,
            ),
        )

    def _normalize_ai_result(
        self,
        raw_result: dict[str, Any],
        data: JobAssistantGenerateRequest,
    ) -> JobAssistantGenerateResponse:
        language = self._normalize_language(
            data.language
        )

        complexity = self._estimate_complexity(
            data
        )

        category = self._clean_text(
            raw_result.get("category")
        )

        if not category:
            category = (
                data.category_hint
                or self._detect_project_type(
                    data.idea
                )
            )

        default_skills = (
            self._default_skills_for_category(
                category
            )
        )

        required_skills = self._unique_strings(
            [
                *self._unique_strings(
                    raw_result.get(
                        "required_skills"
                    )
                ),
                *data.preferred_skills,
            ]
        )

        if not required_skills:
            required_skills = (
                default_skills
            )

        technologies = self._unique_strings(
            raw_result.get(
                "recommended_technologies"
            )
        )

        if not technologies:
            technologies = [
                skill
                for skill in default_skills
                if skill
                not in {
                    "Artificial Intelligence",
                    "Machine Learning",
                    "Computer Vision",
                    "NLP",
                }
            ]

        budget = self._normalize_budget(
            raw_result.get("budget"),
            data,
            complexity,
        )

        timeline = self._normalize_timeline(
            raw_result.get(
                "timeline"
            ),
            data,
            complexity,
        )

        title = self._clean_text(
            raw_result.get("title")
        )

        if not title:
            title = self._fallback_title(
                data,
                category,
            )

        description = self._clean_text(
            raw_result.get(
                "description"
            )
        )

        if not description:
            description = (
                self._fallback_description(
                    data,
                    category,
                    required_skills,
                )
            )

        short_description = self._clean_text(
            raw_result.get(
                "short_description"
            )
        )

        if not short_description:
            short_description = (
                self._truncate(
                    description,
                    300,
                )
            )

        milestones = self._normalize_milestones(
            raw_result.get(
                "milestones"
            ),
            timeline.recommended_days,
            language,
            data.include_milestones,
        )

        objectives = self._unique_strings(
            raw_result.get(
                "objectives"
            )
        )

        if not objectives:
            objectives = self._fallback_objectives(
                data,
                language,
            )

        scope_included = self._unique_strings(
            raw_result.get(
                "scope_included"
            )
        )

        if not scope_included:
            scope_included = (
                self._fallback_scope_included(
                    language
                )
            )

        scope_excluded = self._unique_strings(
            raw_result.get(
                "scope_excluded"
            )
        )

        if not scope_excluded:
            scope_excluded = (
                self._fallback_scope_excluded(
                    language
                )
            )

        acceptance_criteria = (
            self._unique_strings(
                raw_result.get(
                    "acceptance_criteria"
                )
            )
            if data.include_acceptance_criteria
            else []
        )

        if (
            data.include_acceptance_criteria
            and not acceptance_criteria
        ):
            acceptance_criteria = (
                self._fallback_acceptance_criteria(
                    language
                )
            )

        risks = (
            self._unique_strings(
                raw_result.get("risks")
            )
            if data.include_risks
            else []
        )

        if (
            data.include_risks
            and not risks
        ):
            risks = self._fallback_risks(
                language
            )

        assumptions = self._unique_strings(
            raw_result.get(
                "assumptions"
            )
        )

        if not assumptions:
            assumptions = (
                self._fallback_assumptions(
                    language
                )
            )

        questions = self._unique_strings(
            raw_result.get(
                "suggested_questions_for_expert"
            )
        )

        if not questions:
            questions = (
                self._fallback_questions(
                    language
                )
            )

        return JobAssistantGenerateResponse(
            title=self._truncate(
                title,
                255,
            ),
            short_description=self._truncate(
                short_description,
                500,
            ),
            description=self._truncate(
                description,
                self.MAX_DESCRIPTION_LENGTH,
            ),
            category=self._truncate(
                category,
                255,
            ),
            objectives=objectives,
            scope_included=scope_included,
            scope_excluded=scope_excluded,
            required_skills=required_skills,
            recommended_technologies=technologies,
            budget=budget,
            timeline=timeline,
            milestones=milestones,
            acceptance_criteria=acceptance_criteria,
            risks=risks,
            assumptions=assumptions,
            suggested_questions_for_expert=questions,
            generated_by="Gemini AI Job Assistant",
            language=language,
        )

    # ======================================================
    # FALLBACK CONTENT
    # ======================================================

    def _fallback_title(
        self,
        data: JobAssistantGenerateRequest,
        category: str,
    ) -> str:
        idea = re.sub(
            r"\s+",
            " ",
            data.idea,
        ).strip()

        if len(idea) <= 80:
            if data.language == "en":
                return (
                    f"Develop an AI solution: {idea}"
                )

            return (
                f"Xây dựng giải pháp AI: {idea}"
            )

        if data.language == "en":
            return (
                f"Develop a {category} solution"
            )

        return (
            f"Xây dựng giải pháp {category}"
        )

    def _fallback_description(
        self,
        data: JobAssistantGenerateRequest,
        category: str,
        skills: list[str],
    ) -> str:
        skill_text = ", ".join(
            skills
        )

        if data.language == "en":
            return (
                f"The project aims to develop a {category} solution "
                f"based on the following business idea: {data.idea}. "
                f"The solution should cover requirements analysis, "
                f"system design, implementation, AI integration, "
                f"testing, deployment, and documentation. "
                f"Recommended skills include: {skill_text}."
            )

        return (
            f"Dự án nhằm xây dựng giải pháp thuộc nhóm {category} "
            f"dựa trên ý tưởng nghiệp vụ sau: {data.idea}. "
            f"Phạm vi thực hiện bao gồm phân tích yêu cầu, "
            f"thiết kế hệ thống, phát triển chức năng, tích hợp AI, "
            f"kiểm thử, triển khai và bàn giao tài liệu. "
            f"Các kỹ năng đề xuất gồm: {skill_text}."
        )

    @staticmethod
    def _fallback_objectives(
        data: JobAssistantGenerateRequest,
        language: str,
    ) -> list[str]:
        if language == "en":
            return [
                "Develop a solution that meets the described business needs.",
                "Automate relevant manual processes using AI.",
                "Provide a secure and maintainable system.",
                "Deliver documentation and deployment instructions.",
            ]

        return [
            "Xây dựng giải pháp đáp ứng đúng nhu cầu nghiệp vụ đã mô tả.",
            "Ứng dụng AI để tự động hóa các thao tác thủ công phù hợp.",
            "Bảo đảm hệ thống an toàn, ổn định và dễ bảo trì.",
            "Bàn giao tài liệu và hướng dẫn triển khai đầy đủ.",
        ]

    @staticmethod
    def _fallback_scope_included(
        language: str,
    ) -> list[str]:
        if language == "en":
            return [
                "Requirements analysis and solution design",
                "Backend API and database development",
                "AI module integration",
                "Functional testing and deployment",
                "Technical and user documentation",
            ]

        return [
            "Phân tích yêu cầu và thiết kế giải pháp",
            "Phát triển backend API và cơ sở dữ liệu",
            "Tích hợp mô-đun AI",
            "Kiểm thử chức năng và triển khai",
            "Tài liệu kỹ thuật và hướng dẫn sử dụng",
        ]

    @staticmethod
    def _fallback_scope_excluded(
        language: str,
    ) -> list[str]:
        if language == "en":
            return [
                "Third-party service fees",
                "Hardware procurement",
                "Large-scale data labeling unless agreed separately",
                "Features not included in the approved requirements",
            ]

        return [
            "Chi phí dịch vụ bên thứ ba",
            "Mua sắm thiết bị phần cứng",
            "Gán nhãn dữ liệu quy mô lớn nếu chưa có thỏa thuận riêng",
            "Chức năng nằm ngoài tài liệu yêu cầu đã duyệt",
        ]

    @staticmethod
    def _fallback_acceptance_criteria(
        language: str,
    ) -> list[str]:
        if language == "en":
            return [
                "All approved functional requirements operate correctly.",
                "The API returns valid responses for documented test cases.",
                "The AI module meets the agreed evaluation criteria.",
                "No critical security or data-loss defects remain.",
                "Source code and documentation are fully delivered.",
            ]

        return [
            "Tất cả yêu cầu chức năng đã duyệt hoạt động đúng.",
            "API trả kết quả hợp lệ với các trường hợp kiểm thử đã thống nhất.",
            "Mô-đun AI đạt chỉ số đánh giá được hai bên thỏa thuận.",
            "Không còn lỗi nghiêm trọng về bảo mật hoặc mất dữ liệu.",
            "Mã nguồn và tài liệu được bàn giao đầy đủ.",
        ]

    @staticmethod
    def _fallback_risks(
        language: str,
    ) -> list[str]:
        if language == "en":
            return [
                "Insufficient or low-quality training data",
                "Changes in third-party API availability or pricing",
                "AI output may require additional validation",
                "Requirement changes may affect cost and timeline",
            ]

        return [
            "Dữ liệu huấn luyện không đủ hoặc chất lượng thấp",
            "API bên thứ ba thay đổi tính khả dụng hoặc chi phí",
            "Kết quả AI có thể cần bước kiểm duyệt bổ sung",
            "Thay đổi yêu cầu có thể ảnh hưởng ngân sách và tiến độ",
        ]

    @staticmethod
    def _fallback_assumptions(
        language: str,
    ) -> list[str]:
        if language == "en":
            return [
                "The client provides required business information on time.",
                "Required data can be legally collected and processed.",
                "Third-party credentials are provided when needed.",
                "The client reviews milestones within the agreed period.",
            ]

        return [
            "Doanh nghiệp cung cấp thông tin nghiệp vụ đúng thời hạn.",
            "Dữ liệu cần thiết được phép thu thập và xử lý hợp pháp.",
            "Thông tin xác thực dịch vụ bên thứ ba được cung cấp khi cần.",
            "Doanh nghiệp phản hồi milestones trong thời gian đã thống nhất.",
        ]

    @staticmethod
    def _fallback_questions(
        language: str,
    ) -> list[str]:
        if language == "en":
            return [
                "What data sources will the system use?",
                "How many expected users and requests are there?",
                "Which existing systems require integration?",
                "What accuracy or performance metrics are required?",
                "What are the deployment and security requirements?",
            ]

        return [
            "Hệ thống sẽ sử dụng những nguồn dữ liệu nào?",
            "Số lượng người dùng và lưu lượng dự kiến là bao nhiêu?",
            "Cần tích hợp với những hệ thống hiện có nào?",
            "Chỉ số độ chính xác hoặc hiệu năng yêu cầu là gì?",
            "Yêu cầu triển khai và bảo mật cụ thể như thế nào?",
        ]

    def _build_fallback_response(
        self,
        data: JobAssistantGenerateRequest,
    ) -> JobAssistantGenerateResponse:
        language = self._normalize_language(
            data.language
        )

        complexity = self._estimate_complexity(
            data
        )

        category = (
            data.category_hint
            or self._detect_project_type(
                data.idea
            )
        )

        required_skills = self._unique_strings(
            [
                *self._default_skills_for_category(
                    category
                ),
                *data.preferred_skills,
            ]
        )

        budget = self._fallback_budget(
            data,
            complexity,
        )

        timeline = self._fallback_timeline(
            data,
            complexity,
        )

        title = self._fallback_title(
            data,
            category,
        )

        description = (
            self._fallback_description(
                data,
                category,
                required_skills,
            )
        )

        technologies = [
            item
            for item in required_skills
            if item
            not in {
                "Artificial Intelligence",
                "Machine Learning",
                "Computer Vision",
                "NLP",
            }
        ]

        return JobAssistantGenerateResponse(
            title=self._truncate(
                title,
                255,
            ),
            short_description=self._truncate(
                description,
                500,
            ),
            description=self._truncate(
                description,
                self.MAX_DESCRIPTION_LENGTH,
            ),
            category=category,
            objectives=self._fallback_objectives(
                data,
                language,
            ),
            scope_included=(
                self._fallback_scope_included(
                    language
                )
            ),
            scope_excluded=(
                self._fallback_scope_excluded(
                    language
                )
            ),
            required_skills=required_skills,
            recommended_technologies=technologies,
            budget=budget,
            timeline=timeline,
            milestones=(
                self._fallback_milestones(
                    timeline.recommended_days,
                    language,
                )
                if data.include_milestones
                else []
            ),
            acceptance_criteria=(
                self._fallback_acceptance_criteria(
                    language
                )
                if data.include_acceptance_criteria
                else []
            ),
            risks=(
                self._fallback_risks(
                    language
                )
                if data.include_risks
                else []
            ),
            assumptions=self._fallback_assumptions(
                language
            ),
            suggested_questions_for_expert=(
                self._fallback_questions(
                    language
                )
            ),
            generated_by=(
                "AI Job Assistant Fallback"
            ),
            language=language,
        )

    # ======================================================
    # PROJECT PAYLOAD
    # ======================================================

    def _build_project_payload(
        self,
        suggestion: JobAssistantGenerateResponse,
    ) -> JobAssistantProjectPayload:
        description_sections = [
            suggestion.description,
        ]

        if suggestion.objectives:
            description_sections.append(
                "\nMục tiêu:\n- "
                + "\n- ".join(
                    suggestion.objectives
                )
            )

        if suggestion.scope_included:
            description_sections.append(
                "\nPhạm vi thực hiện:\n- "
                + "\n- ".join(
                    suggestion.scope_included
                )
            )

        if suggestion.acceptance_criteria:
            description_sections.append(
                "\nTiêu chí nghiệm thu:\n- "
                + "\n- ".join(
                    suggestion.acceptance_criteria
                )
            )

        payload_description = "\n".join(
            section
            for section in description_sections
            if section
        )

        deadline_days = min(
            365,
            max(
                1,
                suggestion.timeline.recommended_days,
            ),
        )

        return JobAssistantProjectPayload(
            title=suggestion.title,
            description=self._truncate(
                payload_description,
                self.MAX_DESCRIPTION_LENGTH,
            ),
            budget=(
                suggestion.budget.recommended
            ),
            deadline_days=deadline_days,
            required_skills=(
                suggestion.required_skills
            ),
            category=suggestion.category,
        )

    # ======================================================
    # PUBLIC METHODS
    # ======================================================

    def generate(
        self,
        data: JobAssistantGenerateRequest,
    ) -> JobAssistantResult:
        """
        Sinh gợi ý dự án.

        Ưu tiên Gemini, sau đó fallback.
        """

        suggestion: JobAssistantGenerateResponse

        if self.client is not None:
            try:
                prompt = self._build_prompt(
                    data
                )

                raw_response = self._call_gemini(
                    prompt
                )

                parsed_response = (
                    self._extract_json_object(
                        raw_response
                    )
                )

                suggestion = (
                    self._normalize_ai_result(
                        parsed_response,
                        data,
                    )
                )

            except Exception:
                logger.exception(
                    "Job Assistant chuyển sang fallback "
                    "do Gemini gặp lỗi."
                )

                suggestion = (
                    self._build_fallback_response(
                        data
                    )
                )

        else:
            suggestion = (
                self._build_fallback_response(
                    data
                )
            )

        project_payload = (
            self._build_project_payload(
                suggestion
            )
        )

        return JobAssistantResult(
            suggestion=suggestion,
            project_payload=project_payload,
        )

    def health(self) -> dict[str, Any]:
        """
        Kiểm tra trạng thái Job Assistant.
        """

        return {
            "service": "AI Job Assistant",
            "status": "healthy",
            "ai_available": (
                self.client is not None
            ),
            "fallback_available": True,
            "model": self.model_name,
            "api_key_configured": bool(
                self.api_key
            ),
        }


job_assistant_service = JobAssistantService()