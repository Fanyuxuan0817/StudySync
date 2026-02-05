<template>
  <div class="chat-session-container">
    <!-- 左侧群聊列表 -->
    <div class="chat-list-sidebar" :class="{ 'collapsed': isMobile && !showChatList }">
      <!-- 搜索栏 -->
      <div class="sidebar-header">
        <el-input
          v-model="searchQuery"
          placeholder="搜索群聊"
          clearable
          class="search-input"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" circle size="small" @click="goToSearch" class="add-btn">
          <el-icon><Plus /></el-icon>
        </el-button>
      </div>

      <!-- 群聊列表 -->
      <div class="chat-list-content">
        <div v-if="loadingRooms" class="loading-state">
          <el-skeleton :rows="5" animated />
        </div>

        <div v-else-if="filteredChatRooms.length === 0" class="empty-state">
          <el-empty description="暂无群聊" />
          <el-button type="primary" @click="goToSearch">去发现群聊</el-button>
        </div>

        <div v-else class="chat-room-list">
          <div
            v-for="room in filteredChatRooms"
            :key="room.room_id"
            class="chat-room-item"
            :class="{ 
              'active': currentRoomId === room.room_id, 
              'unread': unreadCounts[room.room_id] > 0 
            }"
            @click="selectChatRoom(room)"
          >
            <el-avatar :size="44" :src="room.avatar_url" class="room-avatar">
              {{ room.name?.charAt(0) || '群' }}
            </el-avatar>
            <div class="room-info">
              <div class="room-name-row">
                <span class="room-name">{{ room.name }}</span>
                <span class="message-time">{{ formatShortTime(lastMessages[room.room_id]?.timestamp) }}</span>
              </div>
              <div class="room-meta">
                <span class="last-message">{{ lastMessages[room.room_id]?.content || '暂无消息' }}</span>
                <span v-if="unreadCounts[room.room_id]" class="unread-badge">
                  {{ unreadCounts[room.room_id] > 99 ? '99+' : unreadCounts[room.room_id] }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧聊天区域 -->
    <div class="chat-main-area" :class="{ 'expanded': isMobile && !showChatList }">
      <!-- 空状态 - 未选择群聊 -->
      <div v-if="!currentRoom" class="no-chat-selected">
        <div class="empty-content">
          <el-icon class="empty-icon"><ChatDotRound /></el-icon>
          <p>选择一个群聊开始对话</p>
          <el-button type="primary" @click="goToSearch">去发现群聊</el-button>
        </div>
      </div>

      <!-- 聊天界面 -->
      <div v-else class="chat-container">
        <!-- 顶部导航栏 -->
        <div class="chat-header">
          <div class="header-left">
            <el-button v-if="isMobile" type="text" @click="showChatList = true" class="back-btn">
              <el-icon><ArrowLeft /></el-icon>
            </el-button>
            <div class="room-title">
              <h3 class="page-title">{{ currentRoom.name }}</h3>
              <span class="member-count">
                {{ currentRoom.member_count || 0 }} 人
              </span>
            </div>
          </div>
          <div class="header-actions">
            <el-button type="text" @click="refreshMessages" :loading="refreshing">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button type="text" @click="showCheckinStats">
              <el-icon><DataAnalysis /></el-icon>
              打卡
            </el-button>
            <el-button type="text" @click="showRoomDetail">
              <el-icon><InfoFilled /></el-icon>
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
              <div v-if="currentRoomMessages.length === 0 && !loading" class="no-messages">
                <el-empty description="暂无消息，发送第一条消息吧！" />
              </div>

              <div
                v-for="message in currentRoomMessages"
                :key="message.message_id || message.id"
                class="message-item"
                :class="{ 
                  'own-message': message.is_own || message.isOwn,
                  'system-message': message.message_type === 'system'
                }"
              >
                <!-- 系统消息 -->
                <template v-if="message.message_type === 'system'">
                  <div class="system-content">
                    <span class="system-text">{{ message.content }}</span>
                    <span class="system-time">{{ formatTime(message.timestamp) }}</span>
                  </div>
                </template>

                <!-- 普通消息 -->
                <template v-else>
                  <el-avatar
                    :size="36"
                    :src="message.avatar_url"
                    class="message-avatar"
                  >
                    {{ message.username?.charAt(0) || message.sender?.charAt(0) || '用' }}
                  </el-avatar>
                  <div class="message-content-wrapper">
                    <div class="message-header">
                      <span class="message-sender">{{ message.username || message.sender }}</span>
                      <span class="message-time">{{ formatTime(message.timestamp) }}</span>
                    </div>
                    <div class="message-bubble" :class="{ 'own': message.is_own || message.isOwn }">
                      <div class="message-text">{{ message.content }}</div>
                    </div>
                  </div>
                </template>
              </div>
            </div>
          </div>

          <!-- 消息输入区域 -->
          <div class="message-input-section">
            <div class="input-area">
              <el-input
                v-model="newMessage"
                type="textarea"
                :rows="2"
                placeholder="输入消息..."
                resize="none"
                @keyup.enter.prevent="handleSend"
                :disabled="!currentRoom || sending"
              />
            </div>

            <div class="input-actions">
              <span class="hint-text">按 Enter 发送消息</span>
              <el-button
                type="primary"
                @click="handleSend"
                :disabled="!newMessage.trim() || !currentRoom"
                :loading="sending"
              >
                发送
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 群聊详情弹窗 -->
    <el-dialog
      v-model="roomDetailVisible"
      title="群聊详情"
      width="400px"
    >
      <div v-if="currentRoom" class="room-detail">
        <div class="detail-header">
          <el-avatar :size="64" :src="currentRoom.avatar_url">
            {{ currentRoom.name?.charAt(0) || '群' }}
          </el-avatar>
          <h4>{{ currentRoom.name }}</h4>
          <p class="room-id">ID: {{ currentRoom.chat_id }}</p>
        </div>
        <div class="detail-info">
          <p><strong>描述:</strong> {{ currentRoom.description || '暂无描述' }}</p>
          <p><strong>成员数:</strong> {{ currentRoom.member_count || 0 }} / {{ currentRoom.max_members || 500 }}</p>
          <p><strong>创建时间:</strong> {{ formatTime(currentRoom.created_at) }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../store/modules/auth'
import api from '../api'
import { ElMessage } from 'element-plus'
import {
  Plus, ArrowLeft, InfoFilled, Refresh,
  DataAnalysis, Close, ChatDotRound, Search
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 响应式状态
const isMobile = ref(window.innerWidth <= 768)
const showChatList = ref(true)

// 搜索
const searchQuery = ref('')

// 群聊列表
const chatRooms = ref([])
const loadingRooms = ref(false)
const currentRoomId = ref(null)
const currentRoom = computed(() =>
  chatRooms.value.find(r => r.room_id === currentRoomId.value)
)

// 消息相关
const messages = ref({}) // key 为 room_id
const newMessage = ref('')
const loading = ref(false)
const sending = ref(false)
const refreshing = ref(false)
const messagesContainer = ref(null)

// 未读消息
const unreadCounts = ref({})
const lastMessages = ref({})

// UI 状态
const roomDetailVisible = ref(false)

// 打卡相关
const showCheckinPanel = ref(false)
const checkinDate = ref(new Date())
const activeTab = ref('checked_in')
const groupCheckins = ref({
  checked_in: [],
  not_checked_in: []
})

// 计算属性
const filteredChatRooms = computed(() => {
  if (!searchQuery.value) return chatRooms.value
  return chatRooms.value.filter(room =>
    room.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const currentRoomMessages = computed(() => {
  return messages.value[currentRoomId.value] || []
})

// 方法
const handleResize = () => {
  isMobile.value = window.innerWidth <= 768
}

const goToSearch = () => {
  router.push('/chat-rooms/search')
}

const fetchChatRooms = async () => {
  loadingRooms.value = true
  try {
    const response = await api.chatRooms.getChatRooms()
    const { created, joined } = response.data.data

    // 合并创建的群聊和加入的群聊
    const allRooms = [
      ...(created || []).map(r => ({ ...r, is_creator: true })),
      ...(joined || []).map(r => ({ ...r, is_creator: false }))
    ]

    chatRooms.value = allRooms

    // 检查路由参数中是否有指定的 room_id
    const targetRoomId = route.query.room_id
    if (targetRoomId) {
      // 尝试找到对应的群聊
      const targetRoom = allRooms.find(r => r.room_id === parseInt(targetRoomId))
      if (targetRoom) {
        selectChatRoom(targetRoom)
      } else if (allRooms.length > 0 && !currentRoomId.value) {
        // 如果找不到指定的群聊，默认选中第一个
        selectChatRoom(allRooms[0])
        ElMessage.warning('未找到指定的群聊')
      }
    } else if (allRooms.length > 0 && !currentRoomId.value) {
      // 如果没有指定 room_id，默认选中第一个
      selectChatRoom(allRooms[0])
    }
  } catch (error) {
    console.error('获取群聊列表失败:', error)
    ElMessage.error('获取群聊列表失败')
  } finally {
    loadingRooms.value = false
  }
}

const selectChatRoom = (room) => {
  currentRoomId.value = room.room_id

  // 移动端隐藏列表
  if (isMobile.value) {
    showChatList.value = false
  }

  // 清除未读计数
  unreadCounts.value[room.room_id] = 0

  // 初始化该房间的消息数组
  if (!messages.value[room.room_id]) {
    messages.value[room.room_id] = []
  }

  // 加载消息历史
  loadMessages()
}

const loadMessages = async () => {
  if (!currentRoomId.value) return

  loading.value = true
  try {
    const response = await api.chatRooms.getMessages(currentRoomId.value, {
      limit: 100
    })

    const { messages: newMessages } = response.data.data

    // 存储消息
    messages.value[currentRoomId.value] = newMessages.length > 0 ? newMessages : []

    // 滚动到底部
    nextTick(() => {
      scrollToBottom()
    })
  } catch (error) {
    console.error('加载消息失败:', error)
    ElMessage.error('加载消息失败')
  } finally {
    loading.value = false
  }
}

const refreshMessages = async () => {
  if (!currentRoomId.value) return

  refreshing.value = true
  try {
    const response = await api.chatRooms.getMessages(currentRoomId.value, {
      limit: 100
    })

    const { messages: newMessages } = response.data.data

    // 检查是否有新消息
    const currentMessages = messages.value[currentRoomId.value] || []
    const currentCount = currentMessages.length
    const newCount = newMessages.length

    // 更新消息
    messages.value[currentRoomId.value] = newMessages

    // 如果有新消息，滚动到底部并提示
    if (newCount > currentCount) {
      nextTick(() => {
        scrollToBottom()
      })
      ElMessage.success(`收到 ${newCount - currentCount} 条新消息`)
    } else {
      ElMessage.info('已是最新消息')
    }
  } catch (error) {
    console.error('刷新消息失败:', error)
    ElMessage.error('刷新消息失败')
  } finally {
    refreshing.value = false
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const handleSend = async () => {
  const content = newMessage.value.trim()
  if (!content || !currentRoomId.value) return

  sending.value = true

  try {
    // 使用 HTTP 发送消息
    const response = await api.chatRooms.sendMessage(currentRoomId.value, content)
    const sentMessage = response.data.data

    // 添加到消息列表
    if (!messages.value[currentRoomId.value]) {
      messages.value[currentRoomId.value] = []
    }
    messages.value[currentRoomId.value].push({
      ...sentMessage,
      is_own: true
    })

    // 更新最后消息
    lastMessages.value[currentRoomId.value] = {
      content: content,
      timestamp: new Date().toISOString()
    }

    // 清空输入框
    newMessage.value = ''

    // 滚动到底部
    nextTick(() => {
      scrollToBottom()
    })

    ElMessage.success('发送成功')
  } catch (error) {
    console.error('发送消息失败:', error)
    ElMessage.error('发送消息失败')
  } finally {
    sending.value = false
  }
}

const showRoomDetail = () => {
  if (!currentRoom.value) {
    ElMessage.warning('请先选择一个群聊')
    return
  }
  roomDetailVisible.value = true
}

const showCheckinStats = () => {
  showCheckinPanel.value = true
  fetchGroupCheckins()
}

const toggleCheckinPanel = () => {
  showCheckinPanel.value = !showCheckinPanel.value
}

const fetchGroupCheckins = async () => {
  if (!currentRoom.value?.group_info?.group_id) return

  try {
    const response = await api.groups.getGroupCheckins(currentRoom.value.group_info.group_id, {
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

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const isToday = date.toDateString() === now.toDateString()

  if (isToday) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }

  const isThisYear = date.getFullYear() === now.getFullYear()
  if (isThisYear) {
    return date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
  }

  return date.toLocaleString('zh-CN')
}

const formatShortTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date

  // 今天
  if (date.toDateString() === now.toDateString()) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }

  // 昨天
  const yesterday = new Date(now)
  yesterday.setDate(yesterday.getDate() - 1)
  if (date.toDateString() === yesterday.toDateString()) {
    return '昨天'
  }

  // 本周
  if (diff < 7 * 24 * 60 * 60 * 1000) {
    const days = ['日', '一', '二', '三', '四', '五', '六']
    return `周${days[date.getDay()]}`
  }

  // 更早
  return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}

// 生命周期
onMounted(() => {
  window.addEventListener('resize', handleResize)
  fetchChatRooms()
})
</script>

<style scoped>
.chat-session-container {
  display: flex;
  height: 100vh;
  background-color: #f5f5f5;
}

/* 左侧群聊列表 */
.chat-list-sidebar {
  width: 280px;
  background-color: white;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px;
  border-bottom: 1px solid #e4e7ed;
}

.search-input {
  flex: 1;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 20px;
}

.add-btn {
  flex-shrink: 0;
}

.chat-list-content {
  flex: 1;
  overflow-y: auto;
}

.loading-state {
  padding: 20px;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
}

.chat-room-list {
  padding: 8px 0;
}

.chat-room-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.chat-room-item:hover {
  background-color: #f5f7fa;
}

.chat-room-item.active {
  background-color: #ecf5ff;
  border-left-color: #409eff;
}

.chat-room-item.unread {
  background-color: #fff8e6;
}

.room-avatar {
  margin-right: 12px;
  background-color: #409eff;
  color: white;
  font-weight: bold;
  flex-shrink: 0;
}

.room-info {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.room-name-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.room-name {
  font-weight: 500;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
}

.message-time {
  font-size: 11px;
  color: #999;
  flex-shrink: 0;
  margin-left: 8px;
}

.room-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #999;
}

.last-message {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: 8px;
}

.unread-badge {
  background-color: #f56c6c;
  color: white;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
  flex-shrink: 0;
}

/* 右侧聊天区域 */
.chat-main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

.no-chat-selected {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: white;
}

.empty-content {
  text-align: center;
  color: #999;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  color: #dcdfe6;
}

.empty-content p {
  margin-bottom: 20px;
  font-size: 14px;
}

/* 聊天容器 */
.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background-color: white;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  flex: 1;
}

.back-btn {
  margin-right: 10px;
}

.room-title {
  flex: 1;
}

.page-title {
  margin: 0;
  font-size: 16px;
  color: #333;
  font-weight: 500;
}

.member-count {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #999;
  margin-top: 2px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

/* 聊天内容区 */
.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 打卡区域 */
.checkin-section {
  padding: 15px 20px;
  background-color: white;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
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
  margin-bottom: 15px;
}

.checkin-tabs {
  min-height: 200px;
}

.checkin-list {
  padding: 10px 0;
}

.checkin-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
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
  font-size: 14px;
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
  padding: 30px 0;
}

/* 消息区域 */
.messages-section {
  flex: 1;
  overflow: hidden;
  background-color: #f5f5f5;
  position: relative;
}

.messages-container {
  height: 100%;
  overflow-y: auto;
  padding: 20px;
}

.no-messages {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.message-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 16px;
  gap: 12px;
}

.message-item.own-message {
  flex-direction: row-reverse;
}

.message-item.system-message {
  justify-content: center;
}

.system-content {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background-color: #e4e7ed;
  border-radius: 12px;
  font-size: 12px;
  color: #666;
}

.system-time {
  color: #999;
}

.message-avatar {
  background-color: #409eff;
  color: white;
  font-weight: bold;
  flex-shrink: 0;
}

.message-content-wrapper {
  max-width: 60%;
  display: flex;
  flex-direction: column;
}

.own-message .message-content-wrapper {
  align-items: flex-end;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.own-message .message-header {
  justify-content: flex-end;
}

.message-sender {
  font-size: 13px;
  color: #666;
  font-weight: 500;
}

.message-time {
  font-size: 11px;
  color: #999;
}

.message-bubble {
  display: inline-block;
  padding: 10px 14px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  word-break: break-word;
}

.message-bubble.own {
  background-color: #95ec69;
}

.message-text {
  font-size: 14px;
  line-height: 1.5;
  color: #333;
}

.message-bubble.own .message-text {
  color: #000;
}

/* 输入区域 */
.message-input-section {
  padding: 12px 20px;
  border-top: 1px solid #e4e7ed;
  background-color: white;
  flex-shrink: 0;
}

.input-area {
  margin-bottom: 10px;
}

.input-area :deep(.el-textarea__inner) {
  resize: none;
  border-radius: 8px;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.hint-text {
  font-size: 12px;
  color: #999;
}

/* 群聊详情弹窗 */
.room-detail {
  padding: 20px;
}

.detail-header {
  text-align: center;
  margin-bottom: 20px;
}

.detail-header h4 {
  margin: 12px 0 4px;
  font-size: 18px;
}

.room-id {
  color: #999;
  font-size: 12px;
}

.detail-info p {
  margin: 8px 0;
  color: #666;
  font-size: 14px;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .chat-list-sidebar {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 100;
  }

  .chat-list-sidebar.collapsed {
    display: none;
  }

  .chat-main-area {
    width: 100%;
  }

  .chat-main-area.expanded {
    display: flex;
  }

  .message-content-wrapper {
    max-width: 75%;
  }

  .messages-container {
    padding: 15px;
  }

  .message-input-section {
    padding: 10px 15px;
  }

  .checkin-section {
    padding: 10px 15px;
  }

  .checkin-card {
    margin: 0;
  }
}
</style>
