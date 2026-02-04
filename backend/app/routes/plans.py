from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import User, Plan, Checkin
from app.schemas import PlanCreate, PlanUpdate, PlanResponse, PlansListResponse, ResponseModel
from app.auth import get_current_user
from typing import Optional

router = APIRouter(prefix="/plans", tags=["学习计划"])


@router.post("", response_model=ResponseModel)
async def create_plan(
    plan_data: PlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_plan = Plan(
        user_id=current_user.id,
        title=plan_data.title,
        description=plan_data.description,
        daily_goal_min=plan_data.daily_goal_hours,
        start_date=plan_data.start_date,
        end_date=plan_data.end_date
    )
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    
    return ResponseModel(
        data={
            "plan_id": new_plan.id,
            "user_id": new_plan.user_id,
            "title": new_plan.title,
            "description": new_plan.description,
            "daily_goal_hours": new_plan.daily_goal_min / 60,
            "start_date": new_plan.start_date,
            "end_date": new_plan.end_date,
            "status": "active",
            "created_at": new_plan.created_at
        }
    )


@router.get("", response_model=ResponseModel)
async def get_plans(
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Plan).filter(Plan.user_id == current_user.id)
    
    if status_filter:
        query = query.filter(Plan.end_date >= func.current_date() if status_filter == "active" else False)
    
    total = query.count()
    items = query.order_by(Plan.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    plans_data = []
    for plan in items:
        total_hours = db.query(func.sum(Checkin.duration_min)).filter(
            Checkin.plan_id == plan.id
        ).scalar() or 0
        
        plans_data.append({
            "plan_id": plan.id,
            "title": plan.title,
            "description": plan.description,
            "daily_goal_hours": plan.daily_goal_min / 60,
            "start_date": plan.start_date,
            "end_date": plan.end_date,
            "status": "active",
            "created_at": plan.created_at,
            "progress": {
                "total_hours": total_hours / 60,
                "completion_rate": min(100, (total_hours / (plan.daily_goal_min * 1)) * 100)
            }
        })
    
    return ResponseModel(
        data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": plans_data
        }
    )


@router.put("/{plan_id}", response_model=ResponseModel)
async def update_plan(
    plan_id: int,
    plan_data: PlanUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    plan = db.query(Plan).filter(
        Plan.id == plan_id,
        Plan.user_id == current_user.id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="计划不存在"
        )
    
    if plan_data.title is not None:
        plan.title = plan_data.title
    if plan_data.description is not None:
        plan.description = plan_data.description
    if plan_data.daily_goal_hours is not None:
        plan.daily_goal_min = plan_data.daily_goal_hours
    if plan_data.end_date is not None:
        plan.end_date = plan_data.end_date
    
    db.commit()
    db.refresh(plan)
    
    return ResponseModel(
        data={
            "plan_id": plan.id,
            "title": plan.title,
            "description": plan.description,
            "daily_goal_hours": plan.daily_goal_min / 60,
            "start_date": plan.start_date,
            "end_date": plan.end_date,
            "status": "active",
            "updated_at": plan.updated_at
        }
    )


@router.delete("/{plan_id}", response_model=ResponseModel)
async def delete_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    plan = db.query(Plan).filter(
        Plan.id == plan_id,
        Plan.user_id == current_user.id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="计划不存在"
        )
    
    db.delete(plan)
    db.commit()
    
    return ResponseModel(data=None)
