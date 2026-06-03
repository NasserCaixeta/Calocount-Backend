from google.genai.errors import ClientError, ServerError

from fastapi import APIRouter, HTTPException, UploadFile, File, status

from app.core.deps import CurrentUser
from app.schemas.ai import MealAnalysisResult
from app.tasks.ai_tasks import analyze_meal_photo

router = APIRouter(prefix="/ai", tags=["ai"])

_ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"}
_MAX_SIZE_BYTES = 10 * 1024 * 1024


@router.post("/analyze", response_model=MealAnalysisResult)
async def analyze_meal(
    current_user: CurrentUser,
    file: UploadFile = File(..., description="Foto da refeição (JPEG, PNG ou WEBP, máx 10MB)"),
) -> MealAnalysisResult:
    if file.content_type not in _ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Tipo de arquivo não suportado: {file.content_type}. Use JPEG, PNG ou WEBP.",
        )

    image_bytes = await file.read()

    if len(image_bytes) > _MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Imagem muito grande. Tamanho máximo: 10MB.",
        )

    try:
        result = analyze_meal_photo.delay(image_bytes, file.content_type).get()
    except ClientError as exc:
        if exc.code == 429:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Cota da API Gemini esgotada. Tente novamente em alguns instantes.",
            )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erro na API Gemini: {exc}",
        )
    except ServerError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API Gemini temporariamente indisponível. Tente novamente em alguns segundos.",
        )

    return MealAnalysisResult(**result)
