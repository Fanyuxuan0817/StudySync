<template>
  <div class="chat-session-container">
    <!-- 左侧群聊列表 -->
    <div class="chat-list-section" :class="{ 'collapsed': isMobile && !showChatList }">
      <div class="chat-list-header">
        <h3>群聊列表</h3>
        <el-button type="primary" size="small" @click="goToSearch">
          <el-icon><Plus /></el-icon>
        </el-button>
      </div>
      
      <div class="chat-list-content">
        <div v-if="loadingRooms" class="loading-state">
          <el-skeleton :rows="5" animated />
        </div>
        
        <div v-else-if="chatRooms.length === 0" class="empty-state">
          <el-empty description="暂无群聊" />
          <el-button type="primary" @click="goToSearch">去发现群聊</el-button>
        </div>
        
        <div v-else class="chat-room-list">
          <div
            v-for="room in chatRooms"
            :key="room.room_id"
            class="chat-room-item"
            :class="{ 'active': currentRoomId === room.room_id, 'unread': unreadCounts[room.room_id] > 0 }"
            @click="selectChatRoom(room)"
          >
            <el-avatar :size="40" :src="room.avatar_url" class="room-avatar">
              {{ room.name?.charAt(0) || '群' }}
            </el-avatar>
            <div class="room-info">
              <div class="room-name-row">
                <span class="room-name">{{ room.name }}</span>
                <span v-if="unreadCounts[room.room_id]" class="unread-badge">
                  {{ unreadCounts[room.room_id] > 99 ? '99+' : unreadCounts[room.room_id] }}
                </span>
              </div>
              <div class="room-meta">
                <span class="last-message">{{ lastMessages[room.room_id]?.content || '暂无消息' }}</span>
                <span class="message-time">{{ formatShortTime(lastMessages[room.room_id]?.timestamp) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧聊天区域 -->
    <div class="chat-area-section" :class="{ 'expanded': isMobile && !showChatList }">
      <!-- 聊天头部 -->
      <div class="chat-header">
        <div class="header-left">
          <el-button v-if="isMobile" type="text" @click="showChatList = true" class="back-btn">
            <el-icon><ArrowLeft /></el-icon>
          </el-button>
          <div class="room-title">
            <h3>{{ currentRoom?.name || '选择一个群聊' }}</h3>
            <span class="online-status">
              <el-icon><CircleCheck /></el-icon>
              {{ onlineUsers.length }} 人在线
            </span>
          </div>
        </div>
        <div class="header-actions">
          <el-button type="text" @click="showRoomDetail">
            <el-icon><InfoFilled /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- 消息区域 -->
      <div class="messages-container" ref="messagesContainer" @scroll="handleScroll">
        <!-- 加载更多 -->
        <div v-if="loadingMore" class="loading-more">
          <el-icon class="is-loading"><Loading /></el-icon>
          加载中...
        </div>
        
        <div v-if="!hasMoreMessages && messages.length > 0" class="no-more-messages">
          没有更多消息了
        </div>

        <!-- 消息列表 -->
        <div v-if="messages.length === 0 && !loading" class="empty-messages">
          <el-empty description="暂无消息，开始聊天吧！" />
        </div>

        <div v-else class="message-list">
          <div
            v-for="(message, index) in messages"
            :key="message.message_id || index"
            class="message-item"
            :class="{ 
              'own-message': message.is_own,
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
                @click="showUserInfo(message.user_id)"
              >
                {{ message.username?.charAt(0) || '用' }}
              </el-avatar>
              <div class="message-content-wrapper">
                <div class="message-header">
                  <span class="message-sender">{{ message.username }}</span>
                  <span class="message-time">{{ formatTime(message.timestamp) }}</span>
                </div>
                <div class="message-bubble" :class="{ 'own': message.is_own }">
                  <div class="message-text">{{ message.content }}</div>
                </div>
                <div v-if="message.is_own" class="message-status">
                  <el-icon v-if="message.sending" class="is-loading"><Loading /></el-icon>
                  <span v-else-if="message.failed" class="failed-status">
                    <el-icon><CircleClose /></el-icon> 发送失败
                  </span>
                  <span v-else class="sent-status">已发送</span>
                </div>
              </div>
            </template>
          </div>
        </div>

        <!-- 新消息提示 -->
        <div v-if="showNewMessageTip" class="new-message-tip" @click="scrollToBottom">
          <el-icon><ArrowDown /></el-icon>
          有新消息
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-section">
        <div class="input-toolbar">
          <el-tooltip content="表情">
            <el-button type="text" @click="showEmojiPicker = !showEmojiPicker">
              <el-icon><ChatDotRound /></el-icon>
            </el-button>
          </el-tooltip>
        </div>
        
        <div class="input-area">
          <el-input
            v-model="newMessage"
            type="textarea"
            :rows="3"
            placeholder="输入消息..."
            resize="none"
            @keyup.enter.prevent="handleSend"
            :disabled="!isConnected || !currentRoom"
          />
        </div>
        
        <div class="input-actions">
          <span class="connection-status" :class="connectionStatusClass">
            <el-icon>
              <CircleCheck v-if="isConnected" />
              <CircleClose v-else />
            </el-icon>
            {{ connectionStatusText }}
          </span>
          <el-button 
            type="primary" 
            @click="handleSend"
            :disabled="!newMessage.trim() || !isConnected || !currentRoom"
            :loading="sending"
          >
            发送
          </el-button>
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
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/modules/auth'
import api from '../api'
import { ElMessage } from 'element-plus'
import {
  Plus, ArrowLeft, InfoFilled, CircleCheck, CircleClose,
  Loading, ArrowDown, ChatDotRound
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

// 响应式状态
const isMobile = ref(window.innerWidth <= 768)
const showChatList = ref(true)

// 群聊列表
const chatRooms = ref([])
const loadingRooms = ref(false)
const currentRoomId = ref(null)
const currentRoom = computed(() => 
  chatRooms.value.find(r => r.room_id === currentRoomId.value)
)

// 消息相关
const messages = ref([])
const newMessage = ref('')
const loading = ref(false)
const loadingMore = ref(false)
const hasMoreMessages = ref(true)
const messagesContainer = ref(null)
const showNewMessageTip = ref(false)
const sending = ref(false)

// WebSocket
const ws = ref(null)
const isConnected = ref(false)
const reconnectAttempts = ref(0)
const maxReconnectAttempts = 5
const reconnectTimer = ref(null)

// 在线用户
const onlineUsers = ref([])

// 未读消息
const unreadCounts = ref({})
const lastMessages = ref({})

// UI 状态
const roomDetailVisible = ref(false)
const showEmojiPicker = ref(false)

// 计算属性
const connectionStatusText = computed(() => {
  if (isConnected.value) return '已连接'
  if (reconnectAttempts.value > 0) return '重连中...'
  return '未连接'
})

const connectionStatusClass = computed(() => ({
  'connected': isConnected.value,
  'connecting': reconnectAttempts.value > 0,
  'disconnected': !isConnected.value && reconnectAttempts.value === 0
}))

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
    
    // 如果有群聊且没有选中，默认选中第一个
    if (allRooms.length > 0 && !currentRoomId.value) {
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
  
  // 加载消息历史
  loadMessages()
  
  // 连接 WebSocket
  connectWebSocket()
}

const loadMessages = async (beforeId = null) => {
  if (!currentRoomId.value) return
  
  if (beforeId) {
    loadingMore.value = true
  } else {
    loading.value = true
    messages.value = []
  }
  
  try {
    const response = await api.chatRooms.getMessages(currentRoomId.value, {
      before_id: beforeId,
      limit: 50
    })
    
    const { messages: newMessages, has_more } = response.data.data
    
    if (beforeId) {
      // 加载更多，添加到前面
      const scrollHeight = messagesContainer.value?.scrollHeight || 0
      messages.value = [...newMessages, ...messages.value]
      hasMoreMessages.value = has_more
      
      // 保持滚动位置
      nextTick(() => {
        if (messagesContainer.value) {
          const newScrollHeight = messagesContainer.value.scrollHeight
          messagesContainer.value.scrollTop = newScrollHeight - scrollHeight
        }
      })
    } else {
      // 首次加载
      messages.value = newMessages
      hasMoreMessages.value = has_more
      
      // 滚动到底部
      nextTick(() => {
        scrollToBottom()
      })
    }
  } catch (error) {
    console.error('加载消息失败:', error)
    ElMessage.error('加载消息失败')
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const handleScroll = () => {
  if (!messagesContainer.value) return
  
  const { scrollTop, scrollHeight, clientHeight } = messagesContainer.value
  
  // 判断是否滚动到底部
  const isAtBottom = scrollHeight - scrollTop - clientHeight < 50
  showNewMessageTip.value = !isAtBottom && hasNewMessagesBelow()
  
  // 滚动到顶部，加载更多
  if (scrollTop === 0 && hasMoreMessages.value && !loadingMore.value) {
    const oldestMessage = messages.value[0]
    if (oldestMessage) {
      loadMessages(oldestMessage.message_id)
    }
  }
}

const hasNewMessagesBelow = () => {
  // 简化处理，实际应该记录最后阅读位置
  return false
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      showNewMessageTip.value = false
    }
  })
}

const connectWebSocket = () => {
  // 关闭现有连接
  if (ws.value) {
    ws.value.close()
    ws.value = null
  }
  
  if (!currentRoomId.value) return
  
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.error('请先登录')
    router.push('/auth/login')
    return
  }
  
  // 构建 WebSocket URL
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${wsProtocol}//${window.location.host}/api/chat-rooms/ws/${currentRoomId.value}?token=${token}`
  
  try {
    ws.value = new WebSocket(wsUrl)
    
    ws.value.onopen = () => {
      console.log('WebSocket 连接成功')
      isConnected.value = true
      reconnectAttempts.value = 0
    }
    
    ws.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        handleWebSocketMessage(data)
      } catch (error) {
        console.error('解析消息失败:', error)
      }
    }
    
    ws.value.onclose = () => {
      console.log('WebSocket 连接关闭')
      isConnected.value = false
      ws.value = null
      
      // 自动重连
      if (reconnectAttempts.value < maxReconnectAttempts) {
        reconnectAttempts.value++
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.value), 10000)
        console.log(`${delay}ms 后尝试重连...`)
        reconnectTimer.value = setTimeout(connectWebSocket, delay)
      } else {
        ElMessage.error('连接失败，请刷新页面重试')
      }
    }
    
    ws.value.onerror = (error) => {
      console.error('WebSocket 错误:', error)
    }
  } catch (error) {
    console.error('创建 WebSocket 连接失败:', error)
  }
}

