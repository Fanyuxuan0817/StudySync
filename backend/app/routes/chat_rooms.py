from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.database import get_db
from app.models import User, Group
from app.chat_models import ChatRoom, ChatRoomMember, ChatRoomJoinRequest, ChatRoomStatus, ChatRoomJoinStatus
from app.chat_schemas import (
    ChatRoomCreate, ChatRoomUpdate, ChatRoomResponse, ChatRoomSearchResponse,
    ChatRoomJoinRequestCreate, ChatRoomJoinRequestResponse, ChatRoomJoinRequestReview,
    ChatRoomMembersResponse, ChatRoomMemberResponse, ChatIdSearchRequest, ChatRoomBriefResponse
)
from app.chat_id_generator import ChatIdGenerator
from app.auth import get_current_user
from typing import Optional, List

router = APIRouter(prefix="/chat-rooms", tags=["群聊"])


@router.post("")
async def create_chat_room(
    chat_room_data: ChatRoomCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建群聊房间
    
    功能：
    1. 自动生成唯一群聊ID
    2. 可关联现有学习群组
    3. 创建者自动成为群主
    """
    # 验证群聊名称
    if not chat_room_data.name or len(chat_room_data.name.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="群聊名称不能为空"
        )
    
    # 如果关联了学习群组，验证群组存在且用户是成员
    if chat_room_data.group_id:
        group = db.query(Group).filter(Group.id == chat_room_data.group_id).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="关联的学习群组不存在"
            )
        
        # 检查用户是否是群组成员
        from app.models import GroupMember
        is_group_member = db.query(GroupMember).filter(
            GroupMember.group_id == chat_room_data.group_id,
            GroupMember.user_id == current_user.id
        ).first()
        
        if not is_group_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有学习群组成员才能创建关联的群聊"
            )
    
    # 生成唯一群聊ID
    chat_id = ChatIdGenerator.generate_unique(db)
    if not chat_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="无法生成唯一群聊ID，请稍后重试"
        )
    
    # 创建群聊
    new_chat_room = ChatRoom(
        chat_id=chat_id,
        name=chat_room_data.name.strip(),
        description=chat_room_data.description,
        avatar_url=chat_room_data.avatar_url,
        group_id=chat_room_data.group_id,
        created_by=current_user.id,
        max_members=chat_room_data.max_members,
        is_public=chat_room_data.is_public
    )
    db.add(new_chat_room)
    db.commit()
    db.refresh(new_chat_room)
    
    # 创建群主成员记录
    owner_member = ChatRoomMember(
        chat_room_id=new_chat_room.id,
        user_id=current_user.id,
        role="owner",
        last_active_at=func.now()
    )
    db.add(owner_member)
    db.commit()
    
    from app.schemas import ResponseModel
    
    return ResponseModel(
        data=ChatRoomResponse(
            chat_room_id=new_chat_room.id,
            chat_id=new_chat_room.chat_id,
            name=new_chat_room.name,
            description=new_chat_room.description,
            avatar_url=new_chat_room.avatar_url,
            group_id=new_chat_room.group_id,
            creator_id=new_chat_room.created_by,
            max_members=new_chat_room.max_members,
            current_members=1,
            is_public=new_chat_room.is_public,
            status=new_chat_room.status,
            created_at=new_chat_room.created_at
        ).model_dump()
    )


@router.get("/my-rooms")
async def get_my_chat_rooms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取我的群聊列表

    返回：
    - created: 我创建的群聊
    - joined: 我加入的群聊
    """
    # 获取用户创建的所有群聊
    created_rooms = db.query(ChatRoom).filter(
        ChatRoom.created_by == current_user.id,
        ChatRoom.status == ChatRoomStatus.ACTIVE
    ).all()

    # 获取用户加入的群聊（通过ChatRoomMember表）
    joined_member_records = db.query(ChatRoomMember).filter(
        ChatRoomMember.user_id == current_user.id
    ).all()

    joined_room_ids = [m.chat_room_id for m in joined_member_records]

    # 获取加入的群聊详情（排除自己创建的）
    joined_rooms = db.query(ChatRoom).filter(
        ChatRoom.id.in_(joined_room_ids),
        ChatRoom.created_by != current_user.id,
        ChatRoom.status == ChatRoomStatus.ACTIVE
    ).all()

    # 构建返回数据
    created_data = []
    for room in created_rooms:
        # 获取成员数
        member_count = db.query(func.count(ChatRoomMember.id)).filter(
            ChatRoomMember.chat_room_id == room.id
        ).scalar() or 0

        created_data.append({
            "room_id": room.id,
            "chat_id": room.chat_id,
            "name": room.name,
            "description": room.description,
            "avatar_url": room.avatar_url,
            "member_count": member_count,
            "max_members": room.max_members,
            "is_public": room.is_public,
            "created_at": room.created_at
        })

    joined_data = []
    for room in joined_rooms:
        # 获取成员数
        member_count = db.query(func.count(ChatRoomMember.id)).filter(
            ChatRoomMember.chat_room_id == room.id
        ).scalar() or 0

        joined_data.append({
            "room_id": room.id,
            "chat_id": room.chat_id,
            "name": room.name,
            "description": room.description,
            "avatar_url": room.avatar_url,
            "member_count": member_count,
            "max_members": room.max_members,
            "is_public": room.is_public,
            "created_at": room.created_at
        })

    from app.schemas import ResponseModel
    return ResponseModel(
        data={
            "created": created_data,
            "joined": joined_data
        }
    )


@router.get("/join-requests/pending")
async def get_pending_join_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户作为群主/管理员的所有待处理入群申请
    """
    # 获取用户管理的所有群聊（群主或管理员）
    managed_members = db.query(ChatRoomMember).filter(
        ChatRoomMember.user_id == current_user.id,
        ChatRoomMember.role.in_(["owner", "admin"])
    ).all()

    managed_room_ids = [m.chat_room_id for m in managed_members]

    if not managed_room_ids:
        from app.schemas import ResponseModel
        return ResponseModel(data={"approvals": []})

    # 查询这些群聊的待处理申请
    pending_requests = db.query(ChatRoomJoinRequest, User, ChatRoom).join(
        User, ChatRoomJoinRequest.user_id == User.id
    ).join(
        ChatRoom, ChatRoomJoinRequest.chat_room_id == ChatRoom.id
    ).filter(
        ChatRoomJoinRequest.chat_room_id.in_(managed_room_ids),
        ChatRoomJoinRequest.status == ChatRoomJoinStatus.PENDING
    ).order_by(ChatRoomJoinRequest.created_at.desc()).all()

    approvals_data = []
    for request, user, chat_room in pending_requests:
        approvals_data.append({
            "approval_id": request.id,
            "request_id": request.id,
            "chat_room_id": request.chat_room_id,
            "room_id": request.chat_room_id,
            "chat_id": chat_room.chat_id,
            "room_name": chat_room.name,
            "user_id": request.user_id,
            "user_name": user.username,
            "username": user.username,
            "message": request.message,
            "created_at": request.created_at
        })

    from app.schemas import ResponseModel
    return ResponseModel(data={"approvals": approvals_data})


@router.get("/search")
async def search_chat_rooms(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    chat_id: Optional[str] = Query(None, description="群聊ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    搜索群聊
    
    支持：
    1. 按群聊ID精确搜索
    2. 按名称模糊搜索
    3. 只显示公开群聊或已加入的群聊
    """
    query = db.query(ChatRoom).filter(ChatRoom.status == ChatRoomStatus.ACTIVE)
    
    # 如果提供了群聊ID，进行精确匹配
    if chat_id:
        if not ChatIdGenerator.is_valid(chat_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="群聊ID格式无效"
            )
        query = query.filter(ChatRoom.chat_id == chat_id.upper())
    
    # 如果提供了关键词，进行模糊搜索
    if keyword:
        query = query.filter(
            or_(
                ChatRoom.name.contains(keyword.strip()),
                ChatRoom.description.contains(keyword.strip())
            )
        )
    
    # 只显示公开群聊或用户已加入的群聊
    user_chat_ids = db.query(ChatRoomMember.chat_room_id).filter(
        ChatRoomMember.user_id == current_user.id
    ).subquery()
    
    query = query.filter(
        or_(
            ChatRoom.is_public == True,
            ChatRoom.id.in_(user_chat_ids)
        )
    )
    
    # 统计总数
    total = query.count()
    
    # 分页
    offset = (page - 1) * page_size
    chat_rooms = query.offset(offset).limit(page_size).all()
    
    # 批量获取成员数
    chat_room_ids = [room.id for room in chat_rooms]
    member_counts = db.query(
        ChatRoomMember.chat_room_id,
        func.count(ChatRoomMember.id).label('count')
    ).filter(
        ChatRoomMember.chat_room_id.in_(chat_room_ids)
    ).group_by(
        ChatRoomMember.chat_room_id
    ).all()
    
    # 构建成员数映射
    member_count_map = {item.chat_room_id: item.count for item in member_counts}
    
    # 构建响应数据
    chat_rooms_data = []
    for room in chat_rooms:
        current_members = member_count_map.get(room.id, 0)
        
        chat_rooms_data.append(ChatRoomResponse(
            chat_room_id=room.id,
            chat_id=room.chat_id,
            name=room.name,
            description=room.description,
            avatar_url=room.avatar_url,
            group_id=room.group_id,
            creator_id=room.created_by,
            max_members=room.max_members,
            current_members=current_members,
            is_public=room.is_public,
            status=room.status,
            created_at=room.created_at
        ))
    
    from app.schemas import ResponseModel
    return ResponseModel(
        data=ChatRoomSearchResponse(
            chat_rooms=chat_rooms_data,
            total=total,
            page=page,
            page_size=page_size
        ).model_dump()
    )


@router.get("/search-by-id")
async def search_chat_room_by_id(
    chat_id: str = Query(..., min_length=6, max_length=20, description="群聊ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    通过群聊ID搜索群聊（精确匹配）
    
    用于加入群聊时的快速搜索
    """
    # 验证群聊ID格式
    if not ChatIdGenerator.is_valid(chat_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="群聊ID格式无效"
        )
    
    # 搜索群聊
    chat_room = db.query(ChatRoom).filter(
        ChatRoom.chat_id == chat_id.upper(),
        ChatRoom.status == ChatRoomStatus.ACTIVE
    ).first()
    
    if not chat_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群聊不存在"
        )
    
    # 检查是否是公开群聊或用户已加入
    is_member = db.query(ChatRoomMember).filter(
        ChatRoomMember.chat_room_id == chat_room.id,
        ChatRoomMember.user_id == current_user.id
    ).first()
    
    if not chat_room.is_public and not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="该群聊不对外开放"
        )
    
    # 获取当前成员数
    current_members = db.query(ChatRoomMember).filter(
        ChatRoomMember.chat_room_id == chat_room.id
    ).count()
    
    from app.schemas import ResponseModel
    return ResponseModel(
        data=ChatRoomBriefResponse(
            chat_room_id=chat_room.id,
            chat_id=chat_room.chat_id,
            name=chat_room.name,
            description=chat_room.description,
            avatar_url=chat_room.avatar_url,
            current_members=current_members,
            max_members=chat_room.max_members,
            is_public=chat_room.is_public
        ).model_dump()
    )


@router.get("/{chat_room_id}")
async def get_chat_room(
    chat_room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取群聊详情
    """
    # 验证群聊存在
    chat_room = db.query(ChatRoom).filter(
        ChatRoom.id == chat_room_id,
        ChatRoom.status == ChatRoomStatus.ACTIVE
    ).first()
    
    if not chat_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群聊不存在或已关闭"
        )
    
    # 检查是否是公开群聊或用户已加入
    is_member = db.query(ChatRoomMember).filter(
        ChatRoomMember.chat_room_id == chat_room_id,
        ChatRoomMember.user_id == current_user.id
    ).first()
    
    if not chat_room.is_public and not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="该群聊不对外开放"
        )
    
    # 获取当前成员数
    current_members = db.query(func.count(ChatRoomMember.id)).filter(
        ChatRoomMember.chat_room_id == chat_room_id
    ).scalar() or 0
    
    from app.schemas import ResponseModel
    
    return ResponseModel(
        data=ChatRoomResponse(
            chat_room_id=chat_room.id,
            chat_id=chat_room.chat_id,
            name=chat_room.name,
            description=chat_room.description,
            avatar_url=chat_room.avatar_url,
            group_id=chat_room.group_id,
            creator_id=chat_room.created_by,
            max_members=chat_room.max_members,
            current_members=current_members,
            is_public=chat_room.is_public,
            status=chat_room.status,
            created_at=chat_room.created_at
        ).model_dump()
    )


@router.put("/{chat_room_id}")
async def update_chat_room(
    chat_room_id: int,
    update_data: ChatRoomUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新群聊信息（仅群主或管理员可操作）
    """
    # 验证群聊存在
    chat_room = db.query(ChatRoom).filter(
        ChatRoom.id == chat_room_id,
        ChatRoom.status == ChatRoomStatus.ACTIVE
    ).first()
    
    if not chat_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群聊不存在或已关闭"
        )
    
    # 验证用户权限（群主或管理员）
    member = db.query(ChatRoomMember).filter(
        ChatRoomMember.chat_room_id == chat_room_id,
        ChatRoomMember.user_id == current_user.id,
        ChatRoomMember.role.in_(["owner", "admin"])
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有群主或管理员才能编辑群聊"
        )
    
    # 更新群聊信息
    if update_data.name is not None:
        if len(update_data.name.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="群聊名称不能为空"
            )
        chat_room.name = update_data.name.strip()
    
    if update_data.description is not None:
        chat_room.description = update_data.description
    
    if update_data.avatar_url is not None:
        chat_room.avatar_url = update_data.avatar_url
    
    if update_data.is_public is not None:
        chat_room.is_public = update_data.is_public
    
    if update_data.max_members is not None:
        # 检查当前成员数是否超过新的上限
        current_members = db.query(func.count(ChatRoomMember.id)).filter(
            ChatRoomMember.chat_room_id == chat_room_id
        ).scalar() or 0
        
        if update_data.max_members < current_members:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="新的成员上限不能小于当前成员数"
            )
        chat_room.max_members = update_data.max_members
    
    db.commit()
    db.refresh(chat_room)
    
    # 获取当前成员数
    current_members = db.query(func.count(ChatRoomMember.id)).filter(
        ChatRoomMember.chat_room_id == chat_room_id
    ).scalar() or 0
    
    from app.schemas import ResponseModel
    
    return ResponseModel(
        data=ChatRoomResponse(
            chat_room_id=chat_room.id,
            chat_id=chat_room.chat_id,
            name=chat_room.name,
            description=chat_room.description,
            avatar_url=chat_room.avatar_url,
            group_id=chat_room.group_id,
            creator_id=chat_room.created_by,
            max_members=chat_room.max_members,
            current_members=current_members,
            is_public=chat_room.is_public,
            status=chat_room.status,
            created_at=chat_room.created_at
        ).model_dump()
    )


@router.delete("/{chat_room_id}")
async def delete_chat_room(
    chat_room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除群聊（仅群主可操作）
    """
    # 验证群聊存在
    chat_room = db.query(ChatRoom).filter(
        ChatRoom.id == chat_room_id,
        ChatRoom.status == ChatRoomStatus.ACTIVE
    ).first()
    
    if not chat_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群聊不存在或已关闭"
        )
    
    # 验证用户是群主
    if chat_room.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有群主才能删除群聊"
        )
    
    # 软删除：将状态改为已关闭
    chat_room.status = ChatRoomStatus.CLOSED
    db.commit()
    
    from app.schemas import ResponseModel
    return ResponseModel(data={"message": "群聊已成功删除"})


