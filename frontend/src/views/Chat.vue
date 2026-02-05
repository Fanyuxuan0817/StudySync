<template>
  <div class="chat-container">
    <!-- 顶部导航栏 -->
    <div class="chat-header">
      <el-button type="text" @click="goBack" class="back-button">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
      <h1 class="page-title">{{ groupName }} - 群聊</h1>
      <div class="header-actions">
        <el-button type="text" @click="showCheckinStats">
          <el-icon><DataAnalysis /></el-icon>
          打卡统计
        </el-button>
      </div>
    </div>

    <!-- 聊天内容区域 -->
    <div class="chat-content">
      <!-- 打卡情况展示区域 -->
      <div class="checkin-section" v-if="showCheckinPanel">
        <el-card class="checkin-card">
          <template #header>
            <div class="card-header">
              <span>今日打卡情况</span>
              <el-button type="text" @click="toggleCheckinPanel">
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
          </template>
          
          <el-form :inline="true" class="date-form">
            <el-form-item label="选择日期">
              <el-date-picker
                v-model="checkinDate"
                type="date"
                placeholder="选择日期"
                @change="fetchGroupCheckins"
                size="small"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="fetchGroupCheckins" size="small">
                查询
              </el-button>
            </el-form-item>
          </el-form>

          <div v-if="groupCheckins.checked_in.length > 0 || groupCheckins.not_checked_in.length > 0">
            <el-tabs v-model="activeTab" class="checkin-tabs">
              <el-tab-pane label="已打卡" name="checked_in">
                <div class="checkin-list">
                  <div 
                    v-for="member in groupCheckins.checked_in" 
                    :key="member.user_id"
                    class="checkin-item"
                  >
                    <el-avatar :size="32" class="member-avatar">
                      {{ member.username?.charAt(0) || '用' }}
                    </el-avatar>
                    <div class="checkin-info">
                      <div class="member-name">{{ member.username }}</div>
                      <div class="checkin-details">
                        <el-tag size="small" type="success">
                          学习 {{ member.hours }} 小时
                        </el-tag>
                        <span class="checkin-time">{{ formatTime(member.checkin_time) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </el-tab-pane>
              <el-tab-pane label="未打卡" name="not_checked_in">
                <div class="checkin-list">
                  <div 
                    v-for="member in groupCheckins.not_checked_in" 
                    :key="member.user_id"
                    class="checkin-item not-checked"
                  >
                    <el-avatar :size="32" class="member-avatar">
                      {{ member.username?.charAt(0) || '用' }}
                    </el-avatar>
                    <div class="checkin-info">
                      <div class="member-name">{{ member.username }}</div>
                      <el-tag size="small" type="info">未打卡</el-tag>
                    </div>
                  </div>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
          <div v-else class="no-checkins">
            <el-empty description="暂无打卡数据" />
          </div>
        </el-card>
      </div>

      <!-- 消息列表 -->
      <div class="messages-section">
        <div class="messages-container" ref="messagesContainer">
          <div v-if="messages.length === 0" class="no-messages">
            <el-empty description="暂无消息" />
          </div>
          <div 
            v-for="message in messages" 
            :key="message.id"
            class="message-item"
            :class="{ 'own-message': message.isOwn }"
          >
            <div class="message-avatar">
              <el-avatar :size="36">
                {{ message.sender?.charAt(0) || '用' }}
              </el-avatar>
            </div>
            <div class="message-content">
              <div class="message-header">
                <span class="message-sender">{{ message.sender }}</span>
                <span class="message-time">{{ formatTime(message.timestamp) }}</span>
              </div>
              <div class="message-body">
                {{ message.content }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 消息输入区域 -->
      <div class="message-input-section">
        <el-input
          v-model="newMessage"
          type="textarea"
          placeholder="输入消息..."
          :rows="2"
          @keyup.enter.prevent="sendMessage"
          class="message-input"
        />
        <div class="input-actions">
          <el-button type="primary" @click="sendMessage" :disabled="!newMessage.trim()">
            发送
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft, DataAnalysis, Close } from '@element-plus/icons-vue'
import { useAuthStore } from '../store/modules/auth'
import api from '../api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 状态变量
const groupId = ref(route.params.id)
const groupName = ref(route.query.name || '群聊')
const showCheckinPanel = ref(true) // 默认显示打卡面板
const checkinDate = ref(new Date())
const activeTab = ref('checked_in')
const newMessage = ref('')
const messagesContainer = ref(null)

// 数据
const groupCheckins = ref({
  checked_in: [],
  not_checked_in: []
})

const messages = ref([
  // 模拟消息数据
  {
    id: 1,
    sender: '系统',
    content: '欢迎来到群聊！在这里可以查看群组成员的打卡情况，也可以发送消息互相鼓励学习。',
    timestamp: new Date(),
    isOwn: false
  }
])

// 方法
const goBack = () => {
  router.back()
}

const showCheckinStats = () => {
  showCheckinPanel.value = true
}

const toggleCheckinPanel = () => {
  showCheckinPanel.value = !showCheckinPanel.value
}

const fetchGroupCheckins = async () => {
  if (!groupId.value) return
  
  try {
    const response = await api.groups.getGroupCheckins(groupId.value, {
      date: checkinDate.value
    })
    groupCheckins.value = {
      checked_in: response.data.data.checked_in || [],
      not_checked_in: response.data.data.not_checked_in || []
    }
  } catch (error) {
    console.error('获取群组打卡情况失败:', error)
    ElMessage.error('获取群组打卡情况失败')
  }
}

const sendMessage = () => {
  if (!newMessage.value.trim()) return
  
  const message = {
    id: Date.now(),
    sender: authStore.user?.username || '我',
    content: newMessage.value.trim(),
    timestamp: new Date(),
    isOwn: true
  }
  
  messages.value.push(message)
  newMessage.value = ''
  
  // 滚动到底部
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const formatTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 生命周期
onMounted(async () => {
  // 确保用户已登录
  if (!authStore.isAuthenticated) {
    router.push('/auth/login')
    return
  }
  
  // 获取用户信息
  if (!authStore.user) {
    await authStore.fetchUserInfo()
  }
  
  // 获取群组打卡情况
  await fetchGroupCheckins()
})
</script>

<style scoped>
.chat-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f5f5;
}

.chat-header {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  background-color: white;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.back-button {
  margin-right: 15px;
}

.page-title {
  flex: 1;
  font-size: 20px;
  color: #333;
  margin: 0;
}

.header-actions {
  margin-left: 20px;
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.checkin-section {
  padding: 20px;
  background-color: white;
  border-bottom: 1px solid #e4e7ed;
}

.checkin-card {
  margin: 0 auto;
  max-width: 800px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.date-form {
  margin-bottom: 20px;
}

.checkin-tabs {
  min-height: 300px;
}

.checkin-list {
  padding: 10px 0;
}

.checkin-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  background-color: #f9f9f9;
  transition: background-color 0.2s;
}

.checkin-item:hover {
  background-color: #f0f0f0;
}

.checkin-item.not-checked {
  opacity: 0.7;
}

.member-avatar {
  margin-right: 12px;
  background-color: #409eff;
}

.checkin-info {
  flex: 1;
}

.member-name {
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.checkin-details {
  display: flex;
  align-items: center;
  gap: 10px;
}

.checkin-time {
  font-size: 12px;
  color: #999;
}

.no-checkins {
  text-align: center;
  padding: 40px 0;
}

.messages-section {
  flex: 1;
  overflow: hidden;
  background-color: white;
}

.messages-container {
  height: 100%;
  overflow-y: auto;
  padding: 20px;
}

.no-messages {
  text-align: center;
  padding: 60px 0;
}

.message-item {
  display: flex;
  margin-bottom: 20px;
  align-items: flex-start;
}

.own-message {
  flex-direction: row-reverse;
}

.own-message .message-content {
  background-color: #409eff;
  color: white;
}

.message-avatar {
  margin: 0 12px;
}

.message-content {
  max-width: 60%;
  background-color: #f0f0f0;
  border-radius: 12px;
  padding: 12px 16px;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.message-sender {
  font-size: 14px;
  font-weight: 500;
}

.message-time {
  font-size: 12px;
  opacity: 0.7;
}

.message-body {
  font-size: 14px;
  line-height: 1.4;
}

.message-input-section {
  padding: 20px;
  background-color: white;
  border-top: 1px solid #e4e7ed;
}

.message-input {
  margin-bottom: 10px;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .chat-header {
    padding: 12px 15px;
  }
  
  .page-title {
    font-size: 18px;
  }
  
  .checkin-section {
    padding: 15px;
  }
  
  .checkin-card {
    margin: 0;
  }
  
  .message-content {
    max-width: 80%;
  }
  
  .message-input-section {
    padding: 15px;
  }
}
</style>