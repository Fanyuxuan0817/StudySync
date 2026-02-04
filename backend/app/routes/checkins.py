from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import User, Plan, Checkin
from app.schemas import CheckinCreate, CheckinResponse, CheckinsListResponse, TodayCheckinResponse, CheckinStatsResponse, DailyStats, ResponseModel
from app.auth import get_current_user
from datetime import date, timedelta
from typing import Optional

router = APIRouter(prefix="/checkins", tags=["打卡记录"])


@router.post("", response_model=ResponseModel)
async def create_checkin(
    checkin_data: CheckinCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    plan = db.query(Plan).filter(
        Plan.id == checkin_data.plan_id,
        Plan.user_id == current_user.id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="计划不存在"
        )
    
    checkin_date = checkin_data.checkin_date or date.today()
    
    existing_checkin = db.query(Checkin).filter(
        Checkin.user_id == current_user.id,
        Checkin.plan_id == checkin_data.plan_id,
        Checkin.checkin_date == checkin_date
    ).first()
    
    if existing_checkin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="今日已打卡该计划"
        )
    
    new_checkin = Checkin(
        user_id=current_user.id,
        plan_id=checkin_data.plan_id,
        checkin_date=checkin_date,
        duration_min=checkin_data.hours,
        content=checkin_data.content
    )
    db.add(new_checkin)
    db.commit()
    db.refresh(new_checkin)
    
    return ResponseModel(
        data={
            "checkin_id": new_checkin.id,
            "user_id": new_checkin.user_id,
            "plan_id": new_checkin.plan_id,
            "hours": new_checkin.duration_min / 60,
            "content": new_checkin.content,
            "date": new_checkin.checkin_date,
            "created_at": new_checkin.created_at
        }
    )


