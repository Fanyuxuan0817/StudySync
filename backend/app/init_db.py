from .database import SessionLocal, engine
from .models import Base, User, Role, UserRole, Plan, Checkin, Group, GroupMember, AIWeeklyReport, APIKey
from .auth import get_password_hash


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        user_role = db.query(Role).filter(Role.name == "user").first()
        if not user_role:
            user_role = Role(name="user", description="普通用户")
            db.add(user_role)
        
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            admin_role = Role(name="admin", description="管理员")
            db.add(admin_role)
        
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@studysync.com",
                password_hash=get_password_hash("admin123"),
                avatar_url=None
            )
            db.add(admin_user)
            db.flush()
            
            admin_user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
            db.add(admin_user_role)
        
        db.commit()
        print("数据库初始化成功!")
        print("管理员账号: admin")
        print("管理员密码: admin123")
        
    except Exception as e:
        db.rollback()
        print(f"数据库初始化失败: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