const handleWebSocketMessage = (data) => {
  switch (data.type) {
    case 'message':
      // 新消息
      messages.value.push(data)
      
      // 更新最后消息
      lastMessages.value[currentRoomId.value] = {
        content: data.content,
        timestamp: data.timestamp
      }
      
      // 如果不是当前查看的群聊，增加未读计数
      if (data.user_id !== authStore.user?.id) {
        if (!isInViewport()) {
          unreadCounts.value[currentRoomId.value] = (unreadCounts.value[currentRoomId.value] || 0) + 1
        }
      }
      
      // 滚动到底部
      nextTick(() => {
        if (isInViewport()) {
          scrollToBottom()
        } else {
          showNewMessageTip.value = true
        }
      })
      break
      
    case 'system':
      // 系统消息
      messages.value.push({
        ...data,
        message_type: 'system'
      })
      scrollToBottom()
      break
      
    case 'user_joined':
      // 用户加入
      if (!onlineUsers.value.includes(data.user_id)) {
        onlineUsers.value.push(data.user_id)
      }
      messages.value.push({
        type: 'system',
        content: `${data.username} 加入了群聊`,
        timestamp: data.timestamp,
        message_type: 'system'
      })
      break
      
    case 'user_left':
      // 用户离开
      onlineUsers.value = onlineUsers.value.filter(id => id !== data.user_id)
      messages.value.push({
        type: 'system',
        content: `${data.username} 离开了群聊`,
        timestamp: data.timestamp,
        message_type: 'system'
      })
      break
      
    case 'online_users':
      // 在线用户列表
      onlineUsers.value = data.users || []
      break
      
    case 'error':
      // 错误消息
      ElMessage.error(data.message || '发生错误')
      break
  }
}