@router.get("", response_model=ResponseModel)
async def get_checkins(
    plan_id: Optional[int] = Query(None),
    date_filter: Optional[date] = Query(None, alias="date"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Checkin).filter(Checkin.user_id == current_user.id)
    
    if plan_id:
        query = query.filter(Checkin.plan_id == plan_id)
    if date_filter:
        query = query.filter(Checkin.checkin_date == date_filter)
    if start_date:
        query = query.filter(Checkin.checkin_date >= start_date)
    if end_date:
        query = query.filter(Checkin.checkin_date <= end_date)
    
    total = query.count()
    items = query.order_by(Checkin.checkin_date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    checkins_data = []
    for checkin in items:
        plan_title = db.query(Plan.title).filter(Plan.id == checkin.plan_id).scalar()
        checkins_data.append({
            "checkin_id": checkin.id,
            "user_id": checkin.user_id,
            "plan_id": checkin.plan_id,
            "plan_title": plan_title,
            "hours": checkin.duration_min / 60,
            "content": checkin.content,
            "date": checkin.checkin_date,
            "created_at": checkin.created_at
        })
    
    return ResponseModel(
        data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": checkins_data
        }
    )


@router.get("/today", response_model=ResponseModel)
async def get_today_checkins(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    today = date.today()
    
    checkins = db.query(Checkin, Plan.title).join(
        Plan, Checkin.plan_id == Plan.id
    ).filter(
        Checkin.user_id == current_user.id,
        Checkin.checkin_date == today
    ).all()
    
    checkins_data = []
    total_hours = 0
    for checkin, plan_title in checkins:
        hours = checkin.duration_min / 60
        total_hours += hours
        checkins_data.append({
            "checkin_id": checkin.id,
            "plan_id": checkin.plan_id,
            "plan_title": plan_title,
            "hours": hours,
            "content": checkin.content,
            "created_at": checkin.created_at
        })
    
    return ResponseModel(
        data={
            "date": today,
            "checked_in": len(checkins_data) > 0,
            "total_hours": total_hours,
            "checkins": checkins_data
        }
    )


@router.get("/stats", response_model=ResponseModel)
async def get_checkin_stats(
    period: str = Query("week", regex="^(week|month|year)$"),
    plan_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    today = date.today()
    
    if period == "week":
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif period == "month":
        start_date = today.replace(day=1)
        end_date = today
    else:
        start_date = today.replace(month=1, day=1)
        end_date = today
    
    query = db.query(Checkin).filter(
        Checkin.user_id == current_user.id,
        Checkin.checkin_date >= start_date,
        Checkin.checkin_date <= end_date
    )
    
    if plan_id:
        query = query.filter(Checkin.plan_id == plan_id)
    
    checkins = query.all()
    
    total_hours = sum(c.duration_min for c in checkins) / 60
    checkin_count = len(checkins)
    
    unique_dates = len(set(c.checkin_date for c in checkins))
    total_days = (end_date - start_date).days + 1
    checkin_rate = (unique_dates / total_days) * 100 if total_days > 0 else 0
    avg_hours_per_day = total_hours / total_days if total_days > 0 else 0
    
    daily_stats_query = db.query(
        Checkin.checkin_date,
        func.sum(Checkin.duration_min).label("hours"),
        func.count(Checkin.id).label("checkin_count")
    ).filter(
        Checkin.user_id == current_user.id,
        Checkin.checkin_date >= start_date,
        Checkin.checkin_date <= end_date
    ).group_by(Checkin.checkin_date).all()
    
    daily_stats = [
        DailyStats(
            date=d.checkin_date,
            hours=d.hours / 60,
            checkin_count=d.checkin_count
        )
        for d in daily_stats_query
    ]
    
    return ResponseModel(
        data={
            "period": period,
            "total_hours": total_hours,
            "total_days": total_days,
            "checkin_count": checkin_count,
            "avg_hours_per_day": avg_hours_per_day,
            "checkin_rate": round(checkin_rate, 2),
            "daily_stats": daily_stats
        }
    )


@router.put("/{checkin_id}", response_model=ResponseModel)
async def update_checkin(
    checkin_id: int,
    checkin_data: CheckinCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 查找打卡记录
    checkin = db.query(Checkin).filter(
        Checkin.id == checkin_id,
        Checkin.user_id == current_user.id
    ).first()
    
    if not checkin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="打卡记录不存在"
        )
    
    # 验证计划是否存在且属于当前用户
    plan = db.query(Plan).filter(
        Plan.id == checkin_data.plan_id,
        Plan.user_id == current_user.id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="计划不存在"
        )
    
    checkin_date = checkin_data.checkin_date or date.today()
    
    # 检查是否与其他打卡记录冲突
    existing_checkin = db.query(Checkin).filter(
        Checkin.user_id == current_user.id,
        Checkin.plan_id == checkin_data.plan_id,
        Checkin.checkin_date == checkin_date,
        Checkin.id != checkin_id
    ).first()
    
    if existing_checkin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该日期已打卡该计划"
        )
    
    # 更新打卡记录
    checkin.plan_id = checkin_data.plan_id
    checkin.checkin_date = checkin_date
    checkin.duration_min = checkin_data.hours
    checkin.content = checkin_data.content
    
    db.commit()
    db.refresh(checkin)
    
    return ResponseModel(
        data={
            "checkin_id": checkin.id,
            "user_id": checkin.user_id,
            "plan_id": checkin.plan_id,
            "hours": checkin.duration_min / 60,
            "content": checkin.content,
            "date": checkin.checkin_date,
            "created_at": checkin.created_at
        }
    )


@router.delete("/{checkin_id}", response_model=ResponseModel)
async def delete_checkin(
    checkin_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 查找打卡记录
    checkin = db.query(Checkin).filter(
        Checkin.id == checkin_id,
        Checkin.user_id == current_user.id
    ).first()
    
    if not checkin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="打卡记录不存在"
        )
    
    # 删除打卡记录
    db.delete(checkin)
    db.commit()
    
    return ResponseModel(
        data={"message": "打卡记录删除成功"}
    )
