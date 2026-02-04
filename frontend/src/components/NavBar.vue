<template>
  <nav class="navbar">
    <div class="navbar-container">
      <div class="navbar-brand">
        <router-link to="/home">StudySync</router-link>
      </div>
      <div class="navbar-menu">
        <router-link to="/home" class="navbar-item">首页</router-link>
        <router-link to="/checkin" class="navbar-item">打卡</router-link>
        <router-link to="/groups" class="navbar-item">群组</router-link>
        <router-link to="/ai-report" class="navbar-item">AI报告</router-link>
      </div>
      <div class="navbar-user">
        <span class="user-name">{{ user?.username || '用户' }}</span>
        <el-dropdown @command="handleCommand">
          <el-button type="text">
            <el-avatar :size="32" :src="user?.avatar_url || ''">
              {{ user?.username?.charAt(0) || 'U' }}
            </el-avatar>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人中心</el-dropdown-item>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
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
    // 个人中心页面（如果需要）
    console.log('个人中心')
  }
}
</script>

<style scoped>
.navbar {
  background-color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.navbar-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 30px;
  height: 60px;
  max-width: 1200px;
  margin: 0 auto;
}

.navbar-brand {
  font-size: 20px;
  font-weight: bold;
}

.navbar-brand a {
  color: #667eea;
  text-decoration: none;
}

.navbar-menu {
  display: flex;
  gap: 30px;
}

.navbar-item {
  color: #333;
  text-decoration: none;
  font-size: 16px;
  padding: 8px 0;
  position: relative;
  transition: color 0.3s;
}

.navbar-item:hover {
  color: #667eea;
}

.navbar-item.router-link-active {
  color: #667eea;
  font-weight: 500;
}

.navbar-item.router-link-active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: #667eea;
}

.navbar-user {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-name {
  font-size: 14px;
  color: #666;
}

@media (max-width: 768px) {
  .navbar-container {
    padding: 0 20px;
  }
  
  .navbar-menu {
    gap: 20px;
  }
  
  .navbar-item {
    font-size: 14px;
  }
  
  .user-name {
    display: none;
  }
}
</style>