@router.post("/{chat_room_id}/leave")
async def leave_chat_room(
    chat_room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    退出群聊
    
    特殊规则：
    - 群主不能直接退出，需要先转让群主或删除群聊
    """
    # 验证群聊存在
    chat_room = db.query(ChatRoom).filter(
        ChatRoom.id == chat_room_id,
        ChatRoom.status == ChatRoomStatus.ACTIVE
    ).first()
    
    if not chat_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群聊不存在或已关闭"
        )
    
    # 获取成员记录
    member = db.query(ChatRoomMember).filter(
        ChatRoomMember.chat_room_id == chat_room_id,
        ChatRoomMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="您不在该群聊中"
        )
    
    # 群主不能退出
    if member.role == "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="群主不能退出群聊，请先转让群主或删除群聊"
        )
    
    # 删除成员记录
    db.delete(member)
    db.commit()
    
    from app.schemas import ResponseModel
    return ResponseModel(data={"message": "已成功退出群聊"})


@router.post("/{chat_room_id}/join-request")
async def create_join_request(
    chat_room_id: int,
    request_data: ChatRoomJoinRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    发送加入群聊请求
    """
    # 验证群聊存在且活跃
    chat_room = db.query(ChatRoom).filter(
        ChatRoom.id == chat_room_id,
        ChatRoom.status == ChatRoomStatus.ACTIVE
    ).first()
    
    if not chat_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群聊不存在或已关闭"
        )
    
    # 检查是否已加入
    existing_member = db.query(ChatRoomMember).filter(
        ChatRoomMember.chat_room_id == chat_room_id,
        ChatRoomMember.user_id == current_user.id
    ).first()
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="您已在该群聊中"
        )
    
    # 检查是否已有待处理的申请
    existing_request = db.query(ChatRoomJoinRequest).filter(
        ChatRoomJoinRequest.chat_room_id == chat_room_id,
        ChatRoomJoinRequest.user_id == current_user.id,
        ChatRoomJoinRequest.status == ChatRoomJoinStatus.PENDING
    ).first()
    
    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="您已发送过加入请求，请等待审批"
        )
    
    # 检查群聊是否已满
    current_members = db.query(func.count(ChatRoomMember.id)).filter(
        ChatRoomMember.chat_room_id == chat_room_id
    ).scalar() or 0
    
    if current_members >= chat_room.max_members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="群聊成员已满"
        )
    
    # 创建加入请求
    join_request = ChatRoomJoinRequest(
        chat_room_id=chat_room_id,
        user_id=current_user.id,
        message=request_data.message,
        status=ChatRoomJoinStatus.PENDING
    )
    db.add(join_request)
    db.commit()
    db.refresh(join_request)
    
    from app.schemas import ResponseModel
    return ResponseModel(
        data=ChatRoomJoinRequestResponse(
            request_id=join_request.id,
            chat_room_id=join_request.chat_room_id,
            chat_id=chat_room.chat_id,
            chat_room_name=chat_room.name,
            user_id=join_request.user_id,
            username=current_user.username,
            status=join_request.status,
            message=join_request.message,
            reviewed_by=join_request.reviewed_by,
            reviewer_name=None,
            review_message=join_request.review_message,
            created_at=join_request.created_at,
            reviewed_at=join_request.reviewed_at
        ).model_dump()
    )


