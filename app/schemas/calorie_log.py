from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, Field


class CalorieLogCreate(BaseModel):
    meal_name: str = Field(..., min_length=1, max_length=200)
    calories: float = Field(..., gt=0)
    log_date: date
    notes: Optional[str] = None


class CalorieLogOut(BaseModel):
    id: int
    user_id: int
    meal_name: str
    calories: float
    log_date: date
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class DailySummary(BaseModel):
    log_date: date
    total_calories: float
    meal_count: int
