"""
AITasker Chatbot Service

Chức năng:
- Đọc dữ liệu thật từ PostgreSQL bằng SQLAlchemy.
- Trả lời trực tiếp các câu hỏi phổ biến.
- Xây dựng database context cho Gemini.
- Không để Gemini tự tạo số liệu ngoài hệ thống.
- Ghi nhớ đối tượng gần nhất bằng session.
"""

from __future__ import annotations

import logging
import re
import unicodedata
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

from fastapi import Request
from sqlalchemy.orm import Session

from backend.src.models.contract import Contract
from backend.src.models.enterprise import Enterprise
from backend.src.models.expert import Expert
from backend.src.models.project import Project
from backend.src.models.proposal import Proposal
from backend.src.models.review import Review


# ==========================================================
# OPTIONAL MODELS
# Dùng try/except để backend vẫn chạy nếu một model chưa có.
# ==========================================================

try:
    from backend.src.models.payment import Payment
except (ImportError, ModuleNotFoundError):
    Payment = None

try:
    from backend.src.models.skill import Skill
except (ImportError, ModuleNotFoundError):
    Skill = None

try:
    from backend.src.models.category import Category
except (ImportError, ModuleNotFoundError):
    Category = None

try:
    from backend.src.models.auth import User
except (ImportError, ModuleNotFoundError):
    User = None


logger = logging.getLogger("AITasker.ChatbotService")


# ==========================================================
# TEXT HELPERS
# ==========================================================

def normalize_text(value: Any) -> str:
    """
    Chuẩn hóa chuỗi phục vụ tìm kiếm:

    - Chuyển về chữ thường.
    - Bỏ dấu tiếng Việt.
    - Chuẩn hóa chữ đ thành d.
    - Xóa ký tự đặc biệt.
    - Xóa khoảng trắng thừa.
    """

    text = str(value or "").strip()

    if not text:
        return ""

    text = text.replace("đ", "d").replace("Đ", "D")

    normalized = unicodedata.normalize(
        "NFD",
        text,
    )

    without_accents = "".join(
        character
        for character in normalized
        if unicodedata.category(character) != "Mn"
    )

    without_accents = without_accents.lower()

    without_special_characters = re.sub(
        r"[^a-z0-9\s_-]",
        " ",
        without_accents,
    )

    return re.sub(
        r"\s+",
        " ",
        without_special_characters,
    ).strip()


def contains_any(
    text: str,
    keywords: list[str],
) -> bool:
    """
    Kiểm tra chuỗi đã chuẩn hóa có chứa một keyword hay không.
    """

    return any(
        keyword in text
        for keyword in keywords
    )


def get_attribute(
    obj: Any,
    *field_names: str,
    default: Any = None,
) -> Any:
    """
    Lấy thuộc tính đầu tiên tồn tại và khác None.

    Hữu ích khi các model từng đổi tên trường, ví dụ:
    - bid_amount / price
    - total_amount / amount
    - full_name / name
    """

    if obj is None:
        return default

    for field_name in field_names:
        if hasattr(obj, field_name):
            value = getattr(
                obj,
                field_name,
            )

            if value is not None:
                return value

    return default


# ==========================================================
# FORMAT HELPERS
# ==========================================================

def to_decimal(value: Any) -> Decimal:
    """
    Chuyển giá trị sang Decimal an toàn.
    """

    if value is None:
        return Decimal("0")

    try:
        return Decimal(str(value))
    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):
        return Decimal("0")


def format_vnd(value: Any) -> str:
    """
    Định dạng tiền Việt Nam.

    Ví dụ:
    30000000 -> 30.000.000
    """

    amount = to_decimal(value)

    formatted = f"{amount:,.0f}"

    return formatted.replace(
        ",",
        ".",
    )


def format_date(value: Any) -> str:
    """
    Định dạng ngày DD/MM/YYYY.
    """

    if value is None:
        return "chưa cập nhật"

    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y")

    if isinstance(value, date):
        return value.strftime("%d/%m/%Y")

    try:
        parsed_date = datetime.fromisoformat(
            str(value)
        )

        return parsed_date.strftime(
            "%d/%m/%Y"
        )

    except (ValueError, TypeError):
        return str(value)


def format_status(value: Any) -> str:
    """
    Chuẩn hóa trạng thái để hiển thị.
    """

    status_value = str(
        value or "Chưa cập nhật"
    ).strip()

    status_mapping = {
        "OPEN": "Đang mở",
        "PENDING": "Chờ duyệt",
        "IN_PROGRESS": "Đang thực hiện",
        "COMPLETED": "Hoàn thành",
        "CANCELLED": "Đã hủy",
        "AVAILABLE": "Sẵn sàng",
        "ACTIVE": "Hoạt động",
        "INACTIVE": "Ngừng hoạt động",
        "PAID": "Đã thanh toán",
        "FAILED": "Thất bại",
        "ACCEPTED": "Đã chấp nhận",
        "REJECTED": "Đã từ chối",
    }

    return status_mapping.get(
        status_value.upper(),
        status_value,
    )


# ==========================================================
# SKILL HELPERS
# ==========================================================

