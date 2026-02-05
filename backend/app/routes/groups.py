from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import User, Group, GroupMember, Checkin
from app.schemas import GroupCreate, GroupResponse, GroupsListResponse, GroupMembersResponse, GroupMemberResponse, GroupCheckinsResponse, GroupCheckinMember, ResponseModel, APIKeyResponse, GroupTransferRequest, GroupUpdateRequest
from app.auth import get_current_user, api_key_auth
from datetime import date, timedelta
from typing import Optional

router = APIRouter(prefix="/groups", tags=["学习群组"])


@router.post("", response_model=ResponseModel)
async def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建学习群组
    
    需求：
    - 群组名不能为空，长度 ≤ 100
    - 自动将创建者设为群主
    - 支持设置是否要求每日打卡
    """
    # 验证群组名称
    if not group_data.name or len(group_data.name.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="群组名称不能为空"
        )
    
    # 创建群组
    new_group = Group(
        name=group_data.name.strip(),
        description=group_data.description,
        daily_checkin_required=group_data.daily_checkin_required,
        created_by=current_user.id
    )
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    
    # 自动将创建者设为群主
    new_member = GroupMember(
        group_id=new_group.id,
        user_id=current_user.id,
        role="owner",
        last_checkin=None
    )
    db.add(new_member)
    db.commit()
    
    return ResponseModel(
        data={
            "group_id": new_group.id,
            "name": new_group.name,
            "description": new_group.description,
            "daily_checkin_required": new_group.daily_checkin_required,
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
    """
    加入学习群组
    
    流程：
    1. 验证群组存在
    2. 检查是否已在群组中
    3. 添加为新成员
    """
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
        role="member",
        last_checkin=None
    )
    db.add(new_member)
    db.commit()
    
    return ResponseModel(
        data={
            "group_id": group_id,
            "user_id": current_user.id,
            "joined_at": new_member.joined_at,
            "role": "member",
            "group_name": group.name,
            "daily_checkin_required": group.daily_checkin_required
        }
    )


@router.post("/{group_id}/leave", response_model=ResponseModel)
async def leave_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    退出群组
    
    特殊规则：
    - 群主不能直接退出，需要先转让群主或解散群组
    """
    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未加入该群组"
        )
    
    if member.role == "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="群主不能退出群组，请先转让群主或解散群组"
        )
    
    db.delete(member)
    db.commit()
    
    return ResponseModel(data=None)


@router.delete("/{group_id}", response_model=ResponseModel)
async def delete_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    解散群组（仅群主可操作）
    """
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群组不存在"
        )
    
    # 验证操作者是否为群主
    if group.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有群主才能解散群组"
        )
    
    # 删除群组（级联删除所有成员）
    db.delete(group)
    db.commit()
    
    return ResponseModel(data={"message": "群组已成功解散"})


@router.post("/{group_id}/transfer", response_model=ResponseModel)
async def transfer_group_ownership(
    group_id: int,
    transfer_data: GroupTransferRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    转让群主权限（仅群主可操作）
    
    流程：
    1. 验证当前用户是群主
    2. 验证新群主是群组成员
    3. 更新群主身份
    4. 更新群组创建者字段
    """
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群组不存在"
        )
    
    # 验证当前用户是群主
    current_member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id
    ).first()
    
    if not current_member or current_member.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有群主才能转让群主权限"
        )
    
    # 验证新群主用户存在且是群组成员
    new_owner = db.query(User).filter(User.id == transfer_data.new_owner_id).first()
    if not new_owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="新群主用户不存在"
        )
    
    new_owner_member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == transfer_data.new_owner_id
    ).first()
    
    if not new_owner_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="新群主必须是群组成员"
        )
    
    # 更新群主身份
    current_member.role = "member"
    new_owner_member.role = "owner"
    
    # 更新群组创建者字段
    group.created_by = transfer_data.new_owner_id
    
    db.commit()
    
    return ResponseModel(
        data={
            "group_id": group_id,
            "previous_owner_id": current_user.id,
            "new_owner_id": transfer_data.new_owner_id,
            "message": "群主权限转让成功"
        }
    )


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
    """
    获取群组成员列表（仅群组成员可查看）
    """
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群组不存在"
        )
    
    # 验证用户是否是群组成员
    is_member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id
    ).first()
    
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有群组成员才能查看成员列表"
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
            "daily_checkin_required": group.daily_checkin_required,
            "total_members": len(members_data),
            "members": members_data
        }
    )


