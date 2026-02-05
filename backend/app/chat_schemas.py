from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ChatRoomStatus(str, Enum):
    """群聊状态"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    SUSPENDED = "suspended"


class ChatRoomJoinStatus(str, Enum):
    """加入请求状态"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class ChatRoomMemberRole(str, Enum):
    """群聊成员角色"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class ChatRoomCreate(BaseModel):
    """创建群聊请求"""
    name: str = Field(..., max_length=100, description="群聊名称")
    description: Optional[str] = Field(None, description="群聊描述")
    avatar_url: Optional[str] = Field(None, description="群聊头像URL")
    group_id: Optional[int] = Field(None, description="关联的学习群组ID")
    max_members: int = Field(default=500, ge=10, le=1000, description="最大成员数")
    is_public: bool = Field(default=True, description="是否公开可搜索")


class ChatRoomUpdate(BaseModel):
    """更新群聊信息"""
    name: Optional[str] = Field(None, max_length=100, description="群聊名称")
    description: Optional[str] = Field(None, description="群聊描述")
    avatar_url: Optional[str] = Field(None, description="群聊头像URL")
    max_members: Optional[int] = Field(None, ge=10, le=1000, description="最大成员数")
    is_public: Optional[bool] = Field(None, description="是否公开可搜索")
    status: Optional[str] = Field(None, description="群聊状态")


class ChatRoomResponse(BaseModel):
    """群聊响应"""
    chat_room_id: int
    chat_id: str
    name: str
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    group_id: Optional[int] = None
    creator_id: int
    max_members: int
    current_members: int
    is_public: bool
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatRoomSearchResponse(BaseModel):
    """群聊搜索响应"""
    chat_rooms: List[ChatRoomResponse]
    total: int
    page: int
    page_size: int


class ChatRoomJoinRequestCreate(BaseModel):
    """发送加入群聊请求"""
    message: Optional[str] = Field(None, max_length=500, description="申请理由")


class ChatRoomJoinRequestResponse(BaseModel):
    """加入请求响应"""
    request_id: int
    chat_room_id: int
    chat_id: str
    chat_room_name: str
    user_id: int
    username: str
    status: str
    message: Optional[str] = None
    reviewed_by: Optional[int] = None
    reviewer_name: Optional[str] = None
    review_message: Optional[str] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ChatRoomJoinRequestReview(BaseModel):
    """审批加入请求"""
    approve: bool = Field(..., description="是否批准")
    review_message: Optional[str] = Field(None, max_length=500, description="审批意见")


class ChatRoomMemberResponse(BaseModel):
    """群聊成员响应"""
    user_id: int
    username: str
    avatar_url: Optional[str] = None
    role: str
    joined_at: datetime
    last_active_at: Optional[datetime] = None
    is_muted: bool
    
    class Config:
        from_attributes = True


class ChatRoomMembersResponse(BaseModel):
    """群聊成员列表响应"""
    chat_room_id: int
    chat_id: str
    name: str
    total_members: int
    members: List[ChatRoomMemberResponse]


class ChatIdSearchRequest(BaseModel):
    """群聊ID搜索请求"""
    chat_id: str = Field(..., min_length=6, max_length=20, description="群聊ID")


class ChatRoomBriefResponse(BaseModel):
    """群聊简要信息"""
    chat_room_id: int
    chat_id: str
    name: str
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    current_members: int
    max_members: int
    is_public: bool
    
    class Config:
        from_attributes = True