def serialize_skills(expert: Any) -> list[str]:
    """
    Lấy danh sách kỹ năng của chuyên gia.

    Hỗ trợ:
    - relationship SQLAlchemy;
    - list[str];
    - list[Skill];
    - chuỗi phân cách bằng dấu phẩy;
    - dict.
    """

    raw_skills = get_attribute(
        expert,
        "skills",
        "skill_names",
        default=[],
    )

    if raw_skills is None:
        return []

    # Trường hợp skills là chuỗi
    if isinstance(raw_skills, str):
        return [
            skill.strip()
            for skill in raw_skills.split(",")
            if skill.strip()
        ]

    # Trường hợp skills là dictionary
    if isinstance(raw_skills, dict):
        skill_name = (
            raw_skills.get("name")
            or raw_skills.get("title")
            or raw_skills.get("skill_name")
        )

        return (
            [str(skill_name).strip()]
            if skill_name
            else []
        )

    # Trường hợp skills là danh sách
    if isinstance(
        raw_skills,
        (list, tuple, set),
    ):
        results: list[str] = []

        for skill in raw_skills:
            if isinstance(skill, str):
                skill_name = skill

            elif isinstance(skill, dict):
                skill_name = (
                    skill.get("name")
                    or skill.get("title")
                    or skill.get("skill_name")
                    or ""
                )

            else:
                skill_name = get_attribute(
                    skill,
                    "name",
                    "title",
                    "skill_name",
                    default="",
                )

            skill_name = str(
                skill_name or ""
            ).strip()

            if skill_name:
                results.append(skill_name)

        return results

    return []


def get_unique_skill_names(
    skills: list[Any],
    experts: list[Any],
) -> list[str]:
    """
    Lấy danh sách kỹ năng không trùng lặp.

    Ưu tiên bảng skills.
    Nếu bảng skills trống thì lấy từ hồ sơ chuyên gia.
    """

    unique_skills: dict[str, str] = {}

    for skill in skills:
        skill_name = get_attribute(
            skill,
            "name",
            "title",
            "skill_name",
            default="",
        )

        skill_name = str(
            skill_name or ""
        ).strip()

        normalized_name = normalize_text(
            skill_name
        )

        if normalized_name:
            unique_skills[normalized_name] = skill_name

    for expert in experts:
        for skill_name in serialize_skills(
            expert
        ):
            normalized_name = normalize_text(
                skill_name
            )

            if normalized_name:
                unique_skills.setdefault(
                    normalized_name,
                    skill_name,
                )

    return sorted(
        unique_skills.values(),
        key=lambda item: normalize_text(item),
    )


# ==========================================================
# CHATBOT SERVICE
# ==========================================================