const isInViewport = () => {
  if (!messagesContainer.value) return true
  const { scrollTop, scrollHeight, clientHeight } = messagesContainer.value
  return scrollHeight - scrollTop - clientHeight < 100
}

const handleSend = async () => {
  const content = newMessage.value.trim()
  if (!content || !isConnected.value || !currentRoomId.value) return
  
  sending.value = true
  
  // 创建临时消息
  const tempMessage = {
    message_id: `temp-${Date.now()}`,
    user_id: authStore.user?.id,
    username: authStore.user?.username,
    avatar_url: authStore.user?.avatar_url,
    content: content,
    message_type: 'text',
    timestamp: new Date().toISOString(),
    is_own: true,
    sending: true
  }
  
  messages.value.push(tempMessage)
  newMessage.value = ''
  scrollToBottom()
  
  try {
    // 通过 WebSocket 发送
    if (ws.value && ws.value.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify({
        type: 'text',
        content: content
      }))
      
      // 标记为已发送
      const index = messages.value.findIndex(m => m.message_id === tempMessage.message_id)
      if (index !== -1) {
        messages.value[index].sending = false
      }
    } else {
      // WebSocket 不可用，使用 HTTP
      const response = await api.chatRooms.sendMessage(currentRoomId.value, content)
      const sentMessage = response.data.data
      
      // 替换临时消息
      const index = messages.value.findIndex(m => m.message_id === tempMessage.message_id)
      if (index !== -1) {
        messages.value[index] = { ...sentMessage, is_own: true }
      }
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    
    // 标记为发送失败
    const index = messages.value.findIndex(m => m.message_id === tempMessage.message_id)
    if (index !== -1) {
      messages.value[index].sending = false
      messages.value[index].failed = true
    }
    
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

const showUserInfo = (userId) => {
  // 可以扩展为用户信息弹窗
  console.log('查看用户信息:', userId)
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

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  
  // 清理 WebSocket
  if (ws.value) {
    ws.value.close()
  }
  
  if (reconnectTimer.value) {
    clearTimeout(reconnectTimer.value)
  }
})

// 监听当前群聊变化
watch(currentRoomId, () => {
  if (currentRoomId.value) {
    connectWebSocket()
  }
})
</script>

<style scoped>
.chat-session-container {
  display: flex;
  height: 100vh;
  background-color: #f5f5f5;
}

/* 左侧群聊列表 */
.chat-list-section {
  width: 300px;
  background-color: white;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
}

.chat-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #e4e7ed;
}

