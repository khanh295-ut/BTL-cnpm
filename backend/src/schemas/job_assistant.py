from __future__ import annotations

from decimal import Decimal
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


# ==========================================================
# MILESTONE
# ==========================================================

class JobAssistantMilestone(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
    )

    duration_days: int = Field(
        ...,
        ge=1,
        le=365,
    )

    percentage: Decimal = Field(
        ...,
        ge=0,
        le=100,
    )

    deliverables: list[str] = Field(
        default_factory=list,
    )

    @model_validator(mode="after")
    def normalize_values(self):
        self.title = self.title.strip()

        if self.description is not None:
            self.description = (
                self.description.strip()
            )

        self.deliverables = [
            item.strip()
            for item in self.deliverables
            if item and item.strip()
        ]

        return self


# ==========================================================
# REQUEST
# ==========================================================

class JobAssistantGenerateRequest(BaseModel):
    idea: str = Field(
        ...,
        min_length=10,
        max_length=10000,
        examples=[
            "Tôi muốn xây dựng chatbot AI tư vấn tuyển sinh."
        ],
    )

    category_hint: str | None = Field(
        default=None,
        max_length=255,
    )

    budget_hint: Decimal | None = Field(
        default=None,
        ge=0,
    )

    timeline_hint: int | None = Field(
        default=None,
        ge=1,
        le=365,
    )

    preferred_skills: list[str] = Field(
        default_factory=list,
    )

    language: Literal[
        "vi",
        "en",
    ] = "vi"

    detail_level: Literal[
        "BASIC",
        "STANDARD",
        "DETAILED",
    ] = "STANDARD"

    include_milestones: bool = True

    include_risks: bool = True

    include_acceptance_criteria: bool = True

    @model_validator(mode="after")
    def normalize_values(self):
        self.idea = self.idea.strip()

        if self.category_hint is not None:
            self.category_hint = (
                self.category_hint.strip()
            )

        self.preferred_skills = [
            item.strip()
            for item in self.preferred_skills
            if item and item.strip()
        ]

        self.detail_level = (
            self.detail_level.strip().upper()
        )

        return self


# ==========================================================
# BUDGET
# ==========================================================

class JobAssistantBudgetSuggestion(BaseModel):
    minimum: Decimal = Field(
        ...,
        ge=0,
    )

    recommended: Decimal = Field(
        ...,
        ge=0,
    )

    maximum: Decimal = Field(
        ...,
        ge=0,
    )

    currency: str = Field(
        default="VND",
        min_length=1,
        max_length=10,
    )

    explanation: str | None = Field(
        default=None,
        max_length=2000,
    )

    @model_validator(mode="after")
    def validate_budget(self):
        if not (
            self.minimum
            <= self.recommended
            <= self.maximum
        ):
            raise ValueError(
                "Budget must satisfy: "
                "minimum <= recommended <= maximum."
            )

        self.currency = (
            self.currency.strip().upper()
        )

        if self.explanation is not None:
            self.explanation = (
                self.explanation.strip()
            )

        return self


# ==========================================================
# TIMELINE
# ==========================================================

class JobAssistantTimelineSuggestion(BaseModel):
    minimum_days: int = Field(
        ...,
        ge=1,
        le=365,
    )

    recommended_days: int = Field(
        ...,
        ge=1,
        le=365,
    )

    maximum_days: int = Field(
        ...,
        ge=1,
        le=730,
    )

    explanation: str | None = Field(
        default=None,
        max_length=2000,
    )

    @model_validator(mode="after")
    def validate_timeline(self):
        if not (
            self.minimum_days
            <= self.recommended_days
            <= self.maximum_days
        ):
            raise ValueError(
                "Timeline must satisfy: "
                "minimum_days <= recommended_days <= maximum_days."
            )

        if self.explanation is not None:
            self.explanation = (
                self.explanation.strip()
            )

        return self


# ==========================================================
# RESPONSE
# ==========================================================

class JobAssistantGenerateResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    title: str

    short_description: str | None = None

    description: str

    category: str | None = None

    objectives: list[str] = Field(
        default_factory=list,
    )

    scope_included: list[str] = Field(
        default_factory=list,
    )

    scope_excluded: list[str] = Field(
        default_factory=list,
    )

    required_skills: list[str] = Field(
        default_factory=list,
    )

    recommended_technologies: list[str] = Field(
        default_factory=list,
    )

    budget: JobAssistantBudgetSuggestion

    timeline: JobAssistantTimelineSuggestion

    milestones: list[
        JobAssistantMilestone
    ] = Field(
        default_factory=list,
    )

    acceptance_criteria: list[str] = Field(
        default_factory=list,
    )

    risks: list[str] = Field(
        default_factory=list,
    )

    assumptions: list[str] = Field(
        default_factory=list,
    )

    suggested_questions_for_expert: list[str] = Field(
        default_factory=list,
    )

    generated_by: str = "AI Job Assistant"

    language: str = "vi"


# ==========================================================
# PROJECT CREATE PAYLOAD
#
# Dùng khi frontend muốn chuyển kết quả AI thành ProjectCreate.
# ==========================================================

class JobAssistantProjectPayload(BaseModel):
    title: str

    description: str

    budget: Decimal

    deadline_days: int = Field(
        ...,
        ge=1,
        le=365,
    )

    required_skills: list[str] = Field(
        default_factory=list,
    )

    category: str | None = None


# ==========================================================
# RESPONSE WITH PROJECT PAYLOAD
# ==========================================================

class JobAssistantResult(BaseModel):
    suggestion: JobAssistantGenerateResponse

    project_payload: JobAssistantProjectPayload