class ChatbotService:
    """
    Service xử lý chatbot của hệ thống AITasker.
    """

    def __init__(
        self,
        ai_client: Any = None,
        model_name: str = "gemini-2.5-flash",
    ) -> None:
        self.ai_client = ai_client
        self.model_name = model_name

    # ======================================================
    # GEMINI CONFIGURATION
    # ======================================================

    def configure_ai(
        self,
        ai_client: Any,
        model_name: Optional[str] = None,
    ) -> None:
        """
        Cấu hình Gemini client.
        """

        self.ai_client = ai_client

        if model_name:
            self.model_name = model_name

    # ======================================================
    # DATABASE LOADING
    # ======================================================

    def _safe_query_all(
        self,
        db: Session,
        model: Any,
        table_name: str,
    ) -> list[Any]:
        """
        Query một model an toàn.

        Nếu một bảng lỗi thì ghi log và trả về danh sách rỗng,
        không làm toàn bộ chatbot ngừng hoạt động.
        """

        if model is None:
            return []

        try:
            query = db.query(model)

            if hasattr(model, "created_at"):
                query = query.order_by(
                    model.created_at.desc()
                )

            return query.all()

        except Exception as exc:
            db.rollback()

            logger.exception(
                "Không thể đọc dữ liệu bảng %s: %s",
                table_name,
                exc,
            )

            return []

    def load_system_data(
        self,
        db: Session,
    ) -> dict[str, list[Any]]:
        """
        Đọc toàn bộ dữ liệu cần thiết cho chatbot.
        """

        return {
            "projects": self._safe_query_all(
                db,
                Project,
                "projects",
            ),
            "experts": self._safe_query_all(
                db,
                Expert,
                "experts",
            ),
            "enterprises": self._safe_query_all(
                db,
                Enterprise,
                "enterprises",
            ),
            "proposals": self._safe_query_all(
                db,
                Proposal,
                "proposals",
            ),
            "contracts": self._safe_query_all(
                db,
                Contract,
                "contracts",
            ),
            "payments": self._safe_query_all(
                db,
                Payment,
                "payments",
            ),
            "reviews": self._safe_query_all(
                db,
                Review,
                "reviews",
            ),
            "skills": self._safe_query_all(
                db,
                Skill,
                "skills",
            ),
            "categories": self._safe_query_all(
                db,
                Category,
                "categories",
            ),
            "users": self._safe_query_all(
                db,
                User,
                "users",
            ),
        }

    # ======================================================
    # ENTITY SEARCH
    # ======================================================

    def find_project(
        self,
        question: str,
        projects: list[Any],
    ) -> Optional[Any]:
        """
        Tìm dự án được nhắc tới trong câu hỏi.
        """

        normalized_question = normalize_text(
            question
        )

        sorted_projects = sorted(
            projects,
            key=lambda project: len(
                str(
                    get_attribute(
                        project,
                        "title",
                        "name",
                        default="",
                    )
                )
            ),
            reverse=True,
        )

        for project in sorted_projects:
            project_title = get_attribute(
                project,
                "title",
                "name",
                default="",
            )

            normalized_title = normalize_text(
                project_title
            )

            if (
                normalized_title
                and normalized_title
                in normalized_question
            ):
                return project

        return None

    def find_expert(
        self,
        question: str,
        experts: list[Any],
    ) -> Optional[Any]:
        """
        Tìm chuyên gia được nhắc tới trong câu hỏi.
        """

        normalized_question = normalize_text(
            question
        )

        sorted_experts = sorted(
            experts,
            key=lambda expert: len(
                str(
                    get_attribute(
                        expert,
                        "full_name",
                        "name",
                        default="",
                    )
                )
            ),
            reverse=True,
        )

        for expert in sorted_experts:
            expert_name = get_attribute(
                expert,
                "full_name",
                "name",
                default="",
            )

            normalized_name = normalize_text(
                expert_name
            )

            if (
                normalized_name
                and normalized_name
                in normalized_question
            ):
                return expert

        return None

    def find_enterprise(
        self,
        question: str,
        enterprises: list[Any],
    ) -> Optional[Any]:
        """
        Tìm doanh nghiệp được nhắc tới trong câu hỏi.
        """

        normalized_question = normalize_text(
            question
        )

        sorted_enterprises = sorted(
            enterprises,
            key=lambda enterprise: len(
                str(
                    get_attribute(
                        enterprise,
                        "name",
                        "company_name",
                        default="",
                    )
                )
            ),
            reverse=True,
        )

        for enterprise in sorted_enterprises:
            enterprise_name = get_attribute(
                enterprise,
                "name",
                "company_name",
                default="",
            )

            normalized_name = normalize_text(
                enterprise_name
            )

            if (
                normalized_name
                and normalized_name
                in normalized_question
            ):
                return enterprise

        return None

    # ======================================================
    # SESSION MEMORY
    # ======================================================

    def save_entity_context(
        self,
        request: Optional[Request],
        entity_type: str,
        entity_id: Any,
    ) -> None:
        """
        Ghi nhớ đối tượng đang được hỏi.
        """

        if request is None:
            return

        try:
            request.session[
                "chat_entity_type"
            ] = entity_type

            request.session[
                "chat_entity_id"
            ] = str(entity_id)

        except Exception:
            logger.debug(
                "Không thể lưu chatbot session.",
                exc_info=True,
            )

    def get_previous_entity(
        self,
        request: Optional[Request],
        entity_type: str,
        entities: list[Any],
    ) -> Optional[Any]:
        """
        Lấy lại đối tượng gần nhất từ session.
        """

        if request is None:
            return None

        try:
            previous_type = request.session.get(
                "chat_entity_type"
            )

            previous_id = request.session.get(
                "chat_entity_id"
            )

            if (
                previous_type != entity_type
                or not previous_id
            ):
                return None

            for entity in entities:
                entity_id = get_attribute(
                    entity,
                    "id",
                    default=None,
                )

                if str(entity_id) == str(previous_id):
                    return entity

        except Exception:
            logger.debug(
                "Không thể đọc chatbot session.",
                exc_info=True,
            )

        return None

    def resolve_project(
        self,
        question: str,
        projects: list[Any],
        request: Optional[Request],
    ) -> Optional[Any]:
        """
        Tìm project trong câu hỏi.

        Nếu câu hiện tại không có tên project,
        lấy project gần nhất trong session.
        """

        project = self.find_project(
            question,
            projects,
        )

        if project is not None:
            self.save_entity_context(
                request,
                "project",
                project.id,
            )

            return project

        return self.get_previous_entity(
            request,
            "project",
            projects,
        )

    def resolve_expert(
        self,
        question: str,
        experts: list[Any],
        request: Optional[Request],
    ) -> Optional[Any]:
        """
        Tìm expert trong câu hỏi hoặc session.
        """

        expert = self.find_expert(
            question,
            experts,
        )

        if expert is not None:
            self.save_entity_context(
                request,
                "expert",
                expert.id,
            )

            return expert

        return self.get_previous_entity(
            request,
            "expert",
            experts,
        )

    # ======================================================
    # DIRECT DATABASE ANSWERS
    # ======================================================

    def answer_directly(
        self,
        question: str,
        data: dict[str, list[Any]],
        request: Optional[Request] = None,
    ) -> Optional[dict[str, Any]]:
        """
        Trả lời trực tiếp các câu hỏi phổ biến từ database.

        Hàm trả về None nếu câu hỏi cần chuyển sang Gemini.
        """

        normalized_question = normalize_text(
            question
        )

        projects = data.get(
            "projects",
            [],
        )
        experts = data.get(
            "experts",
            [],
        )
        enterprises = data.get(
            "enterprises",
            [],
        )
        proposals = data.get(
            "proposals",
            [],
        )
        contracts = data.get(
            "contracts",
            [],
        )
        payments = data.get(
            "payments",
            [],
        )
        reviews = data.get(
            "reviews",
            [],
        )
        skills = data.get(
            "skills",
            [],
        )
        categories = data.get(
            "categories",
            [],
        )
        users = data.get(
            "users",
            [],
        )

        unique_skill_names = get_unique_skill_names(
            skills,
            experts,
        )

        # --------------------------------------------------
        # COUNT PROJECTS
        # --------------------------------------------------

        if contains_any(
            normalized_question,
            [
                "bao nhieu du an",
                "co bao nhieu du an",
                "co may du an",
                "tong so du an",
                "so luong du an",
                "tat ca bao nhieu du an",
            ],
        ):
            return {
                "success": True,
                "reply": (
                    f"Hệ thống AITasker hiện có "
                    f"{len(projects)} dự án."
                ),
                "source": "database",
            }

        # --------------------------------------------------
        # COUNT EXPERTS
        # --------------------------------------------------

        if contains_any(
            normalized_question,
            [
                "bao nhieu chuyen gia",
                "co bao nhieu chuyen gia",
                "co may chuyen gia",
                "tong so chuyen gia",
                "so luong chuyen gia",
                "tat ca bao nhieu chuyen gia",
            ],
        ):
            return {
                "success": True,
                "reply": (
                    f"Hệ thống AITasker hiện có "
                    f"{len(experts)} chuyên gia."
                ),
                "source": "database",
            }

        # --------------------------------------------------
        # COUNT UNIQUE SKILLS
        # --------------------------------------------------

        if contains_any(
            normalized_question,
            [
                "bao nhieu ky nang",
                "co bao nhieu ky nang",
                "co may ky nang",
                "tong so ky nang",
                "so luong ky nang",
                "bao nhieu ky nang core",
                "co bao nhieu ky nang core",
                "tong so ky nang core",
            ],
        ):
            skill_text = (
                ", ".join(unique_skill_names)
                if unique_skill_names
                else "chưa có kỹ năng nào"
            )

            return {
                "success": True,
                "reply": (
                    f"Hệ thống AITasker hiện có "
                    f"{len(unique_skill_names)} kỹ năng core "
                    f"khác nhau: {skill_text}."
                ),
                "source": "database",
            }

        # --------------------------------------------------
        # LIST SKILLS
        # --------------------------------------------------

        if contains_any(
            normalized_question,
            [
                "danh sach ky nang",
                "cac ky nang core",
                "co nhung ky nang nao",
                "he thong co ky nang gi",
                "liet ke ky nang",
            ],
        ):
            if not unique_skill_names:
                return {
                    "success": True,
                    "reply": (
                        "Hệ thống hiện chưa có dữ liệu kỹ năng."
                    ),
                    "source": "database",
                }

            return {
                "success": True,
                "reply": (
                    "Các kỹ năng core hiện có gồm: "
                    f"{', '.join(unique_skill_names)}."
                ),
                "source": "database",
            }

        # --------------------------------------------------
        # COUNT ENTERPRISES
        # --------------------------------------------------

        if contains_any(
            normalized_question,
            [
                "bao nhieu doanh nghiep",
                "co bao nhieu doanh nghiep",
                "co may doanh nghiep",
                "tong so doanh nghiep",
                "so luong doanh nghiep",
            ],
        ):
            return {
                "success": True,
                "reply": (
                    f"Hệ thống AITasker hiện có "
                    f"{len(enterprises)} doanh nghiệp."
                ),
                "source": "database",
            }

        # --------------------------------------------------
        # COUNT PROPOSALS
        # --------------------------------------------------

        if contains_any(
            normalized_question,
            [
                "bao nhieu de xuat",
                "co bao nhieu de xuat",
                "co may de xuat",
                "tong so de xuat",
                "bao nhieu proposal",
                "bao nhieu bao gia",
                "co bao nhieu bao gia",
            ],
        ):
            return {
                "success": True,
                "reply": (
                    f"Hệ thống hiện có "
                    f"{len(proposals)} đề xuất hoặc báo giá."
                ),
                "source": "database",
            }

        # --------------------------------------------------
        # COUNT CONTRACTS
        # --------------------------------------------------

        if contains_any(
            normalized_question,
            [
                "bao nhieu hop dong",
                "co bao nhieu hop dong",
                "co may hop dong",
                "tong so hop dong",
            ],
        ):
            return {
                "success": True,
                "reply": (
                    f"Hệ thống hiện có "
                    f"{len(contracts)} hợp đồng."
                ),
                "source": "database",
            }

        # --------------------------------------------------
        # COUNT PAYMENTS
        # --------------------------------------------------

        if contains_any(
            normalized_question,
            [
                "bao nhieu thanh toan",
                "co bao nhieu thanh toan",
                "co may thanh toan",
                "tong so giao dich",
                "bao nhieu giao dich",
            ],
        ):
            return {
                "success": True,
                "reply": (
                    f"Hệ thống hiện có "
                    f"{len(payments)} giao dịch thanh toán."
                ),
                "source": "database",
            }

        # --------------------------------------------------
        # COUNT REVIEWS
        # --------------------------------------------------

        if contains_any(
            normalized_question,
            [
                "bao nhieu danh gia",
                "co bao nhieu danh gia",
                "co may danh gia",
                "tong so danh gia",
                "bao nhieu review",
            ],
        ):
            return {
                "success": True,
                "reply": (
                    f"Hệ thống hiện có "
                    f"{len(reviews)} đánh giá."
                ),
                "source": "database",
            }

        # --------------------------------------------------
        # COUNT CATEGORIES
        # --------------------------------------------------

        if contains_any(
            normalized_question,
            [
                "bao nhieu danh muc",
                "co bao nhieu danh muc",
                "co may danh muc",
                "tong so danh muc",
                "bao nhieu category",
            ],
        ):
            return {
                "success": True,
                "reply": (
                    f"Hệ thống hiện có "
                    f"{len(categories)} danh mục."
                ),
                "source": "database",
            }

        # --------------------------------------------------
        # COUNT USERS
        # --------------------------------------------------

        if contains_any(
            normalized_question,
            [
                "bao nhieu nguoi dung",
                "co bao nhieu nguoi dung",
                "co may nguoi dung",
                "tong so nguoi dung",
                "bao nhieu user",
            ],
        ):
            return {
                "success": True,
                "reply": (
                    f"Hệ thống hiện có "
                    f"{len(users)} người dùng."
                ),
                "source": "database",
            }

        # --------------------------------------------------
        # PROJECT BUDGET
        # --------------------------------------------------

        asks_budget = contains_any(
            normalized_question,
            [
                "ngan sach",
                "kinh phi",
                "budget",
                "bao nhieu tien",
                "chi phi du an",
            ],
        )

        if asks_budget:
            project = self.resolve_project(
                question,
                projects,
                request,
            )

            if project is None:
                return {
                    "success": True,
                    "reply": (
                        "Bạn muốn xem ngân sách của dự án nào? "
                        "Vui lòng nhập tên dự án."
                    ),
                    "source": "database",
                }

            project_name = get_attribute(
                project,
                "title",
                "name",
                default="Chưa cập nhật",
            )

            project_budget = get_attribute(
                project,
                "budget",
                "total_amount",
                "amount",
                default=0,
            )

            return {
                "success": True,
                "reply": (
                    f'Dự án "{project_name}" có ngân sách '
                    f"{format_vnd(project_budget)} VNĐ."
                ),
                "source": "database",
                "entity_type": "project",
                "entity_id": str(project.id),
            }

        # --------------------------------------------------
        # PROJECT DEADLINE
        # --------------------------------------------------

        asks_deadline = contains_any(
            normalized_question,
            [
                "deadline",
                "han chot",
                "han hoan thanh",
                "ngay ket thuc",
                "ket thuc ngay nao",
            ],
        )

        if asks_deadline:
            project = self.resolve_project(
                question,
                projects,
                request,
            )

            if project is None:
                return {
                    "success": True,
                    "reply": (
                        "Bạn muốn xem deadline của dự án nào? "
                        "Vui lòng nhập tên dự án."
                    ),
                    "source": "database",
                }

            project_name = get_attribute(
                project,
                "title",
                "name",
                default="Chưa cập nhật",
            )

            deadline = get_attribute(
                project,
                "deadline",
                "end_date",
                default=None,
            )

            return {
                "success": True,
                "reply": (
                    f'Dự án "{project_name}" có deadline '
                    f"ngày {format_date(deadline)}."
                ),
                "source": "database",
                "entity_type": "project",
                "entity_id": str(project.id),
            }

        # --------------------------------------------------
        # PROJECT STATUS
        # --------------------------------------------------

        asks_project_status = contains_any(
            normalized_question,
            [
                "trang thai du an",
                "tinh trang du an",
                "tien do du an",
                "dang o trang thai nao",
                "du an dang the nao",
            ],
        )

        if asks_project_status:
            project = self.resolve_project(
                question,
                projects,
                request,
            )

            if project is None:
                return {
                    "success": True,
                    "reply": (
                        "Bạn muốn xem trạng thái của dự án nào?"
                    ),
                    "source": "database",
                }

            project_name = get_attribute(
                project,
                "title",
                "name",
                default="Chưa cập nhật",
            )

            project_status = get_attribute(
                project,
                "status",
                default="Chưa cập nhật",
            )

            return {
                "success": True,
                "reply": (
                    f'Dự án "{project_name}" đang ở trạng thái '
                    f'"{format_status(project_status)}".'
                ),
                "source": "database",
                "entity_type": "project",
                "entity_id": str(project.id),
            }

        # --------------------------------------------------
        # PROJECT DESCRIPTION
        # --------------------------------------------------

        if contains_any(
            normalized_question,
            [
                "mo ta du an",
                "du an lam gi",
                "noi dung du an",
                "thong tin du an",
            ],
        ):
            project = self.resolve_project(
                question,
                projects,
                request,
            )

            if project is None:
                return {
                    "success": True,
                    "reply": (
                        "Bạn muốn xem thông tin của dự án nào?"
                    ),
                    "source": "database",
                }

            project_name = get_attribute(
                project,
                "title",
                "name",
                default="Chưa cập nhật",
            )

            description = get_attribute(
                project,
                "description",
                default="chưa cập nhật",
            )

            return {
                "success": True,
                "reply": (
                    f'Dự án "{project_name}": {description}'
                ),
                "source": "database",
                "entity_type": "project",
                "entity_id": str(project.id),
            }

        # --------------------------------------------------
        # EXPERT SEARCH BY SKILL
        # --------------------------------------------------

        if contains_any(
            normalized_question,
            [
                "chuyen gia nao biet",
                "ai biet",
                "ai co ky nang",
                "tim chuyen gia",
                "chuyen gia co ky nang",
                "chuyen gia thanh thao",
            ],
        ):
            matched_skill: Optional[str] = None

            for skill_name in unique_skill_names:
                if (
                    normalize_text(skill_name)
                    in normalized_question
                ):
                    matched_skill = skill_name
                    break

            if matched_skill is None:
                skill_match = re.search(
                    (
                        r"(?:biet|ky nang|thanh thao|chuyen ve)"
                        r"\s+(.+)"
                    ),
                    normalized_question,
                )

                if skill_match:
                    matched_skill = (
                        skill_match.group(1)
                        .strip(" ?.")
                    )

            if not matched_skill:
                return {
                    "success": True,
                    "reply": (
                        "Bạn muốn tìm chuyên gia theo kỹ năng nào?"
                    ),
                    "source": "database",
                }

            matched_experts: list[str] = []

            for expert in experts:
                expert_skills = serialize_skills(
                    expert
                )

                has_skill = any(
                    (
                        normalize_text(matched_skill)
                        in normalize_text(skill)
                        or normalize_text(skill)
                        in normalize_text(matched_skill)
                    )
                    for skill in expert_skills
                )

                if has_skill:
                    expert_name = get_attribute(
                        expert,
                        "full_name",
                        "name",
                        default="Chưa cập nhật",
                    )

                    matched_experts.append(
                        str(expert_name)
                    )

            if matched_experts:
                return {
                    "success": True,
                    "reply": (
                        f'Các chuyên gia có kỹ năng "{matched_skill}" '
                        f"gồm: {', '.join(matched_experts)}."
                    ),
                    "source": "database",
                }

            return {
                "success": True,
                "reply": (
                    f'Tôi không tìm thấy chuyên gia có kỹ năng '
                    f'"{matched_skill}" trong hệ thống.'
                ),
                "source": "database",
            }

        # --------------------------------------------------
        # EXPERT DETAIL
        # --------------------------------------------------

        expert = self.find_expert(
            question,
            experts,
        )

        if expert is not None:
            self.save_entity_context(
                request,
                "expert",
                expert.id,
            )

            expert_name = get_attribute(
                expert,
                "full_name",
                "name",
                default="Chưa cập nhật",
            )

            if contains_any(
                normalized_question,
                [
                    "ky nang",
                    "biet gi",
                    "chuyen mon",
                    "skill",
                ],
            ):
                expert_skills = serialize_skills(
                    expert
                )

                skill_text = (
                    ", ".join(expert_skills)
                    if expert_skills
                    else "chưa cập nhật kỹ năng"
                )

                return {
                    "success": True,
                    "reply": (
                        f"Chuyên gia {expert_name} có kỹ năng: "
                        f"{skill_text}."
                    ),
                    "source": "database",
                    "entity_type": "expert",
                    "entity_id": str(expert.id),
                }

            if "email" in normalized_question:
                expert_email = get_attribute(
                    expert,
                    "email",
                    default="chưa cập nhật",
                )

                return {
                    "success": True,
                    "reply": (
                        f"Email của chuyên gia {expert_name} là "
                        f"{expert_email}."
                    ),
                    "source": "database",
                    "entity_type": "expert",
                    "entity_id": str(expert.id),
                }

            if contains_any(
                normalized_question,
                [
                    "trang thai",
                    "tinh trang",
                    "co san sang",
                ],
            ):
                expert_status = get_attribute(
                    expert,
                    "status",
                    default="Chưa cập nhật",
                )

                return {
                    "success": True,
                    "reply": (
                        f"Chuyên gia {expert_name} đang ở trạng thái "
                        f'"{format_status(expert_status)}".'
                    ),
                    "source": "database",
                    "entity_type": "expert",
                    "entity_id": str(expert.id),
                }

        # --------------------------------------------------
        # FOLLOW-UP EXPERT QUESTION
        # --------------------------------------------------

        if contains_any(
            normalized_question,
            [
                "nguoi nay co ky nang gi",
                "ho co ky nang gi",
                "chuyen gia nay",
                "email cua ho",
            ],
        ):
            previous_expert = self.resolve_expert(
                question,
                experts,
                request,
            )

            if previous_expert is not None:
                expert_name = get_attribute(
                    previous_expert,
                    "full_name",
                    "name",
                    default="Chưa cập nhật",
                )

                if "email" in normalized_question:
                    expert_email = get_attribute(
                        previous_expert,
                        "email",
                        default="chưa cập nhật",
                    )

                    return {
                        "success": True,
                        "reply": (
                            f"Email của chuyên gia {expert_name} là "
                            f"{expert_email}."
                        ),
                        "source": "database",
                    }

                expert_skills = serialize_skills(
                    previous_expert
                )

                return {
                    "success": True,
                    "reply": (
                        f"Chuyên gia {expert_name} có kỹ năng: "
                        f"{', '.join(expert_skills) if expert_skills else 'chưa cập nhật'}."
                    ),
                    "source": "database",
                }

        # --------------------------------------------------
        # ENTERPRISE DETAIL
        # --------------------------------------------------

        enterprise = self.find_enterprise(
            question,
            enterprises,
        )

        if enterprise is not None:
            enterprise_name = get_attribute(
                enterprise,
                "name",
                "company_name",
                default="Chưa cập nhật",
            )

            if "email" in normalized_question:
                enterprise_email = get_attribute(
                    enterprise,
                    "email",
                    default="chưa cập nhật",
                )

                return {
                    "success": True,
                    "reply": (
                        f'Email của doanh nghiệp "{enterprise_name}" '
                        f"là {enterprise_email}."
                    ),
                    "source": "database",
                }

            if contains_any(
                normalized_question,
                [
                    "ma so thue",
                    "tax code",
                    "tax_code",
                ],
            ):
                tax_code = get_attribute(
                    enterprise,
                    "tax_code",
                    "taxCode",
                    "tax_number",
                    default="chưa cập nhật",
                )

                return {
                    "success": True,
                    "reply": (
                        f'Mã số thuế của doanh nghiệp '
                        f'"{enterprise_name}" là {tax_code}.'
                    ),
                    "source": "database",
                }

        # --------------------------------------------------
        # TOTAL PROJECT BUDGET
        # --------------------------------------------------

        if contains_any(
            normalized_question,
            [
                "tong ngan sach du an",
                "tong ngan sach cac du an",
                "tong kinh phi du an",
            ],
        ):
            total_budget = sum(
                (
                    to_decimal(
                        get_attribute(
                            project,
                            "budget",
                            "total_amount",
                            default=0,
                        )
                    )
                    for project in projects
                ),
                Decimal("0"),
            )

            return {
                "success": True,
                "reply": (
                    f"Tổng ngân sách của tất cả dự án là "
                    f"{format_vnd(total_budget)} VNĐ."
                ),
                "source": "database",
            }

        # --------------------------------------------------
        # HIGHEST BUDGET PROJECT
        # --------------------------------------------------

        if contains_any(
            normalized_question,
            [
                "du an ngan sach cao nhat",
                "du an co ngan sach lon nhat",
                "du an dat nhat",
            ],
        ):
            if not projects:
                return {
                    "success": True,
                    "reply": "Hệ thống hiện chưa có dự án.",
                    "source": "database",
                }

            highest_project = max(
                projects,
                key=lambda project: to_decimal(
                    get_attribute(
                        project,
                        "budget",
                        "total_amount",
                        default=0,
                    )
                ),
            )

            project_name = get_attribute(
                highest_project,
                "title",
                "name",
                default="Chưa cập nhật",
            )

            project_budget = get_attribute(
                highest_project,
                "budget",
                "total_amount",
                default=0,
            )

            return {
                "success": True,
                "reply": (
                    f'Dự án có ngân sách cao nhất là '
                    f'"{project_name}" với '
                    f"{format_vnd(project_budget)} VNĐ."
                ),
                "source": "database",
            }

        # --------------------------------------------------
        # TOTAL PAYMENTS
        # --------------------------------------------------

        if contains_any(
            normalized_question,
            [
                "tong tien thanh toan",
                "tong gia tri thanh toan",
                "da thanh toan bao nhieu",
                "tong doanh thu",
            ],
        ):
            total_amount = sum(
                (
                    to_decimal(
                        get_attribute(
                            payment,
                            "amount",
                            "total_amount",
                            default=0,
                        )
                    )
                    for payment in payments
                ),
                Decimal("0"),
            )

            return {
                "success": True,
                "reply": (
                    f"Tổng giá trị thanh toán trong hệ thống là "
                    f"{format_vnd(total_amount)} VNĐ."
                ),
                "source": "database",
            }

        # --------------------------------------------------
        # AVERAGE RATING
        # --------------------------------------------------

        if contains_any(
            normalized_question,
            [
                "diem danh gia trung binh",
                "rating trung binh",
                "danh gia trung binh",
                "diem trung binh",
            ],
        ):
            ratings: list[float] = []

            for review in reviews:
                rating = get_attribute(
                    review,
                    "rating",
                    default=None,
                )

                if rating is None:
                    continue

                try:
                    ratings.append(
                        float(rating)
                    )
                except (ValueError, TypeError):
                    continue

            average_rating = (
                sum(ratings) / len(ratings)
                if ratings
                else 0
            )

            return {
                "success": True,
                "reply": (
                    f"Điểm đánh giá trung bình hiện tại là "
                    f"{average_rating:.2f}/5."
                ),
                "source": "database",
            }

        return None

    # ======================================================
    # DATABASE CONTEXT FOR GEMINI
    # ======================================================

    def build_database_context(
        self,
        data: dict[str, list[Any]],
    ) -> str:
        """
        Chuyển dữ liệu PostgreSQL thành context có cấu trúc.

        Gemini chỉ được phép trả lời dựa trên context này.
        """

        sections: list[str] = []

        projects = data.get("projects", [])
        experts = data.get("experts", [])
        enterprises = data.get("enterprises", [])
        proposals = data.get("proposals", [])
        contracts = data.get("contracts", [])
        payments = data.get("payments", [])
        reviews = data.get("reviews", [])
        skills = data.get("skills", [])
        categories = data.get("categories", [])
        users = data.get("users", [])

        # --------------------------------------------------
        # SYSTEM SUMMARY
        # --------------------------------------------------

        unique_skill_names = get_unique_skill_names(
            skills,
            experts,
        )

        sections.append(
            "\n".join(
                [
                    "TỔNG QUAN HỆ THỐNG:",
                    f"- Số dự án: {len(projects)}",
                    f"- Số chuyên gia: {len(experts)}",
                    f"- Số kỹ năng core: {len(unique_skill_names)}",
                    f"- Số doanh nghiệp: {len(enterprises)}",
                    f"- Số đề xuất: {len(proposals)}",
                    f"- Số hợp đồng: {len(contracts)}",
                    f"- Số thanh toán: {len(payments)}",
                    f"- Số đánh giá: {len(reviews)}",
                    f"- Số danh mục: {len(categories)}",
                    f"- Số người dùng: {len(users)}",
                ]
            )
        )

        # --------------------------------------------------
        # PROJECTS
        # --------------------------------------------------

        project_lines = ["DỰ ÁN:"]

        for project in projects:
            project_lines.append(
                (
                    f"- ID: {get_attribute(project, 'id', default='')}; "
                    f"tên: {get_attribute(project, 'title', 'name', default='Chưa cập nhật')}; "
                    f"ngân sách: "
                    f"{format_vnd(get_attribute(project, 'budget', 'total_amount', default=0))} VNĐ; "
                    f"deadline: "
                    f"{format_date(get_attribute(project, 'deadline', 'end_date', default=None))}; "
                    f"trạng thái: "
                    f"{format_status(get_attribute(project, 'status', default='Chưa cập nhật'))}; "
                    f"mô tả: "
                    f"{get_attribute(project, 'description', default='chưa cập nhật')}."
                )
            )

        if len(project_lines) == 1:
            project_lines.append(
                "- Chưa có dữ liệu dự án."
            )

        sections.append(
            "\n".join(project_lines)
        )

        # --------------------------------------------------
        # EXPERTS
        # --------------------------------------------------

        expert_lines = ["CHUYÊN GIA:"]

        for expert in experts:
            skill_text = (
                ", ".join(
                    serialize_skills(expert)
                )
                or "chưa cập nhật"
            )

            expert_lines.append(
                (
                    f"- ID: {get_attribute(expert, 'id', default='')}; "
                    f"họ tên: "
                    f"{get_attribute(expert, 'full_name', 'name', default='Chưa cập nhật')}; "
                    f"email: "
                    f"{get_attribute(expert, 'email', default='chưa cập nhật')}; "
                    f"kỹ năng: {skill_text}; "
                    f"trạng thái: "
                    f"{format_status(get_attribute(expert, 'status', default='Chưa cập nhật'))}."
                )
            )

        if len(expert_lines) == 1:
            expert_lines.append(
                "- Chưa có dữ liệu chuyên gia."
            )

        sections.append(
            "\n".join(expert_lines)
        )

        # --------------------------------------------------
        # SKILLS
        # --------------------------------------------------

        skill_lines = ["KỸ NĂNG CORE:"]

        for skill_name in unique_skill_names:
            skill_lines.append(
                f"- {skill_name}"
            )

        if len(skill_lines) == 1:
            skill_lines.append(
                "- Chưa có dữ liệu kỹ năng."
            )

        sections.append(
            "\n".join(skill_lines)
        )

        # --------------------------------------------------
        # ENTERPRISES
        # --------------------------------------------------

        enterprise_lines = ["DOANH NGHIỆP:"]

        for enterprise in enterprises:
            enterprise_lines.append(
                (
                    f"- ID: {get_attribute(enterprise, 'id', default='')}; "
                    f"tên: "
                    f"{get_attribute(enterprise, 'name', 'company_name', default='Chưa cập nhật')}; "
                    f"email: "
                    f"{get_attribute(enterprise, 'email', default='chưa cập nhật')}; "
                    f"mã số thuế: "
                    f"{get_attribute(enterprise, 'tax_code', 'taxCode', 'tax_number', default='chưa cập nhật')}; "
                    f"trạng thái: "
                    f"{format_status(get_attribute(enterprise, 'status', default='Chưa cập nhật'))}."
                )
            )

        if len(enterprise_lines) == 1:
            enterprise_lines.append(
                "- Chưa có dữ liệu doanh nghiệp."
            )

        sections.append(
            "\n".join(enterprise_lines)
        )

        # --------------------------------------------------
        # PROPOSALS
        # --------------------------------------------------

        proposal_lines = ["ĐỀ XUẤT / BÁO GIÁ:"]

        for proposal in proposals:
            proposal_lines.append(
                (
                    f"- ID: {get_attribute(proposal, 'id', default='')}; "
                    f"project_id: "
                    f"{get_attribute(proposal, 'project_id', default='')}; "
                    f"expert_id: "
                    f"{get_attribute(proposal, 'expert_id', default='')}; "
                    f"giá đề xuất: "
                    f"{format_vnd(get_attribute(proposal, 'bid_amount', 'price', 'amount', default=0))} VNĐ; "
                    f"trạng thái: "
                    f"{format_status(get_attribute(proposal, 'status', default='Chưa cập nhật'))}."
                )
            )

        if len(proposal_lines) == 1:
            proposal_lines.append(
                "- Chưa có dữ liệu đề xuất."
            )

        sections.append(
            "\n".join(proposal_lines)
        )

        # --------------------------------------------------
        # CONTRACTS
        # --------------------------------------------------

        contract_lines = ["HỢP ĐỒNG:"]

        for contract in contracts:
            contract_lines.append(
                (
                    f"- ID: {get_attribute(contract, 'id', default='')}; "
                    f"project_id: "
                    f"{get_attribute(contract, 'project_id', default='')}; "
                    f"expert_id: "
                    f"{get_attribute(contract, 'expert_id', default='')}; "
                    f"tiêu đề: "
                    f"{get_attribute(contract, 'title', default='chưa cập nhật')}; "
                    f"giá trị: "
                    f"{format_vnd(get_attribute(contract, 'total_amount', 'amount', default=0))} VNĐ; "
                    f"điều khoản: "
                    f"{get_attribute(contract, 'terms', default='chưa cập nhật')}; "
                    f"trạng thái: "
                    f"{format_status(get_attribute(contract, 'status', default='Chưa cập nhật'))}."
                )
            )

        if len(contract_lines) == 1:
            contract_lines.append(
                "- Chưa có dữ liệu hợp đồng."
            )

        sections.append(
            "\n".join(contract_lines)
        )

        # --------------------------------------------------
        # PAYMENTS
        # --------------------------------------------------

        payment_lines = ["THANH TOÁN:"]

        for payment in payments:
            payment_lines.append(
                (
                    f"- ID: {get_attribute(payment, 'id', default='')}; "
                    f"contract_id: "
                    f"{get_attribute(payment, 'contract_id', default='')}; "
                    f"số tiền: "
                    f"{format_vnd(get_attribute(payment, 'amount', 'total_amount', default=0))} VNĐ; "
                    f"phương thức: "
                    f"{get_attribute(payment, 'method', 'payment_method', default='chưa cập nhật')}; "
                    f"trạng thái: "
                    f"{format_status(get_attribute(payment, 'status', default='Chưa cập nhật'))}."
                )
            )

        if len(payment_lines) == 1:
            payment_lines.append(
                "- Chưa có dữ liệu thanh toán."
            )

        sections.append(
            "\n".join(payment_lines)
        )

        # --------------------------------------------------
        # REVIEWS
        # --------------------------------------------------

        review_lines = ["ĐÁNH GIÁ:"]

        for review in reviews:
            review_lines.append(
                (
                    f"- ID: {get_attribute(review, 'id', default='')}; "
                    f"project_id: "
                    f"{get_attribute(review, 'project_id', default='')}; "
                    f"expert_id: "
                    f"{get_attribute(review, 'expert_id', default='')}; "
                    f"điểm: "
                    f"{get_attribute(review, 'rating', default='chưa cập nhật')}; "
                    f"nhận xét: "
                    f"{get_attribute(review, 'comment', default='chưa cập nhật')}."
                )
            )

        if len(review_lines) == 1:
            review_lines.append(
                "- Chưa có dữ liệu đánh giá."
            )

        sections.append(
            "\n".join(review_lines)
        )

        # --------------------------------------------------
        # CATEGORIES
        # --------------------------------------------------

        category_lines = ["DANH MỤC:"]

        for category in categories:
            category_lines.append(
                (
                    f"- ID: {get_attribute(category, 'id', default='')}; "
                    f"tên: "
                    f"{get_attribute(category, 'name', 'title', default='Chưa cập nhật')}; "
                    f"mô tả: "
                    f"{get_attribute(category, 'description', default='chưa cập nhật')}."
                )
            )

        if len(category_lines) == 1:
            category_lines.append(
                "- Chưa có dữ liệu danh mục."
            )

        sections.append(
            "\n".join(category_lines)
        )

        return "\n\n".join(sections)