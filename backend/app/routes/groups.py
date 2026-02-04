from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import User, Group, GroupMember
from app.schemas import GroupCreate, GroupResponse, GroupsListResponse, GroupMembersResponse, GroupMemberResponse, GroupCheckinsResponse, GroupCheckinMember, ResponseModel, APIKeyResponse
from app.auth import get_current_user, api_key_auth
from datetime import date

router = APIRouter(prefix="/groups", tags=["学习群组"])


@router.post("", response_model=ResponseModel)
async def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_group = Group(
        name=group_data.name,
        description=group_data.description,
        daily_checkin_required=group_data.daily_checkin_rule.get("min_checkins_per_day", 1) > 0,
        created_by=current_user.id
    )
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    
    new_member = GroupMember(
        group_id=new_group.id,
        user_id=current_user.id,
        role="owner"
    )
    db.add(new_member)
    db.commit()
    
    return ResponseModel(
        data={
            "group_id": new_group.id,
            "name": new_group.name,
            "description": new_group.description,
            "creator_id": new_group.created_by,
            "member_count": 1,
            "created_at": new_group.created_at
        }
    )


@router.post("/{group_id}/join", response_model=ResponseModel)
async def join_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    group = db.query(Group).filter(Group.id == group_id).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群组不存在"
        )
    
    existing_member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id
    ).first()
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="已在群组中"
        )
    
    new_member = GroupMember(
        group_id=group_id,
        user_id=current_user.id,
        role="member"
    )
    db.add(new_member)
    db.commit()
    
    return ResponseModel(
        data={
            "group_id": group_id,
            "user_id": current_user.id,
            "joined_at": new_member.joined_at,
            "role": "member"
        }
    )


@router.post("/{group_id}/leave", response_model=ResponseModel)
async def leave_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未加入该群组"
        )
    
    group = db.query(Group).filter(Group.id == group_id).first()
    if group and group.created_by == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="群主不能退出群组"
        )
    
    db.delete(member)
    db.commit()
    
    return ResponseModel(data=None)


@router.get("", response_model=ResponseModel)
async def get_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    created_groups = db.query(Group).filter(Group.created_by == current_user.id).all()
    joined_group_ids = db.query(GroupMember.group_id).filter(
        GroupMember.user_id == current_user.id
    ).all()
    joined_groups = db.query(Group).filter(Group.id.in_([g[0] for g in joined_group_ids])).all()
    
    created_data = []
    for group in created_groups:
        member_count = db.query(GroupMember).filter(GroupMember.group_id == group.id).count()
        created_data.append({
            "group_id": group.id,
            "name": group.name,
            "description": group.description,
            "member_count": member_count,
            "created_at": group.created_at
        })
    
    joined_data = []
    for group in joined_groups:
        member_count = db.query(GroupMember).filter(GroupMember.group_id == group.id).count()
        joined_member = db.query(GroupMember).filter(
            GroupMember.group_id == group.id,
            GroupMember.user_id == current_user.id
        ).first()
        joined_data.append({
            "group_id": group.id,
            "name": group.name,
            "description": group.description,
            "member_count": member_count,
            "joined_at": joined_member.joined_at if joined_member else None
        })
    
    return ResponseModel(
        data={
            "created": created_data,
            "joined": joined_data
        }
    )


@router.get("/{group_id}/members", response_model=ResponseModel)
async def get_group_members(
    group_id: int,
    status: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群组不存在"
        )
    
    members_query = db.query(GroupMember, User).join(
        User, GroupMember.user_id == User.id
    ).filter(GroupMember.group_id == group_id)
    
    members = members_query.all()
    
    members_data = []
    for member, user in members:
        days_without_checkin = 0
        if member.last_checkin:
            days_without_checkin = (date.today() - member.last_checkin).days
        
        members_data.append({
            "user_id": user.id,
            "username": user.username,
            "avatar_url": user.avatar_url,
            "role": member.role,
            "joined_at": member.joined_at,
            "last_checkin_date": member.last_checkin,
            "days_without_checkin": days_without_checkin
        })
    
    return ResponseModel(
        data={
            "group_id": group_id,
            "name": group.name,
            "total_members": len(members_data),
            "members": members_data
        }
    )


@router.delete("/{group_id}/members/{user_id}", response_model=ResponseModel)
async def remove_member(
    group_id: int,
    user_id: int,
    api_key_obj = Depends(api_key_auth),
    db: Session = Depends(get_db)
):
    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="成员不存在"
        )
    
    db.delete(member)
    db.commit()
    
    return ResponseModel(
        data={
            "group_id": group_id,
            "user_id": user_id,
            "removed_at": db.execute(func.now()).scalar()
        }
    )


@router.get("/{group_id}/checkins", response_model=ResponseModel)
async def get_group_checkins(
    group_id: int,
    date_filter: date = Query(None, alias="date"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.models import Checkin, Plan
    from sqlalchemy import func
    
    target_date = date_filter or date.today()
    
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群组不存在"
        )
    
    members = db.query(GroupMember).filter(GroupMember.group_id == group_id).all()
    member_ids = [m.user_id for m in members]
    
    checkins = db.query(Checkin, User, Plan).join(
        User, Checkin.user_id == User.id
    ).join(
        Plan, Checkin.plan_id == Plan.id
    ).filter(
        Checkin.user_id.in_(member_ids),
        Checkin.checkin_date == target_date
    ).all()
    
    checked_in_ids = set()
    checked_in_data = []
    for checkin, user, plan in checkins:
        checked_in_ids.add(user.id)
        checked_in_data.append({
            "user_id": user.id,
            "username": user.username,
            "hours": checkin.duration_min / 60,
            "checkin_time": checkin.created_at
        })
    
    not_checked_in_data = []
    for member in members:
        user = db.query(User).filter(User.id == member.user_id).first()
        if user and user.id not in checked_in_ids:
            not_checked_in_data.append({
                "user_id": user.id,
                "username": user.username
            })
    
    return ResponseModel(
        data={
            "group_id": group_id,
            "date": target_date,
            "total_members": len(members),
            "checked_in_count": len(checked_in_data),
            "not_checked_in_count": len(not_checked_in_data),
            "checked_in": checked_in_data,
            "not_checked_in": not_checked_in_data
        }
    )
