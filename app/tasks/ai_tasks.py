import json
import re

from google import genai
from google.genai import types

from app.config import settings
from app.tasks.celery_app import celery_app

_client = genai.Client(api_key=settings.GEMINI_API_KEY)

_ANALYSIS_PROMPT = """
Você é um nutricionista especialista em análise de alimentos.
Analise a imagem desta refeição e responda SOMENTE com um JSON válido, sem markdown, sem explicações extras.

Formato obrigatório:
{
  "meal_name": "nome da refeição identificada",
  "estimated_calories": 000,
  "portions": "descrição das porções estimadas",
  "ingredients": ["ingrediente 1", "ingrediente 2"],
  "macros": {
    "protein_g": 0,
    "carbs_g": 0,
    "fat_g": 0
  },
  "confidence": "alta|media|baixa",
  "notes": "observações adicionais se houver"
}
""".strip()


@celery_app.task(name="ai_tasks.analyze_meal_photo")
def analyze_meal_photo(image_bytes: bytes, mime_type: str) -> dict:
    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

    response = _client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[_ANALYSIS_PROMPT, image_part],
    )
    raw_text = response.text.strip()

    json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if not json_match:
        return {
            "meal_name": "Não identificado",
            "estimated_calories": 0,
            "portions": "",
            "ingredients": [],
            "macros": {"protein_g": 0, "carbs_g": 0, "fat_g": 0},
            "confidence": "baixa",
            "notes": raw_text,
        }

    return json.loads(json_match.group())
