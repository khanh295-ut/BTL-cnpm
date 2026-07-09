from pydantic import BaseModel


class MonthlyStat(BaseModel):
    month: int
    total: int


class RevenueResponse(BaseModel):
    revenue: float


class RatingDistribution(BaseModel):
    rating: int
    total: int