@router.delete("/{group_id}/members/{user_id}", response_model=ResponseModel)
async def remove_member(
    group_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    移除群组成员（仅群主可操作）
    """
    # 验证群组存在
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群组不存在"
        )
    
    # 验证操作者是群主
    operator_member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id
    ).first()
    
    if not operator_member or operator_member.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有群主才能移除成员"
        )
    
    # 不能移除自己
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能移除自己，请先转让群主权限"
        )
    
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


@router.get("/{group_id}/stats", response_model=ResponseModel)
async def get_group_stats(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取群组统计数据
    
    包含：
    - 群组层面：当前群成员数、今日打卡人数、打卡率
    - 个人层面：最近一次打卡日期、本周打卡天数、平均学习时长
    """
    # 检查群组是否存在
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群组不存在"
        )
    
    # 检查用户是否是群组成员
    is_member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id
    ).first()
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该群组成员"
        )
    
    # 获取群成员信息
    members = db.query(GroupMember, User).join(
        User, GroupMember.user_id == User.id
    ).filter(GroupMember.group_id == group_id).all()
    
    # 计算当前群成员数
    total_members = len(members)
    
    # 计算今日打卡人数
    today = date.today()
    member_ids = [m[0].user_id for m in members]
    today_checkins = db.query(Checkin).filter(
        Checkin.user_id.in_(member_ids),
        Checkin.checkin_date == today
    ).distinct(Checkin.user_id).all()
    today_checked_in_count = len(today_checkins)
    
    # 计算打卡率
    checkin_rate = today_checked_in_count / total_members if total_members > 0 else 0
    
    # 计算本周打卡统计
    week_start = today - timedelta(days=today.weekday())
    week_checkins = db.query(
        Checkin.user_id,
        func.count(Checkin.id).label("checkin_count"),
        func.sum(Checkin.duration_min).label("total_minutes")
    ).filter(
        Checkin.user_id.in_(member_ids),
        Checkin.checkin_date >= week_start,
        Checkin.checkin_date <= today
    ).group_by(Checkin.user_id).all()
    
    # 构建个人统计数据
    personal_stats = []
    for member, user in members:
        # 查找该用户的本周打卡统计
        user_week_stats = next((s for s in week_checkins if s.user_id == user.id), None)
        week_checkin_days = user_week_stats.checkin_count if user_week_stats else 0
        avg_hours = (user_week_stats.total_minutes / 60 / week_checkin_days) if user_week_stats and week_checkin_days > 0 else 0
        
        personal_stats.append({
            "user_id": user.id,
            "username": user.username,
            "role": member.role,
            "last_checkin_date": member.last_checkin,
            "week_checkin_days": week_checkin_days,
            "avg_hours_per_day": round(avg_hours, 2)
        })
    
    # 获取当前用户的个人统计
    current_user_stats = next((s for s in personal_stats if s["user_id"] == current_user.id), None)
    
    return ResponseModel(
        data={
            "group_id": group_id,
            "group_name": group.name,
            "daily_checkin_required": group.daily_checkin_required,
            "total_members": total_members,
            "today_checked_in_count": today_checked_in_count,
            "checkin_rate": round(checkin_rate * 100, 2),
            "personal_stats": personal_stats,
            "my_stats": current_user_stats  # 当前用户的个人统计
        }
    )
