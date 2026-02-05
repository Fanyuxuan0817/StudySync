from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional, List
from datetime import datetime, timedelta

from app.database import get_db
from app.auth import get_current_user
from app.chat_models import ChatRoom, ChatRoomMember, ChatMessage, ChatRoomStatus
from app.models import User
from app.chat_websocket import chat_websocket_endpoint
from app.schemas import ResponseModel

router = APIRouter(prefix="/chat-rooms", tags=["聊天消息"])


@router.get("/{chat_room_id}/messages")
async def get_chat_messages(
    chat_room_id: int,
    before_id: Optional[int] = Query(None, description="获取此ID之前的消息（用于分页）"),
    limit: int = Query(50, ge=1, le=100, description="每页消息数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取群聊消息历史
    
    支持分页加载，从最新消息开始，向上滚动加载更早的消息
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
    
    # 验证用户是群聊成员
    is_member = db.query(ChatRoomMember).filter(
        ChatRoomMember.chat_room_id == chat_room_id,
        ChatRoomMember.user_id == current_user.id
    ).first()
    
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有群聊成员才能查看消息"
        )
    
    # 构建查询
    query = db.query(ChatMessage, User).join(
        User, ChatMessage.user_id == User.id
    ).filter(
        ChatMessage.chat_room_id == chat_room_id,
        ChatMessage.is_deleted == False
    )
    
    # 如果指定了before_id，获取更早的消息
    if before_id:
        query = query.filter(ChatMessage.id < before_id)
    
    # 按时间倒序，获取最新消息
    messages = query.order_by(desc(ChatMessage.id)).limit(limit).all()
    
    # 转换为响应格式（反转顺序，使消息按时间正序排列）
    messages_data = []
    for message, user in reversed(messages):
        messages_data.append({
            "message_id": message.id,
            "user_id": user.id,
            "username": user.username,
            "avatar_url": user.avatar_url,
            "content": message.content,
            "message_type": message.message_type,
            "timestamp": message.created_at.isoformat(),
            "is_own": user.id == current_user.id
        })
    
    # 获取是否有更多消息
    has_more = False
    if messages:
        oldest_id = min(m[0].id for m in messages)
        has_more = db.query(ChatMessage).filter(
            ChatMessage.chat_room_id == chat_room_id,
            ChatMessage.id < oldest_id,
            ChatMessage.is_deleted == False
        ).first() is not None
    
    return ResponseModel(data={
        "messages": messages_data,
        "has_more": has_more,
        "total_count": len(messages_data)
    })


@router.post("/{chat_room_id}/messages")
async def send_message(
    chat_room_id: int,
    content: str,
    message_type: str = Query("text", description="消息类型: text, image, file"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    发送消息（HTTP 方式，用于不支持 WebSocket 的场景）
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
    
    # 验证用户是群聊成员
    member = db.query(ChatRoomMember).filter(
        ChatRoomMember.chat_room_id == chat_room_id,
        ChatRoomMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有群聊成员才能发送消息"
        )
    
    # 检查是否被禁言
    if member.is_muted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您已被禁言，无法发送消息"
        )
    
    # 验证消息内容
    if not content or not content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="消息内容不能为空"
        )
    
    # 创建消息
    chat_message = ChatMessage(
        chat_room_id=chat_room_id,
        user_id=current_user.id,
        content=content.strip(),
        message_type=message_type
    )
    db.add(chat_message)
    
    # 更新最后活跃时间
    member.last_active_at = datetime.utcnow()
    
    db.commit()
    db.refresh(chat_message)
    
    return ResponseModel(data={
        "message_id": chat_message.id,
        "user_id": current_user.id,
        "username": current_user.username,
        "avatar_url": current_user.avatar_url,
        "content": chat_message.content,
        "message_type": chat_message.message_type,
        "timestamp": chat_message.created_at.isoformat(),
        "is_own": True
    })


@router.delete("/{chat_room_id}/messages/{message_id}")
async def delete_message(
    chat_room_id: int,
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除消息（仅发送者或群主/管理员可操作）
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
    
    # 获取消息
    message = db.query(ChatMessage).filter(
        ChatMessage.id == message_id,
        ChatMessage.chat_room_id == chat_room_id
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在"
        )
    
    # 检查权限：消息发送者、群主或管理员可以删除
    can_delete = False
    
    if message.user_id == current_user.id:
        can_delete = True
    else:
        # 检查是否是群主或管理员
        member = db.query(ChatRoomMember).filter(
            ChatRoomMember.chat_room_id == chat_room_id,
            ChatRoomMember.user_id == current_user.id,
            ChatRoomMember.role.in_(["owner", "admin"])
        ).first()
        if member:
            can_delete = True
    
    if not can_delete:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限删除此消息"
        )
    
    # 软删除
    message.is_deleted = True
    db.commit()
    
    return ResponseModel(data={"message": "消息已删除"})


@router.get("/{chat_room_id}/messages/search")
async def search_messages(
    chat_room_id: int,
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(20, ge=1, le=50, description="返回数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    搜索群聊消息
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
    
    # 验证用户是群聊成员
    is_member = db.query(ChatRoomMember).filter(
        ChatRoomMember.chat_room_id == chat_room_id,
        ChatRoomMember.user_id == current_user.id
    ).first()
    
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有群聊成员才能搜索消息"
        )
    
    # 搜索消息
    messages = db.query(ChatMessage, User).join(
        User, ChatMessage.user_id == User.id
    ).filter(
        ChatMessage.chat_room_id == chat_room_id,
        ChatMessage.is_deleted == False,
        ChatMessage.content.contains(keyword)
    ).order_by(desc(ChatMessage.created_at)).limit(limit).all()
    
    messages_data = []
    for message, user in messages:
        messages_data.append({
            "message_id": message.id,
            "user_id": user.id,
            "username": user.username,
            "avatar_url": user.avatar_url,
            "content": message.content,
            "message_type": message.message_type,
            "timestamp": message.created_at.isoformat(),
            "is_own": user.id == current_user.id
        })
    
    return ResponseModel(data={
        "messages": messages_data,
        "keyword": keyword,
        "total_count": len(messages_data)
    })


@router.get("/{chat_room_id}/messages/recent")
async def get_recent_messages(
    chat_room_id: int,
    days: int = Query(7, ge=1, le=30, description="最近几天的消息"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取最近几天的消息统计
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
    
    # 验证用户是群聊成员
    is_member = db.query(ChatRoomMember).filter(
        ChatRoomMember.chat_room_id == chat_room_id,
        ChatRoomMember.user_id == current_user.id
    ).first()
    
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有群聊成员才能查看消息统计"
        )
    
    # 计算日期范围
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # 统计每天的消息数
    daily_stats = db.query(
        func.date(ChatMessage.created_at).label('date'),
        func.count(ChatMessage.id).label('count')
    ).filter(
        ChatMessage.chat_room_id == chat_room_id,
        ChatMessage.is_deleted == False,
        ChatMessage.created_at >= start_date
    ).group_by(
        func.date(ChatMessage.created_at)
    ).order_by(
        func.date(ChatMessage.created_at)
    ).all()
    
    # 统计活跃用户
    active_users = db.query(
        ChatMessage.user_id,
        User.username,
        func.count(ChatMessage.id).label('message_count')
    ).join(
        User, ChatMessage.user_id == User.id
    ).filter(
        ChatMessage.chat_room_id == chat_room_id,
        ChatMessage.is_deleted == False,
        ChatMessage.created_at >= start_date
    ).group_by(
        ChatMessage.user_id,
        User.username
    ).order_by(
        desc(func.count(ChatMessage.id))
    ).limit(10).all()
    
    return ResponseModel(data={
        "daily_stats": [
            {"date": str(stat.date), "count": stat.count}
            for stat in daily_stats
        ],
        "active_users": [
            {
                "user_id": user.user_id,
                "username": user.username,
                "message_count": user.message_count
            }
            for user in active_users
        ],
        "total_messages": sum(stat.count for stat in daily_stats)
    })


# WebSocket 端点
@router.websocket("/ws/{chat_room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    chat_room_id: int,
    token: str
):
    """
    WebSocket 实时聊天端点
    
    连接方式: ws://host/api/chat-rooms/ws/{chat_room_id}?token={jwt_token}
    """
    # 获取数据库会话
    db = next(get_db())
    try:
        await chat_websocket_endpoint(websocket, chat_room_id, token, db)
    finally:
        db.close()
