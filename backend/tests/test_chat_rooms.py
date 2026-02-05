import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.models import User, Group, GroupMember
from app.chat_models import ChatRoom, ChatRoomMember
from app.auth import get_password_hash

# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_chat.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_users(test_db):
    # 创建两个测试用户
    user1 = User(
        username="user1",
        email="user1@example.com",
        password_hash=get_password_hash("password123")
    )
    user2 = User(
        username="user2",
        email="user2@example.com",
        password_hash=get_password_hash("password123")
    )
    test_db.add(user1)
    test_db.add(user2)
    test_db.commit()
    test_db.refresh(user1)
    test_db.refresh(user2)
    return user1, user2


@pytest.fixture(scope="function")
def auth_headers():
    # 模拟认证token
    return {"Authorization": f"Bearer test_token"}


class TestChatRoomCreation:
    """测试群聊创建功能"""
    
    def test_create_chat_room_only_creator(self, client, auth_headers, test_db, test_users):
        """测试创建群聊时只有创建者被添加"""
        user1, user2 = test_users
        
        # 模拟用户1创建群聊
        chat_data = {
            "name": "测试群聊",
            "description": "这是一个测试群聊",
            "is_public": True,
            "max_members": 100
        }
        
        # 模拟用户1的认证
        def mock_get_current_user():
            return user1
        
        app.dependency_overrides["get_current_user"] = mock_get_current_user
        
        response = client.post("/chat-rooms", json=chat_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "测试群聊"
        assert data["current_members"] == 1
        
        # 验证数据库中只有创建者用户1被添加到群聊中
        chat_room_id = data["chat_room_id"]
        members = test_db.query(ChatRoomMember).filter(ChatRoomMember.chat_room_id == chat_room_id).all()
        
        assert len(members) == 1
        assert members[0].user_id == user1.id
        assert members[0].role == "owner"
        
        # 验证用户2没有被自动添加到群聊中
        user2_in_chat = test_db.query(ChatRoomMember).filter(
            ChatRoomMember.chat_room_id == chat_room_id,
            ChatRoomMember.user_id == user2.id
        ).first()
        
        assert user2_in_chat is None
    
    def test_create_chat_room_with_group_association(self, client, auth_headers, test_db, test_users):
        """测试关联学习群组时创建群聊"""
        user1, user2 = test_users
        
        # 创建一个学习群组，包含两个用户
        group = Group(
            name="测试学习群组",
            description="这是一个测试学习群组",
            daily_checkin_required=True,
            created_by=user1.id
        )
        test_db.add(group)
        test_db.commit()
        test_db.refresh(group)
        
        # 添加用户1为群主
        member1 = GroupMember(
            group_id=group.id,
            user_id=user1.id,
            role="owner"
        )
        test_db.add(member1)
        
        # 添加用户2为成员
        member2 = GroupMember(
            group_id=group.id,
            user_id=user2.id,
            role="member"
        )
        test_db.add(member2)
        test_db.commit()
        
        # 模拟用户1创建关联该群组的群聊
        chat_data = {
            "name": "关联群组的测试群聊",
            "description": "这是一个关联学习群组的测试群聊",
            "is_public": True,
            "max_members": 100,
            "group_id": group.id
        }
        
        # 模拟用户1的认证
        def mock_get_current_user():
            return user1
        
        app.dependency_overrides["get_current_user"] = mock_get_current_user
        
        response = client.post("/chat-rooms", json=chat_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "关联群组的测试群聊"
        assert data["current_members"] == 1
        assert data["group_id"] == group.id
        
        # 验证数据库中只有创建者用户1被添加到群聊中
        chat_room_id = data["chat_room_id"]
        members = test_db.query(ChatRoomMember).filter(ChatRoomMember.chat_room_id == chat_room_id).all()
        
        assert len(members) == 1
        assert members[0].user_id == user1.id
        assert members[0].role == "owner"
        
        # 验证用户2没有被自动添加到群聊中
        user2_in_chat = test_db.query(ChatRoomMember).filter(
            ChatRoomMember.chat_room_id == chat_room_id,
            ChatRoomMember.user_id == user2.id
        ).first()
        
        assert user2_in_chat is None


if __name__ == "__main__":
    pytest.main([__file__])
