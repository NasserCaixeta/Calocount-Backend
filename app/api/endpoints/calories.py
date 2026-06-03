from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser
from app.db.session import get_db
from app.models.calorie_log import CalorieLog
from app.schemas.calorie_log import CalorieLogCreate, CalorieLogOut, DailySummary

router = APIRouter(prefix="/calories", tags=["calories"])


@router.post("/", response_model=CalorieLogOut, status_code=status.HTTP_201_CREATED)
def create_log(
    payload: CalorieLogCreate,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> CalorieLog:
    log = CalorieLog(
        user_id=current_user.id,
        meal_name=payload.meal_name,
        calories=payload.calories,
        protein_g=payload.protein_g,
        carbs_g=payload.carbs_g,
        fat_g=payload.fat_g,
        via=payload.via,
        log_date=payload.log_date,
        notes=payload.notes,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/summary", response_model=list[DailySummary])
def get_summary(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
) -> list[DailySummary]:
    query = db.query(
        CalorieLog.log_date,
        func.sum(CalorieLog.calories).label("total_calories"),
        func.count(CalorieLog.id).label("meal_count"),
    ).filter(CalorieLog.user_id == current_user.id)

    if start_date:
        query = query.filter(CalorieLog.log_date >= start_date)
    if end_date:
        query = query.filter(CalorieLog.log_date <= end_date)

    rows = query.group_by(CalorieLog.log_date).order_by(CalorieLog.log_date).all()

    return [
        DailySummary(log_date=row.log_date, total_calories=row.total_calories, meal_count=row.meal_count)
        for row in rows
    ]


@router.get("/", response_model=list[CalorieLogOut])
def list_logs(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    log_date: Optional[date] = Query(None),
) -> list[CalorieLog]:
    query = db.query(CalorieLog).filter(CalorieLog.user_id == current_user.id)

    if log_date:
        query = query.filter(CalorieLog.log_date == log_date)

    return query.order_by(CalorieLog.log_date.desc(), CalorieLog.created_at.desc()).all()


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_log(
    log_id: int,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    log = db.query(CalorieLog).filter(
        CalorieLog.id == log_id,
        CalorieLog.user_id == current_user.id,
    ).first()

    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro não encontrado.")

    db.delete(log)
    db.commit()
