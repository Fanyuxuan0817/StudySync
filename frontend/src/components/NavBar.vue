<template>
  <nav class="navbar">
    <div class="navbar-container">
      <div class="navbar-brand">
        <router-link to="/home" class="brand-link">
          <span class="brand-icon">📚</span>
          <span class="brand-text">StudySync</span>
        </router-link>
      </div>
      
      <div class="navbar-menu">
        <router-link to="/home" class="navbar-item" active-class="active">
          <span class="item-icon">🏠</span>
          <span class="item-text">首页</span>
        </router-link>
        <router-link to="/checkin" class="navbar-item" active-class="active">
          <span class="item-icon">✏️</span>
          <span class="item-text">打卡</span>
        </router-link>
        <router-link to="/chat-rooms" class="navbar-item" active-class="active">
          <span class="item-icon">💬</span>
          <span class="item-text">群聊中心</span>
        </router-link>
      </div>
      
      <div class="navbar-user">
        <span class="user-name">{{ user?.username || '用户' }}</span>
        <el-dropdown @command="handleCommand" trigger="click" class="user-dropdown">
          <div class="avatar-wrapper">
            <el-avatar 
              :size="40" 
              :src="user?.avatar_url || ''"
              class="user-avatar"
            >
              {{ user?.username?.charAt(0) || 'U' }}
            </el-avatar>
            <div class="avatar-ring"></div>
          </div>
          <template #dropdown>
            <el-dropdown-menu class="user-menu">
              <el-dropdown-item command="profile">
                <span class="menu-icon">👤</span>
                个人中心
              </el-dropdown-item>
              <el-dropdown-item command="logout" divided>
                <span class="menu-icon">🚪</span>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/modules/auth'

const router = useRouter()
const authStore = useAuthStore()

const user = computed(() => authStore.user)

const handleCommand = async (command) => {
  if (command === 'logout') {
    await authStore.logout()
    router.push('/auth/login')
  } else if (command === 'profile') {
    console.log('个人中心')
  }
}
</script>

<style scoped>
.navbar {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
  position: sticky;
  top: 0;
  z-index: 1000;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.04);
}

.navbar-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 32px;
  height: 72px;
  max-width: 1400px;
  margin: 0 auto;
}

/* ===== 品牌区域 ===== */
.navbar-brand {
  display: flex;
  align-items: center;
}

.brand-link {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.brand-link:hover {
  transform: scale(1.02);
}

.brand-icon {
  font-size: 28px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.brand-text {
  font-size: 22px;
  font-weight: 700;
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 50%, #FFB347 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
}

/* ===== 导航菜单 ===== */
.navbar-menu {
  display: flex;
  gap: 8px;
  align-items: center;
}

.navbar-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 16px;
  text-decoration: none;
  color: #636E72;
  font-weight: 500;
  font-size: 15px;
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  position: relative;
  overflow: hidden;
}

.navbar-item::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(255, 142, 142, 0.1) 100%);
  border-radius: 16px;
  opacity: 0;
  transform: scale(0.8);
  transition: all 0.3s ease;
}

.navbar-item:hover {
  color: #FF6B6B;
  transform: translateY(-2px);
}

.navbar-item:hover::before {
  opacity: 1;
  transform: scale(1);
}

.navbar-item.active {
  color: #FF6B6B;
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(255, 142, 142, 0.1) 100%);
}

.navbar-item.active::before {
  opacity: 1;
  transform: scale(1);
}

.item-icon {
  font-size: 18px;
  transition: transform 0.3s ease;
}

.navbar-item:hover .item-icon {
  transform: scale(1.1) rotate(-5deg);
}

.item-text {
  position: relative;
  z-index: 1;
}

/* ===== 用户区域 ===== */
.navbar-user {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-name {
  font-size: 15px;
  font-weight: 500;
  color: #636E72;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.avatar-wrapper {
  position: relative;
  cursor: pointer;
  transition: transform 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.avatar-wrapper:hover {
  transform: scale(1.05);
}

.user-avatar {
  border: 3px solid white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
  color: white;
  font-weight: 600;
  font-size: 16px;
}

.avatar-ring {
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FF6B6B 0%, #FFD93D 50%, #6BCB77 100%);
  z-index: -1;
  opacity: 0;
  transform: scale(0.9);
  transition: all 0.3s ease;
}

.avatar-wrapper:hover .avatar-ring {
  opacity: 1;
  transform: scale(1);
}

/* ===== 下拉菜单 ===== */
.user-dropdown :deep(.el-dropdown-menu) {
  border-radius: 16px;
  padding: 8px;
  min-width: 160px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
}

.user-dropdown :deep(.el-dropdown-menu__item) {
  border-radius: 12px;
  padding: 12px 16px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.2s ease;
}

.user-dropdown :deep(.el-dropdown-menu__item:hover) {
  background: rgba(255, 107, 107, 0.1);
  color: #FF6B6B;
}

.menu-icon {
  font-size: 16px;
}

/* ===== 响应式设计 ===== */
@media (max-width: 768px) {
  .navbar-container {
    padding: 0 16px;
    height: 64px;
  }
  
  .brand-text {
    font-size: 18px;
  }
  
  .navbar-menu {
    gap: 4px;
  }
  
  .navbar-item {
    padding: 8px 12px;
    border-radius: 12px;
  }
  
  .item-text {
    display: none;
  }
  
  .item-icon {
    font-size: 22px;
  }
  
  .user-name {
    display: none;
  }
}

@media (max-width: 480px) {
  .navbar-container {
    padding: 0 12px;
  }
  
  .brand-icon {
    font-size: 24px;
  }
  
  .brand-text {
    display: none;
  }
  
  .navbar-item {
    padding: 8px;
  }
}
</style>