@router.get("/{chat_room_id}/join-requests")
async def get_join_requests(
    chat_room_id: int,
    status_filter: Optional[ChatRoomJoinStatus] = Query(None, description="筛选状态"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取群聊加入请求列表（管理员/群主权限）
    """
    # 验证群聊存在
    chat_room = db.query(ChatRoom).filter(ChatRoom.id == chat_room_id).first()
    if not chat_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群聊不存在"
        )
    
    # 验证用户权限（管理员或群主）
    member = db.query(ChatRoomMember).filter(
        ChatRoomMember.chat_room_id == chat_room_id,
        ChatRoomMember.user_id == current_user.id,
        ChatRoomMember.role.in_(["owner", "admin"])
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有群主或管理员才能查看加入请求"
        )
    
    # 查询加入请求
    query = db.query(ChatRoomJoinRequest, User).join(
        User, ChatRoomJoinRequest.user_id == User.id
    ).filter(ChatRoomJoinRequest.chat_room_id == chat_room_id)
    
    if status_filter:
        query = query.filter(ChatRoomJoinRequest.status == status_filter)
    
    query = query.order_by(ChatRoomJoinRequest.created_at.desc())
    
    requests_data = []
    for request, user in query.all():
        reviewer_name = None
        if request.reviewed_by:
            reviewer = db.query(User).filter(User.id == request.reviewed_by).first()
            reviewer_name = reviewer.username if reviewer else None
        
        requests_data.append(ChatRoomJoinRequestResponse(
            request_id=request.id,
            chat_room_id=request.chat_room_id,
            chat_id=chat_room.chat_id,
            chat_room_name=chat_room.name,
            user_id=request.user_id,
            username=user.username,
            status=request.status,
            message=request.message,
            reviewed_by=request.reviewed_by,
            reviewer_name=reviewer_name,
            review_message=request.review_message,
            created_at=request.created_at,
            reviewed_at=request.reviewed_at
        ))
    
    from app.schemas import ResponseModel
    return ResponseModel(data={"join_requests": requests_data})


@router.post("/{chat_room_id}/join-requests/{request_id}/review")
async def review_join_request(
    chat_room_id: int,
    request_id: int,
    review_data: ChatRoomJoinRequestReview,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    审批加入请求（管理员/群主权限）
    """
    # 验证群聊存在
    chat_room = db.query(ChatRoom).filter(ChatRoom.id == chat_room_id).first()
    if not chat_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群聊不存在"
        )
    
    # 验证用户权限（管理员或群主）
    member = db.query(ChatRoomMember).filter(
        ChatRoomMember.chat_room_id == chat_room_id,
        ChatRoomMember.user_id == current_user.id,
        ChatRoomMember.role.in_(["owner", "admin"])
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有群主或管理员才能审批加入请求"
        )
    
    # 获取加入请求
    join_request = db.query(ChatRoomJoinRequest).filter(
        ChatRoomJoinRequest.id == request_id,
        ChatRoomJoinRequest.chat_room_id == chat_room_id,
        ChatRoomJoinRequest.status == ChatRoomJoinStatus.PENDING
    ).first()
    
    if not join_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="加入请求不存在或已处理"
        )
    
    # 检查群聊是否已满（只在批准时检查）
    if review_data.approve:
        current_members = db.query(func.count(ChatRoomMember.id)).filter(
            ChatRoomMember.chat_room_id == chat_room_id
        ).scalar() or 0
        
        if current_members >= chat_room.max_members:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="群聊成员已满"
            )
    
    # 更新请求状态
    join_request.status = ChatRoomJoinStatus.APPROVED if review_data.approve else ChatRoomJoinStatus.REJECTED
    join_request.reviewed_by = current_user.id
    join_request.reviewed_at = func.now()
    join_request.review_message = review_data.review_message
    
    # 如果批准，添加成员
    if review_data.approve:
        new_member = ChatRoomMember(
            chat_room_id=chat_room_id,
            user_id=join_request.user_id,
            role="member",
            last_active_at=func.now()
        )
        db.add(new_member)
    
    db.commit()
    db.refresh(join_request)
    
    # 获取用户信息
    user = db.query(User).filter(User.id == join_request.user_id).first()
    
    from app.schemas import ResponseModel
    return ResponseModel(
        data=ChatRoomJoinRequestResponse(
            request_id=join_request.id,
            chat_room_id=join_request.chat_room_id,
            chat_id=chat_room.chat_id,
            chat_room_name=chat_room.name,
            user_id=join_request.user_id,
            username=user.username if user else "未知用户",
            status=join_request.status,
            message=join_request.message,
            reviewed_by=join_request.reviewed_by,
            reviewer_name=current_user.username,
            review_message=join_request.review_message,
            created_at=join_request.created_at,
            reviewed_at=join_request.reviewed_at
        ).model_dump()
    )