.chat-list-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
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
  padding: 10px 0;
}

.chat-room-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.chat-room-item:hover {
  background-color: #f5f7fa;
}

.chat-room-item.active {
  background-color: #ecf5ff;
}

.chat-room-item.unread {
  background-color: #fff8e6;
}

.room-avatar {
  margin-right: 12px;
  background-color: #409eff;
  color: white;
  font-weight: bold;
}

.room-info {
  flex: 1;
  min-width: 0;
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
}

.unread-badge {
  background-color: #f56c6c;
  color: white;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
}

.room-meta {
  display: flex;
  justify-content: space-between;
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

/* 右侧聊天区域 */
.chat-area-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: white;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #e4e7ed;
  background-color: white;
}

.header-left {
  display: flex;
  align-items: center;
}

.back-btn {
  margin-right: 10px;
}

.room-title h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.online-status {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #67c23a;
  margin-top: 4px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

/* 消息区域 */
.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #f5f5f5;
}

.loading-more {
  text-align: center;
  padding: 10px;
  color: #999;
}

.no-more-messages {
  text-align: center;
  padding: 10px;
  color: #999;
  font-size: 12px;
}

.empty-messages {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-item {
  display: flex;
  align-items: flex-start;
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
  cursor: pointer;
  background-color: #409eff;
  color: white;
  font-weight: bold;
}

.message-content-wrapper {
  max-width: 60%;
}

.own-message .message-content-wrapper {
  text-align: right;
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

.message-status {
  margin-top: 4px;
  font-size: 11px;
}

.sent-status {
  color: #999;
}

.failed-status {
  color: #f56c6c;
  cursor: pointer;
}

.new-message-tip {
  position: absolute;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #409eff;
  color: white;
  padding: 8px 16px;
  border-radius: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

/* 输入区域 */
.input-section {
  padding: 15px 20px;
  border-top: 1px solid #e4e7ed;
  background-color: white;
}

.input-toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
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

.connection-status {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

.connection-status.connected {
  color: #67c23a;
}

.connection-status.connecting {
  color: #e6a23c;
}

.connection-status.disconnected {
  color: #f56c6c;
}

/* 群聊详情 */
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
}

/* 移动端适配 */
@media (max-width: 768px) {
  .chat-list-section {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 10;
  }
  
  .chat-list-section.collapsed {
    display: none;
  }
  
  .chat-area-section {
    width: 100%;
  }
  
  .chat-area-section.expanded {
    display: flex;
  }
  
  .message-content-wrapper {
    max-width: 75%;
  }
  
  .messages-container {
    padding: 15px;
  }
  
  .input-section {
    padding: 10px 15px;
  }
}
</style>
