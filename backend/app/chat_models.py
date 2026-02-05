from sqlalchemy import Column, BigInteger, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class ChatRoomStatus(enum.Enum):
    """群聊状态"""
    ACTIVE = "active"  # 正常
    ARCHIVED = "archived"  # 归档
    SUSPENDED = "suspended"  # 暂停


class ChatRoomJoinStatus(enum.Enum):
    """加入请求状态"""
    PENDING = "pending"  # 待审批
    APPROVED = "approved"  # 已批准
    REJECTED = "rejected"  # 已拒绝
    CANCELLED = "cancelled"  # 已取消


class ChatRoom(Base):
    """群聊房间表"""
    __tablename__ = "chat_rooms"
    
    id = Column(BigInteger, primary_key=True, index=True)
    chat_id = Column(String(20), unique=True, nullable=False, index=True)  # 唯一群聊ID
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    avatar_url = Column(String(256), nullable=True)
    group_id = Column(BigInteger, ForeignKey("groups.id", ondelete="CASCADE"), nullable=True)  # 关联的学习群组
    created_by = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    max_members = Column(Integer, default=500, nullable=False)  # 最大成员数
    is_public = Column(Boolean, default=True, nullable=False)  # 是否公开可搜索
    status = Column(Enum(ChatRoomStatus), default=ChatRoomStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关联
    creator = relationship("User", foreign_keys=[created_by])
    group = relationship("Group", back_populates="chat_room")
    members = relationship("ChatRoomMember", back_populates="chat_room", cascade="all, delete-orphan")
    join_requests = relationship("ChatRoomJoinRequest", back_populates="chat_room", cascade="all, delete-orphan")


class ChatRoomMember(Base):
    """群聊成员表"""
    __tablename__ = "chat_room_members"
    
    id = Column(BigInteger, primary_key=True, index=True)
    chat_room_id = Column(BigInteger, ForeignKey("chat_rooms.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False, default="member")  # member, admin, owner
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active_at = Column(DateTime(timezone=True), nullable=True)
    is_muted = Column(Boolean, default=False, nullable=False)  # 是否禁言
    
    # 联合唯一索引
    __table_args__ = (
        Index('idx_chat_room_user', 'chat_room_id', 'user_id', unique=True),
    )
    
    # 关联
    chat_room = relationship("ChatRoom", back_populates="members")
    user = relationship("User")


class ChatRoomJoinRequest(Base):
    """群聊加入请求表"""
    __tablename__ = "chat_room_join_requests"
    
    id = Column(BigInteger, primary_key=True, index=True)
    chat_room_id = Column(BigInteger, ForeignKey("chat_rooms.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(ChatRoomJoinStatus), default=ChatRoomJoinStatus.PENDING, nullable=False)
    message = Column(Text, nullable=True)  # 申请理由
    reviewed_by = Column(BigInteger, ForeignKey("users.id"), nullable=True)  # 审批人
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    review_message = Column(Text, nullable=True)  # 审批意见
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 联合索引，防止重复申请
    __table_args__ = (
        Index('idx_user_chat_room', 'user_id', 'chat_room_id', unique=True),
    )
    
    # 关联
    chat_room = relationship("ChatRoom", back_populates="join_requests")
    user = relationship("User", foreign_keys=[user_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])


class ChatMessage(Base):
    """聊天消息表（预留，用于后续扩展）"""
    __tablename__ = "chat_messages"
    
    id = Column(BigInteger, primary_key=True, index=True)
    chat_room_id = Column(BigInteger, ForeignKey("chat_rooms.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default="text", nullable=False)  # text, image, file
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联
    chat_room = relationship("ChatRoom")
    user = relationship("User")