from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import date, datetime


class ResponseModel(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[dict] = None


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=20)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    user_id: int
    username: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserAuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class PlanCreate(BaseModel):
    title: str = Field(..., max_length=100)
    description: Optional[str] = None
    daily_goal_hours: float = Field(..., ge=0.1)
    start_date: date
    end_date: Optional[date] = None

    @validator('daily_goal_hours')
    def convert_to_minutes(cls, v):
        return int(v * 60)


class PlanUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    daily_goal_hours: Optional[float] = Field(None, ge=0.1)
    end_date: Optional[date] = None
    status: Optional[str] = None

    @validator('daily_goal_hours')
    def convert_to_minutes(cls, v):
        if v is not None:
            return int(v * 60)
        return v


class PlanResponse(BaseModel):
    plan_id: int
    user_id: int
    title: str
    description: Optional[str] = None
    daily_goal_hours: float
    start_date: date
    end_date: Optional[date] = None
    status: str = "active"
    created_at: datetime
    progress: Optional[dict] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        data = obj.__dict__.copy()
        data['plan_id'] = obj.id
        data['daily_goal_hours'] = obj.daily_goal_min / 60
        return cls(**data)


class PlansListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[PlanResponse]


class CheckinCreate(BaseModel):
    plan_id: int
    hours: float = Field(..., ge=0.1)
    content: str
    checkin_date: Optional[date] = None

    @validator('hours')
    def convert_to_minutes(cls, v):
        return int(v * 60)


class CheckinResponse(BaseModel):
    checkin_id: int
    user_id: int
    plan_id: int
    plan_title: Optional[str] = None
    hours: float
    content: str
    checkin_date: date
    created_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        data = obj.__dict__.copy()
        data['checkin_id'] = obj.id
        data['hours'] = obj.duration_min / 60
        data['checkin_date'] = obj.checkin_date
        return cls(**data)


class CheckinsListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[CheckinResponse]


class TodayCheckinResponse(BaseModel):
    date: date
    checked_in: bool
    total_hours: float
    checkins: List[CheckinResponse]


class DailyStats(BaseModel):
    date: date
    hours: float
    checkin_count: int


class CheckinStatsResponse(BaseModel):
    period: str
    total_hours: float
    total_days: int
    checkin_count: int
    avg_hours_per_day: float
    checkin_rate: float
    daily_stats: List[DailyStats]


class GroupCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    daily_checkin_rule: dict = Field(default={"min_checkins_per_day": 1})
    auto_remove_days: int = 3


class GroupResponse(BaseModel):
    group_id: int
    name: str
    description: Optional[str] = None
    creator_id: int
    member_count: int
    created_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        data = obj.__dict__.copy()
        data['group_id'] = obj.id
        data['creator_id'] = obj.created_by
        data['member_count'] = len(obj.members) if obj.members else 0
        return cls(**data)


class GroupsListResponse(BaseModel):
    created: List[GroupResponse]
    joined: List[GroupResponse]


class GroupMemberResponse(BaseModel):
    user_id: int
    username: str
    avatar_url: Optional[str] = None
    role: str
    joined_at: datetime
    last_checkin_date: Optional[date] = None
    days_without_checkin: int = 0


class GroupMembersResponse(BaseModel):
    group_id: int
    name: str
    total_members: int
    members: List[GroupMemberResponse]


class GroupCheckinMember(BaseModel):
    user_id: int
    username: str
    hours: Optional[float] = None
    checkin_time: Optional[datetime] = None


class GroupCheckinsResponse(BaseModel):
    group_id: int
    date: date
    total_members: int
    checked_in_count: int
    not_checked_in_count: int
    checked_in: List[GroupCheckinMember]
    not_checked_in: List[dict]


class AIReportResponse(BaseModel):
    week_start: date
    week_end: date
    generated_at: datetime
    score: dict
    summary: dict
    issues: List[str]
    suggestions: List[str]
    recommended_hours: float


class AIReportGenerate(BaseModel):
    user_id: int
    week_start: date
    week_end: date


class AIReportTaskResponse(BaseModel):
    task_id: str
    status: str
    estimated_time: int


class APIKeyResponse(BaseModel):
    api_key: str
    created_at: datetime
