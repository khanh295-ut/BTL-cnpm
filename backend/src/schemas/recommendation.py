from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


# ==========================================================
# SCORE BREAKDOWN
# ==========================================================

class RecommendationScoreBreakdown(BaseModel):
    skill_score: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        le=100,
    )

    rating_score: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        le=100,
    )

    experience_score: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        le=100,
    )

    price_score: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        le=100,
    )


# ==========================================================
# BASE
# ==========================================================

class RecommendationBase(BaseModel):
    project_id: UUID

    expert_id: UUID

    match_score: Decimal = Field(
        ...,
        ge=0,
        le=100,
    )

    skill_score: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        le=100,
    )

    rating_score: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        le=100,
    )

    experience_score: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        le=100,
    )

    price_score: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        le=100,
    )

    matched_skills: list[str] = Field(
        default_factory=list,
    )

    missing_skills: list[str] = Field(
        default_factory=list,
    )

    reason: Optional[str] = Field(
        default=None,
        max_length=5000,
    )

    recommendation_level: str = Field(
        default="MEDIUM",
        min_length=1,
        max_length=30,
    )

    algorithm_version: str = Field(
        default="v1.0",
        min_length=1,
        max_length=50,
    )

    @model_validator(mode="after")
    def normalize_values(self):
        self.recommendation_level = (
            self.recommendation_level
            .strip()
            .upper()
        )

        allowed_levels = {
            "LOW",
            "MEDIUM",
            "HIGH",
            "VERY_HIGH",
        }

        if self.recommendation_level not in allowed_levels:
            raise ValueError(
                "Invalid recommendation level."
            )

        self.algorithm_version = (
            self.algorithm_version.strip()
        )

        self.matched_skills = [
            skill.strip()
            for skill in self.matched_skills
            if skill and skill.strip()
        ]

        self.missing_skills = [
            skill.strip()
            for skill in self.missing_skills
            if skill and skill.strip()
        ]

        return self


# ==========================================================
# CREATE
# Dùng khi service đã tính xong điểm và muốn lưu kết quả.
# ==========================================================

class RecommendationCreate(RecommendationBase):
    pass


# ==========================================================
# UPDATE
# ==========================================================

class RecommendationUpdate(BaseModel):
    match_score: Optional[Decimal] = Field(
        default=None,
        ge=0,
        le=100,
    )

    skill_score: Optional[Decimal] = Field(
        default=None,
        ge=0,
        le=100,
    )

    rating_score: Optional[Decimal] = Field(
        default=None,
        ge=0,
        le=100,
    )

    experience_score: Optional[Decimal] = Field(
        default=None,
        ge=0,
        le=100,
    )

    price_score: Optional[Decimal] = Field(
        default=None,
        ge=0,
        le=100,
    )

    matched_skills: Optional[list[str]] = None

    missing_skills: Optional[list[str]] = None

    reason: Optional[str] = Field(
        default=None,
        max_length=5000,
    )

    recommendation_level: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=30,
    )

    algorithm_version: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    @model_validator(mode="after")
    def normalize_values(self):
        if self.recommendation_level is not None:
            normalized_level = (
                self.recommendation_level
                .strip()
                .upper()
            )

            allowed_levels = {
                "LOW",
                "MEDIUM",
                "HIGH",
                "VERY_HIGH",
            }

            if normalized_level not in allowed_levels:
                raise ValueError(
                    "Invalid recommendation level."
                )

            self.recommendation_level = normalized_level

        if self.algorithm_version is not None:
            self.algorithm_version = (
                self.algorithm_version.strip()
            )

        if self.matched_skills is not None:
            self.matched_skills = [
                skill.strip()
                for skill in self.matched_skills
                if skill and skill.strip()
            ]

        if self.missing_skills is not None:
            self.missing_skills = [
                skill.strip()
                for skill in self.missing_skills
                if skill and skill.strip()
            ]

        return self


# ==========================================================
# GENERATE REQUEST
# Gọi service để tính recommendation cho một project.
# ==========================================================

class RecommendationGenerateRequest(BaseModel):
    project_id: UUID

    limit: int = Field(
        default=10,
        ge=1,
        le=100,
    )

    force_refresh: bool = False

    algorithm_version: str = Field(
        default="v1.0",
        min_length=1,
        max_length=50,
    )


# ==========================================================
# FEEDBACK
# ==========================================================

class RecommendationFeedbackUpdate(BaseModel):
    was_viewed: Optional[bool] = None

    was_selected: Optional[bool] = None

    feedback: Optional[str] = Field(
        default=None,
        max_length=5000,
    )


# ==========================================================
# RESPONSE
# ==========================================================

class RecommendationResponse(RecommendationBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    was_viewed: str

    was_selected: str

    feedback: Optional[str] = None

    created_at: datetime

    updated_at: datetime


# ==========================================================
# EXPERT SUMMARY RESPONSE
# Dùng cho frontend hiển thị danh sách đề xuất.
# ==========================================================

class RecommendedExpertResponse(BaseModel):
    recommendation_id: UUID

    expert_id: UUID

    expert_name: str

    expert_title: Optional[str] = None

    hourly_rate: Decimal

    location: Optional[str] = None

    match_score: Decimal

    recommendation_level: str

    matched_skills: list[str] = Field(
        default_factory=list,
    )

    missing_skills: list[str] = Field(
        default_factory=list,
    )

    reason: Optional[str] = None

    score_breakdown: RecommendationScoreBreakdown


# ==========================================================
# GENERATE RESPONSE
# ==========================================================

class RecommendationGenerateResponse(BaseModel):
    project_id: UUID

    total_candidates: int

    algorithm_version: str

    generated_at: datetime

    recommendations: list[
        RecommendedExpertResponse
    ] = Field(
        default_factory=list,
    )