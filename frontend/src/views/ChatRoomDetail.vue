<template>
  <div class="chat-room-detail">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <el-spinner size="60" />
      <p class="loading-text">加载中，请稍候...</p>
    </div>
    
    <div v-else>
      <div class="detail-header">
        <el-button type="text" @click="goBack" class="back-button">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <div class="room-info">
          <div class="room-avatar">
            <el-avatar :size="60" :src="roomInfo.avatar_url || defaultAvatar">
              {{ roomInfo.name?.charAt(0) }}
            </el-avatar>
          </div>
          <div class="room-details">
            <h1 class="room-name">{{ roomInfo.name }}</h1>
            <p class="room-id">群聊ID: {{ formatChatId(roomInfo.chat_id) }}</p>
            <div class="room-stats">
              <el-tag size="small" :type="roomInfo.is_public ? 'success' : 'warning'">
                {{ roomInfo.is_public ? '公开群聊' : '私密群聊' }}
              </el-tag>
              <span class="member-count">
                <el-icon><User /></el-icon>
                {{ roomInfo.current_members }}/{{ roomInfo.max_members }} 成员
              </span>
            </div>
          </div>
        </div>
        <div class="header-actions">
          <el-button 
            v-if="!isMember" 
            type="primary" 
            @click="showJoinDialog = true"
            :disabled="roomInfo.current_members >= roomInfo.max_members"
          >
            申请加入
          </el-button>
          <el-button 
            v-else 
            type="success" 
            @click="enterChatRoom"
          >
            进入群聊
          </el-button>
        </div>
      </div>

    <el-tabs v-model="activeTab" class="detail-tabs">
      <!-- 群聊信息 -->
      <el-tab-pane label="群聊信息" name="info">
        <el-card>
          <div class="info-section">
            <h3>基本信息</h3>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="群聊名称">{{ roomInfo.name }}</el-descriptions-item>
              <el-descriptions-item label="群聊ID">{{ roomInfo.chat_id }}</el-descriptions-item>
              <el-descriptions-item label="群聊描述">{{ roomInfo.description || '暂无描述' }}</el-descriptions-item>
              <el-descriptions-item label="创建者">{{ roomInfo.creator_name || '未知' }}</el-descriptions-item>
              <el-descriptions-item label="创建时间">{{ formatDate(roomInfo.created_at) }}</el-descriptions-item>
              <el-descriptions-item label="最大成员数">{{ roomInfo.max_members }}</el-descriptions-item>
              <el-descriptions-item label="是否公开">
                <el-tag :type="roomInfo.is_public ? 'success' : 'warning'">
                  {{ roomInfo.is_public ? '公开' : '私密' }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <div class="info-section" v-if="roomInfo.group_info">
            <h3>关联的学习群组</h3>
            <el-card shadow="never">
              <div class="group-info">
                <h4>{{ roomInfo.group_info.name }}</h4>
                <p>{{ roomInfo.group_info.description }}</p>
                <el-button type="text" @click="goToGroup(roomInfo.group_info.group_id)">
                  查看群组详情
                </el-button>
              </div>
            </el-card>
          </div>
        </el-card>
      </el-tab-pane>

      <!-- 成员列表 -->
      <el-tab-pane label="成员列表" name="members">
        <div class="members-section">
          <div class="members-header">
            <h3>群聊成员 ({{ members.length }})</h3>
            <el-input
              v-model="memberSearch"
              placeholder="搜索成员"
              style="width: 200px"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
          
          <div class="members-list">
            <div 
              v-for="member in filteredMembers" 
              :key="member.user_id"
              class="member-item"
            >
              <div class="member-avatar">
                <el-avatar :size="40" :src="member.avatar_url">
                  {{ member.username.charAt(0) }}
                </el-avatar>
              </div>
              <div class="member-info">
                <div class="member-name">{{ member.username }}</div>
                <div class="member-role">
                  <el-tag size="small" :type="getRoleType(member.role)">
                    {{ getRoleLabel(member.role) }}
                  </el-tag>
                </div>
              </div>
              <div class="member-stats">
                <div class="join-time">加入时间：{{ formatDate(member.joined_at) }}</div>
                <div class="last-active" v-if="member.last_active_at">
                  最后活跃：{{ formatDate(member.last_active_at) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 加入请求历史（仅管理员可见） -->
      <el-tab-pane label="加入申请" name="requests" v-if="isAdmin">
        <div class="requests-section">
          <div class="requests-header">
            <h3>加入申请历史</h3>
            <el-radio-group v-model="requestStatus" size="small">
              <el-radio-button label="all">全部</el-radio-button>
              <el-radio-button label="pending">待审批</el-radio-button>
              <el-radio-button label="approved">已批准</el-radio-button>
              <el-radio-button label="rejected">已拒绝</el-radio-button>
            </el-radio-group>
          </div>
          
          <div class="requests-list">
            <div 
              v-for="request in filteredRequests" 
              :key="request.request_id"
              class="request-item"
            >
              <div class="request-user">
                <el-avatar :size="32" :src="request.avatar_url">
                  {{ request.username.charAt(0) }}
                </el-avatar>
                <span class="username">{{ request.username }}</span>
              </div>
              <div class="request-content">
                <div class="request-message" v-if="request.message">
                  申请理由：{{ request.message }}
                </div>
                <div class="request-time">
                  申请时间：{{ formatDate(request.created_at) }}
                </div>
                <div class="request-status">
                  <el-tag :type="getRequestStatusType(request.status)">
                    {{ getRequestStatusLabel(request.status) }}
                  </el-tag>
                  <span v-if="request.reviewed_at" class="review-time">
                    审批时间：{{ formatDate(request.reviewed_at) }}
                  </span>
                </div>
                <div class="review-message" v-if="request.review_message">
                  审批意见：{{ request.review_message }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 加入群聊对话框 -->
    <el-dialog
      v-model="showJoinDialog"
      title="申请加入群聊"
      width="400px"
    >
      <div class="join-dialog-content">
        <el-form :model="joinForm" label-width="80px">
          <el-form-item label="申请理由">
            <el-input
              v-model="joinForm.message"
              type="textarea"
              placeholder="请输入申请加入的理由（可选）"
              maxlength="500"
              :rows="3"
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="showJoinDialog = false">取消</el-button>
        <el-button type="primary" @click="submitJoinRequest" :loading="joinLoading">
          提交申请
        </el-button>
      </template>
    </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/store/modules/auth'
import api from '@/api'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 获取当前用户ID
const currentUserId = computed(() => authStore.user?.user_id)

// 默认头像
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

// 数据状态
const loading = ref(false)
const joinLoading = ref(false)
const roomInfo = ref({})
const members = ref([])
const joinRequests = ref([])
const isMember = ref(false)
const isAdmin = ref(false)

// 标签页状态
const activeTab = ref('info')

// 搜索和筛选
const memberSearch = ref('')
const requestStatus = ref('all')

// 对话框状态
const showJoinDialog = ref(false)

// 表单数据
const joinForm = reactive({
  message: ''
})

// 计算属性
const filteredMembers = computed(() => {
  if (!memberSearch.value) return members.value
  return members.value.filter(member => 
    member.username.toLowerCase().includes(memberSearch.value.toLowerCase())
  )
})

const filteredRequests = computed(() => {
  if (requestStatus.value === 'all') return joinRequests.value
  return joinRequests.value.filter(request => request.status === requestStatus.value)
})

// 格式化函数
const formatChatId = (chatId) => {
  if (!chatId || chatId.length <= 4) return chatId
  
  let formatted = ''
  for (let i = 0; i < chatId.length; i++) {
    if (i > 0 && i % 3 === 0) {
      formatted += '-'
    }
    formatted += chatId[i]
  }
  return formatted
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

// 角色相关函数
const getRoleLabel = (role) => {
  const roleMap = {
    owner: '群主',
    admin: '管理员',
    member: '成员'
  }
  return roleMap[role] || role
}

const getRoleType = (role) => {
  const typeMap = {
    owner: 'danger',
    admin: 'warning',
    member: 'info'
  }
  return typeMap[role] || 'info'
}

// 申请状态相关函数
const getRequestStatusLabel = (status) => {
  const statusMap = {
    pending: '待审批',
    approved: '已批准',
    rejected: '已拒绝',
    cancelled: '已取消'
  }
  return statusMap[status] || status
}

const getRequestStatusType = (status) => {
  const typeMap = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
    cancelled: 'info'
  }
  return typeMap[status] || 'info'
}

// 导航函数
const goBack = () => {
  router.back()
}

const goToGroup = (groupId) => {
  router.push(`/groups/${groupId}`)
}

const enterChatRoom = () => {
  router.push({
    path: `/chat/${roomInfo.value.group_info?.group_id || route.params.id}`,
    query: { name: roomInfo.value.name }
  })
}

// 数据加载函数
const loadRoomInfo = async () => {
  loading.value = true
  try {
    // 使用专门的群聊详情API
    const response = await api.chatRooms.getChatRoom(route.params.id)
    roomInfo.value = response.data.data
  } catch (error) {
    // 优化错误提示信息
    let errorMessage = '加载群聊信息失败'
    if (error.response?.status === 404) {
      errorMessage = '抱歉，该群聊不存在或已关闭'
    } else if (error.response?.status === 403) {
      errorMessage = '抱歉，该群聊不对外开放'
    } else if (error.response?.data?.detail) {
      errorMessage += '：' + error.response.data.detail
    } else if (error.response?.data?.message) {
      errorMessage += '：' + error.response.data.message
    } else if (error.message) {
      errorMessage += '：' + error.message
    }
    ElMessage.error(errorMessage)
    router.push('/chat-rooms')
  } finally {
    loading.value = false
  }
}

const loadMembers = async () => {
  try {
    const response = await api.chatRooms.getChatRoomMembers(route.params.id)
    members.value = response.data.data.members
  } catch (error) {
    // 优化错误提示信息
    let errorMessage = '加载成员列表失败'
    if (error.response?.data?.detail) {
      errorMessage += '：' + error.response.data.detail
    } else if (error.response?.data?.message) {
      errorMessage += '：' + error.response.data.message
    } else if (error.message) {
      errorMessage += '：' + error.message
    } else if (error.response?.data) {
      // 处理对象类型的错误信息
      try {
        errorMessage += '：' + JSON.stringify(error.response.data)
      } catch {
        errorMessage += '：未知错误'
      }
    }
    ElMessage.error(errorMessage)
  }
}

const loadJoinRequests = async () => {
  try {
    // 获取所有状态的加入请求
    const response = await api.chatRooms.getJoinRequests(route.params.id)
    // 检查响应格式，适应可能的变化
    if (response.data.data?.join_requests) {
      joinRequests.value = response.data.data.join_requests
    } else if (response.data.data) {
      joinRequests.value = response.data.data
    } else if (response.data) {
      joinRequests.value = response.data
    }
  } catch (error) {
    // 优化错误提示信息
    let errorMessage = '加载申请历史失败'
    if (error.response?.data?.detail) {
      errorMessage += '：' + error.response.data.detail
    } else if (error.response?.data?.message) {
      errorMessage += '：' + error.response.data.message
    } else if (error.message) {
      errorMessage += '：' + error.message
    } else if (error.response?.data) {
      // 处理对象类型的错误信息
      try {
        errorMessage += '：' + JSON.stringify(error.response.data)
      } catch {
        errorMessage += '：未知错误'
      }
    }
    ElMessage.error(errorMessage)
  }
}

const checkMembership = async () => {
  try {
    // 通过获取成员列表来检查当前用户是否是成员
    const response = await api.chatRooms.getChatRoomMembers(route.params.id)
    
    const currentUserMember = response.data.data.members.find(member => member.user_id === currentUserId.value)
    
    if (currentUserMember) {
      isMember.value = true
      isAdmin.value = currentUserMember.role === 'owner' || currentUserMember.role === 'admin'
    } else {
      isMember.value = false
      isAdmin.value = false
    }
  } catch (error) {
    // 如果获取成员列表失败，说明用户不是成员
    isMember.value = false
    isAdmin.value = false
    console.log('用户不是群聊成员或群聊不存在')
  }
}

// 提交加入申请
const submitJoinRequest = async () => {
  if (!joinForm.message.trim()) {
    ElMessage.warning('请输入申请理由')
    return
  }
  
  joinLoading.value = true
  try {
    await api.chatRooms.createJoinRequest(route.params.id, {
      message: joinForm.message.trim()
    })
    ElMessage.success('加入申请已提交，请等待审批')
    showJoinDialog.value = false
    joinForm.message = ''
  } catch (error) {
    ElMessage.error('提交申请失败：' + (error.response?.data?.detail || error.message))
  } finally {
    joinLoading.value = false
  }
}

// 初始化
onMounted(async () => {
  await loadRoomInfo()
  await checkMembership()
  if (isMember.value) {
    await loadMembers()
    if (isAdmin.value) {
      await loadJoinRequests()
    }
  }
})
</script>

<style scoped>
.chat-room-detail {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.back-button {
  padding: 8px 12px;
}

.room-info {
  display: flex;
  align-items: center;
  flex: 1;
  margin: 0 20px;
}

.room-avatar {
  margin-right: 16px;
}

.room-details {
  flex: 1;
}

.room-name {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.room-id {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #909399;
}

.room-stats {
  display: flex;
  align-items: center;
  gap: 16px;
}

.member-count {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: #606266;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.detail-tabs {
  background: white;
  border-radius: 8px;
  padding: 20px;
}

.info-section {
  margin-bottom: 24px;
}

.info-section h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #303133;
}

.group-info {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 4px;
}

.group-info h4 {
  margin: 0 0 8px 0;
  color: #303133;
}

.group-info p {
  margin: 0 0 12px 0;
  color: #606266;
}

.members-section {
  padding: 20px 0;
}

.members-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.members-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.members-list {
  display: grid;
  gap: 12px;
}

.member-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
  transition: background-color 0.3s;
}

.member-item:hover {
  background: #ebeef5;
}

.member-avatar {
  margin-right: 12px;
}

.member-info {
  flex: 1;
}

.member-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.member-stats {
  text-align: right;
  font-size: 12px;
  color: #909399;
}

.join-time, .last-active {
  margin-bottom: 2px;
}

.requests-section {
  padding: 20px 0;
}

.requests-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.requests-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.requests-list {
  display: grid;
  gap: 12px;
}

.request-item {
  display: flex;
  align-items: flex-start;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 6px;
}

.request-user {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-right: 16px;
  min-width: 120px;
}

.username {
  font-weight: 500;
  color: #303133;
}

.request-content {
  flex: 1;
}

.request-message {
  margin-bottom: 8px;
  color: #606266;
}

.request-time {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.request-status {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.review-time {
  font-size: 12px;
  color: #909399;
}

.review-message {
  font-size: 14px;
  color: #606266;
  background: white;
  padding: 8px 12px;
  border-radius: 4px;
  margin-top: 8px;
}

.join-dialog-content {
  padding: 10px 0;
}

/* 加载状态样式 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.loading-text {
  margin-top: 16px;
  font-size: 16px;
  color: #606266;
}

@media (max-width: 768px) {
  .chat-room-detail {
    padding: 10px;
  }
  
  .detail-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .room-info {
    margin: 0;
  }
  
  .room-name {
    font-size: 20px;
  }
  
  .request-item {
    flex-direction: column;
    gap: 12px;
  }
  
  .request-user {
    margin-right: 0;
    min-width: auto;
  }
}
</style>