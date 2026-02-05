from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, users, plans, checkins, groups, ai
from app.routes import chat_rooms
from app.database import engine, Base, get_db
from app.models import User, Role, UserRole, Plan, Checkin, Group, GroupMember, AIWeeklyReport, APIKey
from app.chat_models import ChatRoom, ChatRoomMember, ChatRoomJoinRequest, ChatMessage

app = FastAPI(title="StudySync API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(plans.router, prefix="/api")
app.include_router(checkins.router, prefix="/api")
app.include_router(groups.router, prefix="/api")
app.include_router(chat_rooms.router, prefix="/api")
app.include_router(ai.router, prefix="/api")


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    
    db = next(get_db())
    
    default_role = db.query(Role).filter(Role.name == "user").first()
    if not default_role:
        default_role = Role(name="user", description="普通用户")
        db.add(default_role)
        db.commit()
    
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        admin_role = Role(name="admin", description="管理员")
        db.add(admin_role)
        db.commit()
    
    db.close()


@app.get("/")
async def root():
    return {
        "message": "Welcome to StudySync API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