@router.get("/{chat_room_id}/members")
async def get_chat_room_members(
    chat_room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取群聊成员列表
    """
    # 验证群聊存在
    chat_room = db.query(ChatRoom).filter(ChatRoom.id == chat_room_id).first()
    if not chat_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群聊不存在"
        )
    
    # 检查用户是否是群聊成员
    is_member = db.query(ChatRoomMember).filter(
        ChatRoomMember.chat_room_id == chat_room_id,
        ChatRoomMember.user_id == current_user.id
    ).first()
    
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有群聊成员才能查看成员列表"
        )
    
    # 获取成员列表
    members_query = db.query(ChatRoomMember, User).join(
        User, ChatRoomMember.user_id == User.id
    ).filter(ChatRoomMember.chat_room_id == chat_room_id)
    
    members = members_query.all()
    
    members_data = []
    for member, user in members:
        members_data.append(ChatRoomMemberResponse(
            user_id=user.id,
            username=user.username,
            avatar_url=user.avatar_url,
            role=member.role,
            joined_at=member.joined_at,
            last_active_at=member.last_active_at,
            is_muted=member.is_muted
        ))
    
    from app.schemas import ResponseModel
    
    return ResponseModel(
        data=ChatRoomMembersResponse(
            chat_room_id=chat_room_id,
            chat_id=chat_room.chat_id,
            name=chat_room.name,
            total_members=len(members_data),
            members=members_data
        ).model_dump()
    )


