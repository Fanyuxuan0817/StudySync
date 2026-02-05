import json
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.auth import get_current_user_ws
from app.chat_models import ChatRoom, ChatRoomMember, ChatMessage, ChatRoomStatus
from app.models import User
import asyncio
from datetime import datetime


class ConnectionManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        # 存储每个群聊的连接: {chat_room_id: {user_id: WebSocket}}
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}
        # 存储用户当前所在的群聊: {user_id: chat_room_id}
        self.user_rooms: Dict[int, int] = {}
    
    async def connect(self, websocket: WebSocket, chat_room_id: int, user_id: int):
        """建立 WebSocket 连接"""
        await websocket.accept()
        
        if chat_room_id not in self.active_connections:
            self.active_connections[chat_room_id] = {}
        
        # 如果用户已在其他群聊，先断开
        if user_id in self.user_rooms:
            old_room = self.user_rooms[user_id]
            if old_room in self.active_connections and user_id in self.active_connections[old_room]:
                del self.active_connections[old_room][user_id]
        
        self.active_connections[chat_room_id][user_id] = websocket
        self.user_rooms[user_id] = chat_room_id
    
    def disconnect(self, chat_room_id: int, user_id: int):
        """断开 WebSocket 连接"""
        if chat_room_id in self.active_connections:
            if user_id in self.active_connections[chat_room_id]:
                del self.active_connections[chat_room_id][user_id]
            
            # 如果群聊没有连接了，清理
            if not self.active_connections[chat_room_id]:
                del self.active_connections[chat_room_id]
        
        if user_id in self.user_rooms:
            del self.user_rooms[user_id]
    
    async def broadcast_to_room(self, chat_room_id: int, message: dict, exclude_user_id: int = None):
        """向群聊广播消息"""
        if chat_room_id not in self.active_connections:
            return
        
        message_json = json.dumps(message, ensure_ascii=False, default=str)
        
        for user_id, connection in self.active_connections[chat_room_id].items():
            if exclude_user_id and user_id == exclude_user_id:
                continue
            try:
                await connection.send_text(message_json)
            except Exception:
                # 发送失败，标记为断开
                pass
    
    async def send_to_user(self, user_id: int, message: dict):
        """向指定用户发送消息"""
        if user_id not in self.user_rooms:
            return
        
        chat_room_id = self.user_rooms[user_id]
        if chat_room_id not in self.active_connections:
            return
        
        if user_id not in self.active_connections[chat_room_id]:
            return
        
        try:
            message_json = json.dumps(message, ensure_ascii=False, default=str)
            await self.active_connections[chat_room_id][user_id].send_text(message_json)
        except Exception:
            pass
    
    def get_online_users(self, chat_room_id: int) -> Set[int]:
        """获取群聊在线用户列表"""
        if chat_room_id not in self.active_connections:
            return set()
        return set(self.active_connections[chat_room_id].keys())


# 全局连接管理器
manager = ConnectionManager()


async def chat_websocket_endpoint(
    websocket: WebSocket,
    chat_room_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    """WebSocket 聊天端点"""
    
    # 验证用户身份
    try:
        user = await get_current_user_ws(token, db)
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # 验证群聊存在且活跃
    chat_room = db.query(ChatRoom).filter(
        ChatRoom.id == chat_room_id,
        ChatRoom.status == ChatRoomStatus.ACTIVE
    ).first()
    
    if not chat_room:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="群聊不存在")
        return
    
    # 验证用户是群聊成员
    member = db.query(ChatRoomMember).filter(
        ChatRoomMember.chat_room_id == chat_room_id,
        ChatRoomMember.user_id == user.id
    ).first()
    
    if not member:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="不是群聊成员")
        return
    
    # 检查是否被禁言
    if member.is_muted:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="您已被禁言")
        return
    
    # 建立连接
    await manager.connect(websocket, chat_room_id, user.id)
    
    try:
        # 更新最后活跃时间
        member.last_active_at = datetime.utcnow()
        db.commit()
        
        # 发送欢迎消息
        welcome_msg = {
            "type": "system",
            "content": f"欢迎 {user.username} 加入群聊",
            "timestamp": datetime.utcnow().isoformat()
        }
        await manager.broadcast_to_room(chat_room_id, welcome_msg)
        
        # 发送在线用户列表
        online_users = manager.get_online_users(chat_room_id)
        await websocket.send_text(json.dumps({
            "type": "online_users",
            "users": list(online_users),
            "count": len(online_users)
        }, ensure_ascii=False))
        
        # 广播用户加入通知
        join_notification = {
            "type": "user_joined",
            "user_id": user.id,
            "username": user.username,
            "timestamp": datetime.utcnow().isoformat()
        }
        await manager.broadcast_to_room(chat_room_id, join_notification, exclude_user_id=user.id)
        
        # 消息处理循环
        while True:
            try:
                # 接收消息
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                msg_type = message_data.get("type", "text")
                content = message_data.get("content", "").strip()
                
                if not content and msg_type == "text":
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "消息内容不能为空"
                    }, ensure_ascii=False))
                    continue
                
                # 保存消息到数据库
                chat_message = ChatMessage(
                    chat_room_id=chat_room_id,
                    user_id=user.id,
                    content=content,
                    message_type=msg_type
                )
                db.add(chat_message)
                db.commit()
                db.refresh(chat_message)
                
                # 构建消息响应
                message_response = {
                    "type": "message",
                    "message_id": chat_message.id,
                    "user_id": user.id,
                    "username": user.username,
                    "avatar_url": user.avatar_url,
                    "content": content,
                    "message_type": msg_type,
                    "timestamp": chat_message.created_at.isoformat(),
                    "is_own": False
                }
                
                # 广播给所有群聊成员
                await manager.broadcast_to_room(chat_room_id, message_response)
                
                # 更新最后活跃时间
                member.last_active_at = datetime.utcnow()
                db.commit()
                
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "消息格式错误"
                }, ensure_ascii=False))
            except Exception as e:
                print(f"处理消息时出错: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "消息处理失败"
                }, ensure_ascii=False))
                
    except WebSocketDisconnect:
        # 断开连接
        manager.disconnect(chat_room_id, user.id)
        
        # 广播用户离开通知
        leave_notification = {
            "type": "user_left",
            "user_id": user.id,
            "username": user.username,
            "timestamp": datetime.utcnow().isoformat()
        }
        await manager.broadcast_to_room(chat_room_id, leave_notification)
        
    except Exception as e:
        print(f"WebSocket 错误: {e}")
        manager.disconnect(chat_room_id, user.id)
