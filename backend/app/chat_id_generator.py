"""
群聊ID生成器

提供唯一、安全、易记的群聊ID生成算法
"""
import secrets
import string
from typing import Optional
from sqlalchemy.orm import Session


class ChatIdGenerator:
    """群聊ID生成器"""
    
    # 字符集：排除易混淆字符（0, O, 1, I, l）
    CHARACTERS = string.ascii_uppercase.replace('O', '') + string.digits.replace('0', '').replace('1', '')
    
    # ID长度配置
    MIN_LENGTH = 6
    MAX_LENGTH = 8
    
    @classmethod
    def generate(cls, length: int = 6) -> str:
        """
        生成随机群聊ID
        
        Args:
            length: ID长度，默认6位
            
        Returns:
            str: 生成的群聊ID
        """
        if length < cls.MIN_LENGTH or length > cls.MAX_LENGTH:
            length = cls.MIN_LENGTH
            
        # 生成随机ID
        chat_id = ''.join(secrets.choice(cls.CHARACTERS) for _ in range(length))
        return chat_id
    
    @classmethod
    def generate_unique(cls, db: Session, length: int = 6, max_attempts: int = 10) -> Optional[str]:
        """
        生成唯一的群聊ID
        
        Args:
            db: 数据库会话
            length: ID长度
            max_attempts: 最大尝试次数
            
        Returns:
            str: 唯一的群聊ID，失败返回None
        """
        for attempt in range(max_attempts):
            chat_id = cls.generate(length)
            
            # 检查是否已存在
            # 注意：这里需要导入ChatRoom模型，为了避免循环导入，在函数内部导入
            from app.chat_models import ChatRoom
            existing = db.query(ChatRoom).filter(ChatRoom.chat_id == chat_id).first()
            if not existing:
                return chat_id
                
        # 如果6位ID生成失败，尝试7位
        if length < cls.MAX_LENGTH:
            return cls.generate_unique(db, length + 1, max_attempts)
            
        return None
    
    @classmethod
    def is_valid(cls, chat_id: str) -> bool:
        """
        验证群聊ID格式是否有效
        
        Args:
            chat_id: 要验证的群聊ID
            
        Returns:
            bool: 是否有效
        """
        if not chat_id:
            return False
            
        # 检查长度
        if len(chat_id) < cls.MIN_LENGTH or len(chat_id) > cls.MAX_LENGTH:
            return False
            
        # 检查字符是否合法
        for char in chat_id:
            if char not in cls.CHARACTERS:
                return False
                
        return True
    
    @classmethod
    def format_for_display(cls, chat_id: str) -> str:
        """
        格式化群聊ID用于显示（添加分隔符提高可读性）
        
        Args:
            chat_id: 原始群聊ID
            
        Returns:
            str: 格式化后的群聊ID
        """
        if len(chat_id) <= 4:
            return chat_id
            
        # 每3位添加一个分隔符
        formatted = ""
        for i, char in enumerate(chat_id):
            if i > 0 and i % 3 == 0:
                formatted += "-"
            formatted += char
            
        return formatted