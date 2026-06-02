from typing import Optional
from pydantic import BaseModel


class Macros(BaseModel):
    protein_g: float
    carbs_g: float
    fat_g: float


class MealAnalysisResult(BaseModel):
    meal_name: str
    estimated_calories: float
    portions: Optional[str] = None
    ingredients: list[str] = []
    macros: Optional[Macros] = None
    confidence: str
    notes: Optional[str] = None
