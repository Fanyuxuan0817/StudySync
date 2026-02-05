import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.models import User, Group, GroupMember, Checkin
from datetime import date, timedelta
import json

# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
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
def test_user(test_db):
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="testpassword"  # 修正字段名
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(test_user):
    # 模拟认证token
    return {"Authorization": f"Bearer test_token"}


class TestGroupCreation:
    """测试群组创建功能"""
    
    def test_create_group_success(self, client, auth_headers):
        """测试成功创建群组"""
        group_data = {
            "name": "测试学习群组",
            "description": "这是一个测试群组",
            "daily_checkin_required": True
        }
        
        response = client.post("/groups", json=group_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "测试学习群组"
        assert data["description"] == "这是一个测试群组"
        assert data["daily_checkin_required"] is True
        assert "group_id" in data
        assert data["member_count"] == 1
    
    def test_create_group_empty_name(self, client, auth_headers):
        """测试创建群组时名称为空"""
        group_data = {
            "name": "",
            "description": "这是一个测试群组",
            "daily_checkin_required": True
        }
        
        response = client.post("/groups", json=group_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "群组名称不能为空" in response.json()["detail"]
    
    def test_create_group_name_too_long(self, client, auth_headers):
        """测试创建群组时名称过长"""
        group_data = {
            "name": "a" * 101,  # 超过100字符限制
            "description": "这是一个测试群组",
            "daily_checkin_required": True
        }
        
        response = client.post("/groups", json=group_data, headers=auth_headers)
        
        assert response.status_code == 422  # FastAPI验证错误


class TestGroupJoinLeave:
    """测试加入和退出群组功能"""
    
    @pytest.fixture
    def existing_group(self, test_db, test_user):
        """创建测试群组"""
        group = Group(
            name="现有测试群组",
            description="用于测试的群组",
            daily_checkin_required=True,
            created_by=test_user.id
        )
        test_db.add(group)
        test_db.commit()
        test_db.refresh(group)
        
        # 添加创建者为群主
        member = GroupMember(
            group_id=group.id,
            user_id=test_user.id,
            role="owner"
        )
        test_db.add(member)
        test_db.commit()
        
        return group
    
    def test_join_group_success(self, client, auth_headers, existing_group, test_db):
        """测试成功加入群组"""
        # 创建第二个用户
        new_user = User(username="newuser", email="new@example.com", password_hash="test")
        test_db.add(new_user)
        test_db.commit()
        
        # 模拟新用户的认证
        new_auth_headers = {"Authorization": f"Bearer new_token"}
        
        response = client.post(f"/groups/{existing_group.id}/join", headers=new_auth_headers)
        
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["group_id"] == existing_group.id
        assert data["role"] == "member"
        assert data["daily_checkin_required"] is True
    
    def test_join_group_already_member(self, client, auth_headers, existing_group):
        """测试重复加入群组"""
        response = client.post(f"/groups/{existing_group.id}/join", headers=auth_headers)
        
        assert response.status_code == 409
        assert "已在群组中" in response.json()["detail"]
    
    def test_join_nonexistent_group(self, client, auth_headers):
        """测试加入不存在的群组"""
        response = client.post("/groups/999/join", headers=auth_headers)
        
        assert response.status_code == 404
        assert "群组不存在" in response.json()["detail"]
    
    def test_leave_group_success(self, client, auth_headers, existing_group, test_db):
        """测试成功退出群组"""
        # 先创建并加入群组的新用户
        new_user = User(username="leaver", email="leave@example.com", password_hash="test")
        test_db.add(new_user)
        test_db.commit()
        
        member = GroupMember(group_id=existing_group.id, user_id=new_user.id, role="member")
        test_db.add(member)
        test_db.commit()
        
        new_auth_headers = {"Authorization": f"Bearer leave_token"}
        
        response = client.post(f"/groups/{existing_group.id}/leave", headers=new_auth_headers)
        
        assert response.status_code == 200
    
    def test_leave_group_owner_cannot_leave(self, client, auth_headers, existing_group):
        """测试群主不能直接退出群组"""
        response = client.post(f"/groups/{existing_group.id}/leave", headers=auth_headers)
        
        assert response.status_code == 403
        assert "群主不能退出群组" in response.json()["detail"]


class TestGroupTransfer:
    """测试群主转让功能"""
    
    @pytest.fixture
    def existing_group(self, test_db, test_user):
        """创建测试群组"""
        group = Group(
            name="转让测试群组",
            description="用于测试群主转让的群组",
            daily_checkin_required=True,
            created_by=test_user.id
        )
        test_db.add(group)
        test_db.commit()
        test_db.refresh(group)
        
        # 添加创建者为群主
        member = GroupMember(
            group_id=group.id,
            user_id=test_user.id,
            role="owner"
        )
        test_db.add(member)
        test_db.commit()
        
        return group
    
    @pytest.fixture
    def new_member(self, test_db, existing_group):
        """创建新成员"""
        new_user = User(username="newowner", email="newowner@example.com", password_hash="test")
        test_db.add(new_user)
        test_db.commit()
        
        member = GroupMember(
            group_id=existing_group.id,
            user_id=new_user.id,
            role="member"
        )
        test_db.add(member)
        test_db.commit()
        
        return new_user
    
    def test_transfer_ownership_success(self, client, auth_headers, existing_group, new_member):
        """测试成功转让群主"""
        transfer_data = {
            "new_owner_id": new_member.id
        }
        
        response = client.post(f"/groups/{existing_group.id}/transfer", json=transfer_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["previous_owner_id"] == existing_group.created_by
        assert data["new_owner_id"] == new_member.id
    
    def test_transfer_ownership_not_owner(self, client, auth_headers, existing_group, new_member, test_db):
        """测试非群主尝试转让群主权限"""
        # 创建另一个普通成员
        regular_user = User(username="regular", email="regular@example.com", password_hash="test")
        test_db.add(regular_user)
        test_db.commit()
        
        member = GroupMember(group_id=existing_group.id, user_id=regular_user.id, role="member")
        test_db.add(member)
        test_db.commit()
        
        regular_auth_headers = {"Authorization": f"Bearer regular_token"}
        
        transfer_data = {
            "new_owner_id": new_member.id
        }
        
        response = client.post(f"/groups/{existing_group.id}/transfer", json=transfer_data, headers=regular_auth_headers)
        
        assert response.status_code == 403
        assert "只有群主才能转让群主权限" in response.json()["detail"]
    
    def test_transfer_ownership_nonexistent_user(self, client, auth_headers, existing_group):
        """测试转让给不存在的用户"""
        transfer_data = {
            "new_owner_id": 999
        }
        
        response = client.post(f"/groups/{existing_group.id}/transfer", json=transfer_data, headers=auth_headers)
        
        assert response.status_code == 404
        assert "新群主用户不存在" in response.json()["detail"]
    
    def test_transfer_ownership_non_member(self, client, auth_headers, existing_group, test_db):
        """测试转让给非群组成员"""
        # 创建不在群组中的用户
        outsider = User(username="outsider", email="outsider@example.com", password_hash="test")
        test_db.add(outsider)
        test_db.commit()
        
        transfer_data = {
            "new_owner_id": outsider.id
        }
        
        response = client.post(f"/groups/{existing_group.id}/transfer", json=transfer_data, headers=auth_headers)
        
        assert response.status_code == 404
        assert "新群主必须是群组成员" in response.json()["detail"]


class TestGroupDeletion:
    """测试群组解散功能"""
    
    @pytest.fixture
    def existing_group(self, test_db, test_user):
        """创建测试群组"""
        group = Group(
            name="解散测试群组",
            description="用于测试群组解散的群组",
            daily_checkin_required=True,
            created_by=test_user.id
        )
        test_db.add(group)
        test_db.commit()
        test_db.refresh(group)
        
        # 添加创建者为群主
        member = GroupMember(
            group_id=group.id,
            user_id=test_user.id,
            role="owner"
        )
        test_db.add(member)
        test_db.commit()
        
        return group
    
    def test_delete_group_success(self, client, auth_headers, existing_group):
        """测试成功解散群组"""
        response = client.delete(f"/groups/{existing_group.id}", headers=auth_headers)
        
        assert response.status_code == 200
        assert "群组已成功解散" in response.json()["data"]["message"]
    
    def test_delete_group_not_owner(self, client, auth_headers, existing_group, test_db):
        """测试非群主尝试解散群组"""
        # 创建另一个普通成员
        regular_user = User(username="regular", email="regular@example.com", password_hash="test")
        test_db.add(regular_user)
        test_db.commit()
        
        member = GroupMember(group_id=existing_group.id, user_id=regular_user.id, role="member")
        test_db.add(member)
        test_db.commit()
        
        regular_auth_headers = {"Authorization": f"Bearer regular_token"}
        
        response = client.delete(f"/groups/{existing_group.id}", headers=regular_auth_headers)
        
        assert response.status_code == 403
        assert "只有群主才能解散群组" in response.json()["detail"]
    
    def test_delete_nonexistent_group(self, client, auth_headers):
        """测试解散不存在的群组"""
        response = client.delete("/groups/999", headers=auth_headers)
        
        assert response.status_code == 404
        assert "群组不存在" in response.json()["detail"]


class TestGroupStats:
    """测试群组统计功能"""
    
    @pytest.fixture
    def existing_group(self, test_db, test_user):
        """创建测试群组"""
        group = Group(
            name="统计测试群组",
            description="用于测试统计的群组",
            daily_checkin_required=True,
            created_by=test_user.id
        )
        test_db.add(group)
        test_db.commit()
        test_db.refresh(group)
        
        # 添加创建者为群主
        member = GroupMember(
            group_id=group.id,
            user_id=test_user.id,
            role="owner"
        )
        test_db.add(member)
        test_db.commit()
        
        return group
    
    @pytest.fixture
    def member_with_checkins(self, test_db, existing_group):
        """创建有打卡记录的成员"""
        user = User(username="checker", email="checker@example.com", password_hash="test")
        test_db.add(user)
        test_db.commit()
        
        member = GroupMember(group_id=existing_group.id, user_id=user.id, role="member")
        test_db.add(member)
        test_db.commit()
        
        # 添加一些打卡记录
        today = date.today()
        for i in range(3):  # 本周3天打卡
            checkin_date = today - timedelta(days=i)
            checkin = Checkin(
                user_id=user.id,
                plan_id=1,
                checkin_date=checkin_date,
                duration_min=120  # 2小时
            )
            test_db.add(checkin)
        
        test_db.commit()
        return user
    
    def test_get_group_stats_success(self, client, auth_headers, existing_group, member_with_checkins):
        """测试获取群组统计"""
        response = client.get(f"/groups/{existing_group.id}/stats", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()["data"]
        
        # 验证群组层面统计
        assert data["total_members"] == 2  # 群主 + 1成员
        assert data["today_checked_in_count"] >= 0
        assert 0 <= data["checkin_rate"] <= 100
        assert data["daily_checkin_required"] is True
        
        # 验证个人统计
        assert "personal_stats" in data
        assert len(data["personal_stats"]) == 2
        
        # 验证当前用户的个人统计
        assert "my_stats" in data
        my_stats = data["my_stats"]
        assert my_stats is not None
        assert "week_checkin_days" in my_stats
        assert "avg_hours_per_day" in my_stats
    
    def test_get_group_stats_non_member(self, client, auth_headers, existing_group, test_db):
        """测试非群组成员获取统计"""
        # 创建不在群组中的用户
        outsider = User(username="outsider", email="outsider@example.com", password_hash="test")
        test_db.add(outsider)
        test_db.commit()
        
        outsider_auth_headers = {"Authorization": f"Bearer outsider_token"}
        
        response = client.get(f"/groups/{existing_group.id}/stats", headers=outsider_auth_headers)
        
        assert response.status_code == 403
        assert "您不是该群组成员" in response.json()["detail"]


class TestGroupPermissions:
    """测试群组权限控制"""
    
    @pytest.fixture
    def existing_group(self, test_db, test_user):
        """创建测试群组"""
        group = Group(
            name="权限测试群组",
            description="用于测试权限的群组",
            daily_checkin_required=True,
            created_by=test_user.id
        )
        test_db.add(group)
        test_db.commit()
        test_db.refresh(group)
        
        # 添加创建者为群主
        member = GroupMember(
            group_id=group.id,
            user_id=test_user.id,
            role="owner"
        )
        test_db.add(member)
        test_db.commit()
        
        return group
    
    @pytest.fixture
    def regular_member(self, test_db, existing_group):
        """创建普通成员"""
        user = User(username="regular", email="regular@example.com", password_hash="test")
        test_db.add(user)
        test_db.commit()
        
        member = GroupMember(group_id=existing_group.id, user_id=user.id, role="member")
        test_db.add(member)
        test_db.commit()
        
        return user
    
    def test_owner_remove_member(self, client, auth_headers, existing_group, regular_member, test_db):
        """测试群主移除成员"""
        response = client.delete(f"/groups/{existing_group.id}/members/{regular_member.id}", headers=auth_headers)
        
        assert response.status_code == 200
        
        # 验证成员已被移除
        member = test_db.query(GroupMember).filter(
            GroupMember.group_id == existing_group.id,
            GroupMember.user_id == regular_member.id
        ).first()
        
        assert member is None
    
    def test_member_cannot_remove_others(self, client, auth_headers, existing_group, regular_member, test_db):
        """测试普通成员不能移除其他成员"""
        # 创建另一个普通成员
        another_user = User(username="another", email="another@example.com", password_hash="test")
        test_db.add(another_user)
        test_db.commit()
        
        another_member = GroupMember(group_id=existing_group.id, user_id=another_user.id, role="member")
        test_db.add(another_member)
        test_db.commit()
        
        # 模拟普通成员认证
        regular_auth_headers = {"Authorization": f"Bearer regular_token"}
        
        response = client.delete(f"/groups/{existing_group.id}/members/{another_user.id}", headers=regular_auth_headers)
        
        assert response.status_code == 403
        assert "只有群主才能移除成员" in response.json()["detail"]
    
    def test_owner_cannot_remove_self(self, client, auth_headers, existing_group, test_user):
        """测试群主不能移除自己"""
        response = client.delete(f"/groups/{existing_group.id}/members/{test_user.id}", headers=auth_headers)
        
        assert response.status_code == 400
        assert "不能移除自己，请先转让群主权限" in response.json()["detail"]


class TestGroupCheckinIntegration:
    """测试群组与打卡功能的集成"""
    
    @pytest.fixture
    def existing_group(self, test_db, test_user):
        """创建测试群组"""
        group = Group(
            name="打卡集成测试群组",
            description="用于测试打卡集成的群组",
            daily_checkin_required=True,
            created_by=test_user.id
        )
        test_db.add(group)
        test_db.commit()
        test_db.refresh(group)
        
        # 添加创建者为群主
        member = GroupMember(
            group_id=group.id,
            user_id=test_user.id,
            role="owner"
        )
        test_db.add(member)
        test_db.commit()
        
        return group
    
    def test_checkin_updates_group_last_checkin(self, client, auth_headers, existing_group, test_db):
        """测试打卡时更新群组的最后打卡日期"""
        # 创建学习计划
        from app.models import Plan
        plan = Plan(
            user_id=test_user.id,
            title="测试学习计划",
            description="用于测试的学习计划",
            target_hours=10,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7)
        )
        test_db.add(plan)
        test_db.commit()
        
        # 进行打卡
        checkin_data = {
            "plan_id": plan.id,
            "hours": 2,
            "content": "今日学习内容"
        }
        
        response = client.post("/checkins", json=checkin_data, headers=auth_headers)
        
        assert response.status_code == 200
        
        # 验证群组成员的最后打卡日期已更新
        member = test_db.query(GroupMember).filter(
            GroupMember.group_id == existing_group.id,
            GroupMember.user_id == test_user.id
        ).first()
        
        assert member.last_checkin == date.today()


if __name__ == "__main__":
    pytest.main([__file__])