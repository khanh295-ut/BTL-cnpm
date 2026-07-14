from __future__ import annotations

import logging
import re
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from backend.src.models.expert import Expert
from backend.src.models.project import Project
from backend.src.models.proposal import Proposal
from backend.src.models.recommendation import Recommendation
from backend.src.models.review import Review
from backend.src.models.skill import Skill
from backend.src.schemas.recommendation import (
    RecommendationCreate,
    RecommendationFeedbackUpdate,
    RecommendationGenerateRequest,
    RecommendationUpdate,
)


logger = logging.getLogger(
    "AITasker.RecommendationService"
)


class RecommendationService:
    """
    Service gợi ý chuyên gia phù hợp với dự án.

    Thuật toán v1.0:

        match_score =
            skill_score      * 0.45
            + rating_score   * 0.25
            + experience     * 0.20
            + price_score    * 0.10

    Các thang điểm thành phần đều nằm trong khoảng 0–100.
    """

    SKILL_WEIGHT = Decimal("0.45")
    RATING_WEIGHT = Decimal("0.25")
    EXPERIENCE_WEIGHT = Decimal("0.20")
    PRICE_WEIGHT = Decimal("0.10")

    DEFAULT_ALGORITHM_VERSION = "v1.0"

    # ======================================================
    # HELPERS
    # ======================================================

    @staticmethod
    def _decimal(value) -> Decimal:
        if value is None:
            return Decimal("0.00")

        if isinstance(value, Decimal):
            return value

        return Decimal(str(value))

    @staticmethod
    def _round_score(value) -> Decimal:
        score = Decimal(str(value))

        if score < Decimal("0"):
            score = Decimal("0")

        if score > Decimal("100"):
            score = Decimal("100")

        return score.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    @staticmethod
    def _normalize_text(value: str | None) -> str:
        """
        Chuẩn hóa chuỗi để so khớp kỹ năng.
        """
        normalized = str(value or "").strip().lower()

        normalized = re.sub(
            r"[^a-zA-Z0-9À-ỹ+#.\-\s]",
            " ",
            normalized,
        )

        normalized = re.sub(
            r"\s+",
            " ",
            normalized,
        )

        return normalized.strip()

    @staticmethod
    def _tokenize(value: str | None) -> set[str]:
        normalized = RecommendationService._normalize_text(
            value
        )

        if not normalized:
            return set()

        ignored_words = {
            "và",
            "của",
            "cho",
            "với",
            "các",
            "một",
            "những",
            "trong",
            "the",
            "and",
            "for",
            "with",
            "from",
            "that",
            "this",
            "project",
            "dự",
            "án",
            "hệ",
            "thống",
            "cần",
            "xây",
            "dựng",
            "phát",
            "triển",
        }

        return {
            token
            for token in normalized.split()
            if len(token) >= 2
            and token not in ignored_words
        }

    @staticmethod
    def _normalize_name(value: str | None) -> str:
        return RecommendationService._normalize_text(
            value
        )

    @staticmethod
    def _level_from_score(
        score: Decimal,
    ) -> str:
        if score >= Decimal("85"):
            return "VERY_HIGH"

        if score >= Decimal("70"):
            return "HIGH"

        if score >= Decimal("50"):
            return "MEDIUM"

        return "LOW"

    # ======================================================
    # GET PROJECT
    # ======================================================

    def _get_project(
        self,
        db: Session,
        project_id: UUID,
    ) -> Project:
        project = (
            db.query(Project)
            .filter(Project.id == project_id)
            .first()
        )

        if project is None:
            raise ValueError(
                "Project not found."
            )

        return project

    # ======================================================
    # GET EXPERT
    # ======================================================

    def _get_expert(
        self,
        db: Session,
        expert_id: UUID,
    ) -> Expert:
        expert = (
            db.query(Expert)
            .options(
                selectinload(Expert.skills)
            )
            .filter(Expert.id == expert_id)
            .first()
        )

        if expert is None:
            raise ValueError(
                "Expert not found."
            )

        return expert

    # ======================================================
    # PROJECT TEXT
    # ======================================================

    def _project_text(
        self,
        project: Project,
    ) -> str:
        category_name = ""

        category = getattr(
            project,
            "category",
            None,
        )

        if category is not None:
            category_name = str(
                getattr(
                    category,
                    "name",
                    "",
                )
                or ""
            )

        return " ".join(
            [
                str(project.title or ""),
                str(project.description or ""),
                category_name,
            ]
        )

    # ======================================================
    # EXTRACT PROJECT SKILLS
    # ======================================================

    def _extract_project_skills(
        self,
        db: Session,
        project: Project,
    ) -> list[str]:
        """
        Trích xuất kỹ năng yêu cầu từ nội dung dự án.

        Vì Project hiện chưa có bảng project_skills,
        service sẽ so khớp tên các Skill có trong hệ thống
        với title, description và category của Project.
        """

        project_text = self._normalize_text(
            self._project_text(project)
        )

        all_skill_names = (
            db.query(Skill.name)
            .filter(Skill.name.isnot(None))
            .distinct()
            .all()
        )

        detected: list[str] = []

        for row in all_skill_names:
            skill_name = str(row[0] or "").strip()

            if not skill_name:
                continue

            normalized_skill = self._normalize_name(
                skill_name
            )

            if (
                normalized_skill
                and normalized_skill in project_text
            ):
                detected.append(skill_name)

        unique_skills: dict[str, str] = {}

        for skill in detected:
            normalized = self._normalize_name(
                skill
            )

            unique_skills[normalized] = skill

        return sorted(
            unique_skills.values(),
            key=str.lower,
        )

    # ======================================================
    # EXPERT SKILLS
    # ======================================================

    def _expert_skills(
        self,
        expert: Expert,
    ) -> list[str]:
        skills = getattr(
            expert,
            "skills",
            [],
        ) or []

        result: list[str] = []

        for item in skills:
            name = str(
                getattr(
                    item,
                    "name",
                    "",
                )
                or ""
            ).strip()

            if name:
                result.append(name)

        unique: dict[str, str] = {}

        for name in result:
            unique[
                self._normalize_name(name)
            ] = name

        return sorted(
            unique.values(),
            key=str.lower,
        )

    # ======================================================
    # SKILL SCORE
    # ======================================================

    def _calculate_skill_score(
        self,
        *,
        project: Project,
        project_skills: list[str],
        expert_skills: list[str],
    ) -> tuple[
        Decimal,
        list[str],
        list[str],
    ]:
        required_map = {
            self._normalize_name(skill): skill
            for skill in project_skills
        }

        expert_map = {
            self._normalize_name(skill): skill
            for skill in expert_skills
        }

        required_names = set(
            required_map.keys()
        )

        expert_names = set(
            expert_map.keys()
        )

        matched_names = (
            required_names & expert_names
        )

        missing_names = (
            required_names - expert_names
        )

        matched_skills = [
            required_map[name]
            for name in sorted(matched_names)
        ]

        missing_skills = [
            required_map[name]
            for name in sorted(missing_names)
        ]

        if required_names:
            score = (
                Decimal(len(matched_names))
                / Decimal(len(required_names))
                * Decimal("100")
            )

            return (
                self._round_score(score),
                matched_skills,
                missing_skills,
            )

        # Fallback khi mô tả dự án không chứa tên Skill rõ ràng.
        project_tokens = self._tokenize(
            self._project_text(project)
        )

        expert_tokens: set[str] = set()

        for skill in expert_skills:
            expert_tokens.update(
                self._tokenize(skill)
            )

        if not project_tokens or not expert_tokens:
            return (
                Decimal("0.00"),
                [],
                [],
            )

        token_matches = (
            project_tokens & expert_tokens
        )

        score = (
            Decimal(len(token_matches))
            / Decimal(len(expert_tokens))
            * Decimal("100")
        )

        fallback_matches = sorted(
            {
                skill
                for skill in expert_skills
                if self._tokenize(skill)
                & project_tokens
            },
            key=str.lower,
        )

        return (
            self._round_score(score),
            fallback_matches,
            [],
        )

    # ======================================================
    # RATING SCORE
    # ======================================================

    def _calculate_rating_score(
        self,
        db: Session,
        expert_id: UUID,
    ) -> tuple[Decimal, Decimal, int]:
        row = (
            db.query(
                func.coalesce(
                    func.avg(Review.rating),
                    0,
                ).label("average_rating"),
                func.count(
                    Review.id
                ).label("review_count"),
            )
            .filter(
                Review.expert_id == expert_id
            )
            .first()
        )

        average_rating = self._decimal(
            row.average_rating
            if row is not None
            else 0
        )

        review_count = int(
            row.review_count
            if row is not None
            else 0
        )

        if average_rating <= Decimal("0"):
            return (
                Decimal("0.00"),
                Decimal("0.00"),
                review_count,
            )

        score = (
            average_rating
            / Decimal("5")
            * Decimal("100")
        )

        # Giảm nhẹ điểm khi chuyên gia chỉ có rất ít review.
        confidence_factor = min(
            Decimal("1.00"),
            Decimal(review_count)
            / Decimal("5"),
        )

        adjusted_score = (
            score
            * (
                Decimal("0.70")
                + Decimal("0.30")
                * confidence_factor
            )
        )

        return (
            self._round_score(adjusted_score),
            average_rating.quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            ),
            review_count,
        )

    # ======================================================
    # ACCEPTED PROPOSAL COUNT
    # ======================================================

    def _accepted_proposal_count(
        self,
        db: Session,
        expert_id: UUID,
    ) -> int:
        return int(
            (
                db.query(
                    func.count(Proposal.id)
                )
                .filter(
                    Proposal.expert_id
                    == expert_id,
                    func.upper(
                        Proposal.status
                    )
                    == "ACCEPTED",
                )
                .scalar()
            )
            or 0
        )

    # ======================================================
    # EXPERIENCE SCORE
    # ======================================================

    def _calculate_experience_score(
        self,
        accepted_count: int,
        max_accepted_count: int,
    ) -> Decimal:
        if max_accepted_count <= 0:
            return Decimal("0.00")

        normalized = (
            Decimal(accepted_count)
            / Decimal(max_accepted_count)
            * Decimal("100")
        )

        return self._round_score(
            normalized
        )

    # ======================================================
    # PRICE SCORE
    # ======================================================

    def _calculate_price_score(
        self,
        project: Project,
        expert: Expert,
    ) -> Decimal:
        """
        So sánh hourly_rate với ngân sách dự án.

        Do Project hiện chỉ có tổng budget và chưa có
        estimated_hours, thuật toán dùng ngưỡng ước lượng:

            target_hourly_rate = budget / 160

        160 giờ tương đương khoảng một tháng làm việc.
        """

        budget = self._decimal(
            project.budget
        )

        hourly_rate = self._decimal(
            expert.hourly_rate
        )

        if hourly_rate <= Decimal("0"):
            return Decimal("50.00")

        if budget <= Decimal("0"):
            return Decimal("50.00")

        target_hourly_rate = (
            budget / Decimal("160")
        )

        if target_hourly_rate <= Decimal("0"):
            return Decimal("50.00")

        ratio = (
            hourly_rate
            / target_hourly_rate
        )

        if ratio <= Decimal("1"):
            score = Decimal("100")
        elif ratio <= Decimal("1.25"):
            score = Decimal("85")
        elif ratio <= Decimal("1.50"):
            score = Decimal("70")
        elif ratio <= Decimal("2.00"):
            score = Decimal("45")
        else:
            score = Decimal("20")

        return self._round_score(
            score
        )

    # ======================================================
    # FINAL SCORE
    # ======================================================

    def _calculate_final_score(
        self,
        *,
        skill_score: Decimal,
        rating_score: Decimal,
        experience_score: Decimal,
        price_score: Decimal,
    ) -> Decimal:
        total = (
            skill_score
            * self.SKILL_WEIGHT
            + rating_score
            * self.RATING_WEIGHT
            + experience_score
            * self.EXPERIENCE_WEIGHT
            + price_score
            * self.PRICE_WEIGHT
        )

        return self._round_score(
            total
        )

    # ======================================================
    # REASON
    # ======================================================

    def _build_reason(
        self,
        *,
        match_score: Decimal,
        matched_skills: list[str],
        missing_skills: list[str],
        average_rating: Decimal,
        accepted_count: int,
        price_score: Decimal,
    ) -> str:
        parts: list[str] = []

        if matched_skills:
            parts.append(
                "Phù hợp các kỹ năng: "
                + ", ".join(matched_skills)
                + "."
            )
        else:
            parts.append(
                "Chưa phát hiện kỹ năng trùng khớp rõ ràng."
            )

        if missing_skills:
            parts.append(
                "Còn thiếu: "
                + ", ".join(missing_skills)
                + "."
            )

        if average_rating > Decimal("0"):
            parts.append(
                f"Đánh giá trung bình {average_rating}/5."
            )
        else:
            parts.append(
                "Chưa có dữ liệu đánh giá."
            )

        parts.append(
            f"Đã có {accepted_count} đề xuất được chấp nhận."
        )

        if price_score >= Decimal("80"):
            parts.append(
                "Mức giá phù hợp với ngân sách dự án."
            )
        elif price_score < Decimal("50"):
            parts.append(
                "Mức giá có thể vượt ngân sách ước tính."
            )

        if match_score >= Decimal("85"):
            parts.append(
                "Đây là chuyên gia rất phù hợp."
            )
        elif match_score >= Decimal("70"):
            parts.append(
                "Đây là chuyên gia phù hợp cao."
            )
        elif match_score >= Decimal("50"):
            parts.append(
                "Chuyên gia có mức phù hợp trung bình."
            )
        else:
            parts.append(
                "Mức phù hợp hiện tại còn thấp."
            )

        return " ".join(parts)

    # ======================================================
    # GET ALL
    # ======================================================

    def get_all(
        self,
        db: Session,
    ) -> list[Recommendation]:
        return (
            db.query(Recommendation)
            .order_by(
                Recommendation.created_at.desc()
            )
            .all()
        )

    # ======================================================
    # GET BY ID
    # ======================================================

    def get_by_id(
        self,
        db: Session,
        recommendation_id: UUID,
    ) -> Recommendation | None:
        return (
            db.query(Recommendation)
            .filter(
                Recommendation.id
                == recommendation_id
            )
            .first()
        )

    # ======================================================
    # GET BY PROJECT
    # ======================================================

    def get_by_project(
        self,
        db: Session,
        project_id: UUID,
        limit: int | None = None,
    ) -> list[Recommendation]:
        query = (
            db.query(Recommendation)
            .filter(
                Recommendation.project_id
                == project_id
            )
            .order_by(
                Recommendation.match_score.desc()
            )
        )

        if limit is not None:
            query = query.limit(limit)

        return query.all()

    # ======================================================
    # GET BY EXPERT
    # ======================================================

    def get_by_expert(
        self,
        db: Session,
        expert_id: UUID,
    ) -> list[Recommendation]:
        return (
            db.query(Recommendation)
            .filter(
                Recommendation.expert_id
                == expert_id
            )
            .order_by(
                Recommendation.match_score.desc()
            )
            .all()
        )

    # ======================================================
    # CREATE
    # ======================================================

    def create(
        self,
        db: Session,
        data: RecommendationCreate,
    ) -> Recommendation:
        try:
            self._get_project(
                db=db,
                project_id=data.project_id,
            )

            self._get_expert(
                db=db,
                expert_id=data.expert_id,
            )

            existing = (
                db.query(Recommendation)
                .filter(
                    Recommendation.project_id
                    == data.project_id,
                    Recommendation.expert_id
                    == data.expert_id,
                )
                .first()
            )

            if existing is not None:
                raise ValueError(
                    "Recommendation already exists "
                    "for this project and expert."
                )

            now = datetime.utcnow()

            recommendation = Recommendation(
                project_id=data.project_id,
                expert_id=data.expert_id,
                match_score=data.match_score,
                skill_score=data.skill_score,
                rating_score=data.rating_score,
                experience_score=(
                    data.experience_score
                ),
                price_score=data.price_score,
                matched_skills=data.matched_skills,
                missing_skills=data.missing_skills,
                reason=data.reason,
                recommendation_level=(
                    data.recommendation_level
                ),
                algorithm_version=(
                    data.algorithm_version
                ),
                was_viewed="NO",
                was_selected="NO",
                feedback=None,
                created_at=now,
                updated_at=now,
            )

            db.add(recommendation)
            db.commit()
            db.refresh(recommendation)

            return recommendation

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể tạo recommendation."
            )

            raise

    # ======================================================
    # UPDATE
    # ======================================================

    def update(
        self,
        db: Session,
        recommendation_id: UUID,
        data: RecommendationUpdate,
    ) -> Recommendation | None:
        recommendation = self.get_by_id(
            db=db,
            recommendation_id=recommendation_id,
        )

        if recommendation is None:
            return None

        try:
            update_data = data.model_dump(
                exclude_unset=True
            )

            for field_name, value in update_data.items():
                setattr(
                    recommendation,
                    field_name,
                    value,
                )

            recommendation.updated_at = (
                datetime.utcnow()
            )

            db.commit()
            db.refresh(recommendation)

            return recommendation

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể cập nhật recommendation %s.",
                recommendation_id,
            )

            raise

    # ======================================================
    # UPSERT GENERATED RECOMMENDATION
    # ======================================================

    def _save_generated_result(
        self,
        db: Session,
        *,
        project: Project,
        expert: Expert,
        match_score: Decimal,
        skill_score: Decimal,
        rating_score: Decimal,
        experience_score: Decimal,
        price_score: Decimal,
        matched_skills: list[str],
        missing_skills: list[str],
        reason: str,
        recommendation_level: str,
        algorithm_version: str,
    ) -> Recommendation:
        recommendation = (
            db.query(Recommendation)
            .filter(
                Recommendation.project_id
                == project.id,
                Recommendation.expert_id
                == expert.id,
            )
            .first()
        )

        now = datetime.utcnow()

        if recommendation is None:
            recommendation = Recommendation(
                project_id=project.id,
                expert_id=expert.id,
                was_viewed="NO",
                was_selected="NO",
                feedback=None,
                created_at=now,
            )

            db.add(recommendation)

        recommendation.match_score = match_score
        recommendation.skill_score = skill_score
        recommendation.rating_score = rating_score
        recommendation.experience_score = (
            experience_score
        )
        recommendation.price_score = price_score
        recommendation.matched_skills = (
            matched_skills
        )
        recommendation.missing_skills = (
            missing_skills
        )
        recommendation.reason = reason
        recommendation.recommendation_level = (
            recommendation_level
        )
        recommendation.algorithm_version = (
            algorithm_version
        )
        recommendation.updated_at = now

        return recommendation

    # ======================================================
    # GENERATE
    # ======================================================

    def generate(
        self,
        db: Session,
        data: RecommendationGenerateRequest,
    ) -> dict:
        try:
            project = self._get_project(
                db=db,
                project_id=data.project_id,
            )

            if not data.force_refresh:
                cached = self.get_by_project(
                    db=db,
                    project_id=project.id,
                    limit=data.limit,
                )

                cached_for_version = [
                    item
                    for item in cached
                    if item.algorithm_version
                    == data.algorithm_version
                ]

                if cached_for_version:
                    return self._build_generate_response(
                        project=project,
                        recommendations=(
                            cached_for_version[
                                : data.limit
                            ]
                        ),
                        total_candidates=(
                            len(cached_for_version)
                        ),
                        algorithm_version=(
                            data.algorithm_version
                        ),
                    )

            experts = (
                db.query(Expert)
                .options(
                    selectinload(
                        Expert.skills
                    )
                )
                .all()
            )

            if not experts:
                return {
                    "project_id": project.id,
                    "total_candidates": 0,
                    "algorithm_version": (
                        data.algorithm_version
                    ),
                    "generated_at": datetime.utcnow(),
                    "recommendations": [],
                }

            project_skills = (
                self._extract_project_skills(
                    db=db,
                    project=project,
                )
            )

            accepted_counts: dict[
                UUID,
                int,
            ] = {}

            for expert in experts:
                accepted_counts[expert.id] = (
                    self._accepted_proposal_count(
                        db=db,
                        expert_id=expert.id,
                    )
                )

            max_accepted_count = max(
                accepted_counts.values(),
                default=0,
            )

            generated: list[Recommendation] = []

            for expert in experts:
                expert_skills = self._expert_skills(
                    expert
                )

                (
                    skill_score,
                    matched_skills,
                    missing_skills,
                ) = self._calculate_skill_score(
                    project=project,
                    project_skills=project_skills,
                    expert_skills=expert_skills,
                )

                (
                    rating_score,
                    average_rating,
                    _review_count,
                ) = self._calculate_rating_score(
                    db=db,
                    expert_id=expert.id,
                )

                accepted_count = accepted_counts[
                    expert.id
                ]

                experience_score = (
                    self._calculate_experience_score(
                        accepted_count=accepted_count,
                        max_accepted_count=(
                            max_accepted_count
                        ),
                    )
                )

                price_score = (
                    self._calculate_price_score(
                        project=project,
                        expert=expert,
                    )
                )

                match_score = (
                    self._calculate_final_score(
                        skill_score=skill_score,
                        rating_score=rating_score,
                        experience_score=(
                            experience_score
                        ),
                        price_score=price_score,
                    )
                )

                recommendation_level = (
                    self._level_from_score(
                        match_score
                    )
                )

                reason = self._build_reason(
                    match_score=match_score,
                    matched_skills=matched_skills,
                    missing_skills=missing_skills,
                    average_rating=average_rating,
                    accepted_count=accepted_count,
                    price_score=price_score,
                )

                recommendation = (
                    self._save_generated_result(
                        db=db,
                        project=project,
                        expert=expert,
                        match_score=match_score,
                        skill_score=skill_score,
                        rating_score=rating_score,
                        experience_score=(
                            experience_score
                        ),
                        price_score=price_score,
                        matched_skills=(
                            matched_skills
                        ),
                        missing_skills=(
                            missing_skills
                        ),
                        reason=reason,
                        recommendation_level=(
                            recommendation_level
                        ),
                        algorithm_version=(
                            data.algorithm_version
                        ),
                    )
                )

                generated.append(
                    recommendation
                )

            db.flush()

            generated.sort(
                key=lambda item: self._decimal(
                    item.match_score
                ),
                reverse=True,
            )

            # Xóa cache cũ không nằm trong kết quả mới
            # chỉ khi force_refresh được bật.
            if data.force_refresh:
                expert_ids = {
                    expert.id
                    for expert in experts
                }

                stale_items = (
                    db.query(Recommendation)
                    .filter(
                        Recommendation.project_id
                        == project.id,
                        Recommendation.expert_id.notin_(
                            expert_ids
                        ),
                    )
                    .all()
                )

                for item in stale_items:
                    db.delete(item)

            db.commit()

            selected = generated[
                : data.limit
            ]

            for item in selected:
                db.refresh(item)

            logger.info(
                "Generated %s recommendations "
                "for project %s.",
                len(generated),
                project.id,
            )

            return self._build_generate_response(
                project=project,
                recommendations=selected,
                total_candidates=len(generated),
                algorithm_version=(
                    data.algorithm_version
                ),
            )

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể tạo recommendation "
                "cho project %s.",
                data.project_id,
            )

            raise

    # ======================================================
    # BUILD GENERATE RESPONSE
    # ======================================================

    def _build_generate_response(
        self,
        *,
        project: Project,
        recommendations: list[
            Recommendation
        ],
        total_candidates: int,
        algorithm_version: str,
    ) -> dict:
        items: list[dict] = []

        for recommendation in recommendations:
            expert = recommendation.expert

            items.append(
                {
                    "recommendation_id": (
                        recommendation.id
                    ),
                    "expert_id": (
                        recommendation.expert_id
                    ),
                    "expert_name": (
                        expert.full_name
                        if expert
                        else "Unknown expert"
                    ),
                    "expert_title": (
                        expert.title
                        if expert
                        else None
                    ),
                    "hourly_rate": (
                        self._decimal(
                            expert.hourly_rate
                        )
                        if expert
                        else Decimal("0.00")
                    ),
                    "location": (
                        expert.location
                        if expert
                        else None
                    ),
                    "match_score": (
                        self._decimal(
                            recommendation.match_score
                        )
                    ),
                    "recommendation_level": (
                        recommendation
                        .recommendation_level
                    ),
                    "matched_skills": (
                        recommendation.matched_skills
                        or []
                    ),
                    "missing_skills": (
                        recommendation.missing_skills
                        or []
                    ),
                    "reason": (
                        recommendation.reason
                    ),
                    "score_breakdown": {
                        "skill_score": self._decimal(
                            recommendation.skill_score
                        ),
                        "rating_score": self._decimal(
                            recommendation.rating_score
                        ),
                        "experience_score": self._decimal(
                            recommendation.experience_score
                        ),
                        "price_score": self._decimal(
                            recommendation.price_score
                        ),
                    },
                }
            )

        return {
            "project_id": project.id,
            "total_candidates": total_candidates,
            "algorithm_version": (
                algorithm_version
            ),
            "generated_at": datetime.utcnow(),
            "recommendations": items,
        }

    # ======================================================
    # FEEDBACK
    # ======================================================

    def update_feedback(
        self,
        db: Session,
        recommendation_id: UUID,
        data: RecommendationFeedbackUpdate,
    ) -> Recommendation | None:
        recommendation = self.get_by_id(
            db=db,
            recommendation_id=(
                recommendation_id
            ),
        )

        if recommendation is None:
            return None

        try:
            update_data = data.model_dump(
                exclude_unset=True
            )

            if "was_viewed" in update_data:
                recommendation.was_viewed = (
                    "YES"
                    if update_data["was_viewed"]
                    else "NO"
                )

            if "was_selected" in update_data:
                recommendation.was_selected = (
                    "YES"
                    if update_data["was_selected"]
                    else "NO"
                )

            if "feedback" in update_data:
                recommendation.feedback = (
                    update_data["feedback"].strip()
                    if update_data["feedback"]
                    else None
                )

            recommendation.updated_at = (
                datetime.utcnow()
            )

            db.commit()
            db.refresh(recommendation)

            return recommendation

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể cập nhật feedback "
                "của recommendation %s.",
                recommendation_id,
            )

            raise

    # ======================================================
    # DELETE
    # ======================================================

    def delete(
        self,
        db: Session,
        recommendation_id: UUID,
    ) -> bool:
        recommendation = self.get_by_id(
            db=db,
            recommendation_id=(
                recommendation_id
            ),
        )

        if recommendation is None:
            return False

        try:
            db.delete(recommendation)
            db.commit()

            return True

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể xóa recommendation %s.",
                recommendation_id,
            )

            raise

    # ======================================================
    # DELETE BY PROJECT
    # ======================================================

    def delete_by_project(
        self,
        db: Session,
        project_id: UUID,
    ) -> int:
        try:
            recommendations = (
                db.query(Recommendation)
                .filter(
                    Recommendation.project_id
                    == project_id
                )
                .all()
            )

            total = len(
                recommendations
            )

            for recommendation in recommendations:
                db.delete(
                    recommendation
                )

            db.commit()

            return total

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể xóa recommendation "
                "của project %s.",
                project_id,
            )

            raise


recommendation_service = RecommendationService()