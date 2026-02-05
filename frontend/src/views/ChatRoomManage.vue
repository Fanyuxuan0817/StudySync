<template>
  <div class="chat-room-manage">
    <div class="manage-header">
      <h2>群聊管理</h2>
      <div class="header-actions">
        <el-button @click="goToSearch">
          <el-icon><Search /></el-icon>
          搜索群聊
        </el-button>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="manage-tabs">
      <!-- 我创建的群聊 -->
      <el-tab-pane label="我创建的群聊" name="created">
        <div class="chat-rooms-list" v-loading="loading">
          <div v-if="createdRooms.length === 0" class="empty-state">
            <el-empty description="暂无创建的群聊">
              <el-button type="primary" @click="goToSearch">创建群聊</el-button>
            </el-empty>
          </div>
          <div v-else>
            <el-row :gutter="20">
              <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="room in createdRooms" :key="room.chat_room_id">
                <el-card class="chat-room-card" shadow="hover">
                  <div class="room-header">
                    <div class="room-avatar">
                      <el-avatar :size="50" :src="room.avatar_url || defaultAvatar">
                        {{ room.name.charAt(0) }}
                      </el-avatar>
                    </div>
                    <div class="room-info">
                      <h3 class="room-name">{{ room.name }}</h3>
                      <p class="room-id">ID: {{ formatChatId(room.chat_id) }}</p>
                    </div>
                  </div>
                  
                  <div class="room-stats">
                    <div class="stat-item">
                      <span class="stat-value">{{ room.current_members }}</span>
                      <span class="stat-label">成员数</span>
                    </div>
                    <div class="stat-item">
                      <el-tag size="small" :type="room.is_public ? 'success' : 'warning'">
                        {{ room.is_public ? '公开' : '私密' }}
                      </el-tag>
                    </div>
                  </div>
                  
                  <div class="room-actions">
                    <el-button type="primary" size="small" @click="enterChatRoom(room)">
                      进入群聊
                    </el-button>
                    <el-button size="small" @click="viewJoinRequests(room)" v-if="room.pending_requests > 0">
                      审批申请
                      <el-badge :value="room.pending_requests" class="item-badge" />
                    </el-button>
                    <el-button size="small" @click="editRoom(room)">
                      编辑
                    </el-button>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </div>
      </el-tab-pane>

      <!-- 我加入的群聊 -->
      <el-tab-pane label="我加入的群聊" name="joined">
        <div class="chat-rooms-list" v-loading="loading">
          <div v-if="joinedRooms.length === 0" class="empty-state">
            <el-empty description="暂无加入的群聊">
              <el-button type="primary" @click="goToSearch">搜索群聊</el-button>
            </el-empty>
          </div>
          <div v-else>
            <el-row :gutter="20">
              <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="room in joinedRooms" :key="room.chat_room_id">
                <el-card class="chat-room-card" shadow="hover">
                  <div class="room-header">
                    <div class="room-avatar">
                      <el-avatar :size="50" :src="room.avatar_url || defaultAvatar">
                        {{ room.name.charAt(0) }}
                      </el-avatar>
                    </div>
                    <div class="room-info">
                      <h3 class="room-name">{{ room.name }}</h3>
                      <p class="room-id">ID: {{ formatChatId(room.chat_id) }}</p>
                      <el-tag size="small" :type="getRoleType(room.role)">
                        {{ getRoleLabel(room.role) }}
                      </el-tag>
                    </div>
                  </div>
                  
                  <div class="room-stats">
                    <div class="stat-item">
                      <span class="stat-value">{{ room.current_members }}</span>
                      <span class="stat-label">成员数</span>
                    </div>
                    <div class="stat-item">
                      <el-tag size="small" :type="room.is_public ? 'success' : 'warning'">
                        {{ room.is_public ? '公开' : '私密' }}
                      </el-tag>
                    </div>
                  </div>
                  
                  <div class="room-actions">
                    <el-button type="primary" size="small" @click="enterChatRoom(room)">
                      进入群聊
                    </el-button>
                    <el-button size="small" @click="viewMembers(room)" v-if="room.role !== 'member'">
                      成员管理
                    </el-button>
                    <el-button size="small" @click="leaveRoom(room)" type="danger" plain>
                      退出群聊
                    </el-button>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </div>
      </el-tab-pane>

      <!-- 审批管理 -->
      <el-tab-pane label="审批管理" name="requests" v-if="hasAdminRooms">
        <div class="requests-list" v-loading="requestsLoading">
          <div class="requests-header">
            <h3>待审批的加入请求</h3>
            <el-button @click="loadJoinRequests" :icon="Refresh">刷新</el-button>
          </div>
          
          <div v-if="joinRequests.length === 0" class="empty-state">
            <el-empty description="暂无待审批的请求" />
          </div>
          <div v-else>
            <el-table :data="joinRequests" style="width: 100%">
              <el-table-column prop="username" label="申请人" width="120">
                <template #default="scope">
                  <div class="user-info">
                    <el-avatar :size="32" :src="scope.row.avatar_url">
                      {{ scope.row.username.charAt(0) }}
                    </el-avatar>
                    <span>{{ scope.row.username }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="chat_room_name" label="群聊名称" width="150" />
              <el-table-column prop="chat_id" label="群聊ID" width="120">
                <template #default="scope">
                  {{ formatChatId(scope.row.chat_id) }}
                </template>
              </el-table-column>
              <el-table-column prop="message" label="申请理由" show-overflow-tooltip />
              <el-table-column prop="created_at" label="申请时间" width="160">
                <template #default="scope">
                  {{ formatDate(scope.row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200" fixed="right">
                <template #default="scope">
                  <el-button size="small" type="success" @click="approveRequest(scope.row)">
                    批准
                  </el-button>
                  <el-button size="small" type="danger" @click="rejectRequest(scope.row)">
                    拒绝
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 审批对话框 -->
    <el-dialog
      v-model="showReviewDialog"
      title="审批加入申请"
      width="400px"
    >
      <div v-if="currentRequest" class="review-info">
        <div class="user-info">
          <el-avatar :size="40" :src="currentRequest.avatar_url">
            {{ currentRequest.username.charAt(0) }}
          </el-avatar>
          <div class="user-details">
            <h4>{{ currentRequest.username }}</h4>
            <p>申请加入 {{ currentRequest.chat_room_name }}</p>
          </div>
        </div>
        
        <div class="request-message" v-if="currentRequest.message">
          <label>申请理由：</label>
          <p>{{ currentRequest.message }}</p>
        </div>
        
        <el-form :model="reviewForm" label-width="80px">
          <el-form-item label="审批意见">
            <el-input
              v-model="reviewForm.review_message"
              type="textarea"
              placeholder="请输入审批意见（可选）"
              maxlength="500"
              :rows="3"
            />
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <el-button @click="showReviewDialog = false">取消</el-button>
        <el-button type="danger" @click="submitReview(false)">拒绝</el-button>
        <el-button type="success" @click="submitReview(true)">批准</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { useAuthStore } from '@/store/modules/auth'
import api from '@/api'

const router = useRouter()
const authStore = useAuthStore()

// 获取当前用户ID
const currentUserId = computed(() => authStore.user?.user_id)

// 默认头像
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

// 标签页状态
const activeTab = ref('created')

// 数据加载
const loading = ref(false)
const requestsLoading = ref(false)

// 群聊数据
const createdRooms = ref([])
const joinedRooms = ref([])
const joinRequests = ref([])

// 审批对话框
const showReviewDialog = ref(false)
const currentRequest = ref(null)
const reviewForm = reactive({
  review_message: ''
})

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

// 计算属性
const hasAdminRooms = computed(() => {
  return joinedRooms.value.some(room => room.role === 'owner' || room.role === 'admin')
})

// 加载群聊数据
const loadChatRooms = async () => {
  loading.value = true
  try {
    // 获取用户创建和加入的群聊列表
    const response = await api.chatRooms.searchChatRooms({ page: 1, page_size: 100 })
    const allRooms = response.data.chat_rooms
    
    // 分离创建的群聊和加入的群聊
    createdRooms.value = allRooms.filter(room => room.creator_id === currentUserId.value)
    joinedRooms.value = allRooms.filter(room => {
      // 这里需要根据实际的用户ID进行筛选
      // 暂时显示所有群聊，后续需要根据成员关系筛选
      return room.creator_id !== currentUserId.value
    })
    
    // 获取每个群聊的待审批请求数量
    for (const room of createdRooms.value) {
      try {
        const requestsResponse = await api.chatRooms.getJoinRequests(room.chat_room_id, { status: 'pending' })
        room.pending_requests = requestsResponse.data.length || 0
      } catch (error) {
        room.pending_requests = 0
      }
    }
    
  } catch (error) {
    ElMessage.error('加载群聊失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 加载加入请求
const loadJoinRequests = async () => {
  requestsLoading.value = true
  try {
    // 获取所有需要审批的请求
    const allRequests = []
    
    // 遍历用户管理的群聊，获取每个群聊的加入请求
    for (const room of createdRooms.value) {
      try {
        const response = await api.chatRooms.getJoinRequests(room.chat_room_id)
        const roomRequests = response.data.map(request => ({
          ...request,
          avatar_url: null // 可以后续添加头像信息
        }))
        allRequests.push(...roomRequests)
      } catch (error) {
        console.error(`获取群聊 ${room.chat_room_id} 的请求失败:`, error)
      }
    }
    
    joinRequests.value = allRequests
  } catch (error) {
    ElMessage.error('加载请求失败：' + (error.response?.data?.detail || error.message))
  } finally {
    requestsLoading.value = false
  }
}

// 导航函数
const goToSearch = () => {
  router.push('/chat-rooms/search')
}

const enterChatRoom = (room) => {
  router.push(`/chat-rooms/${room.chat_room_id}`)
}

const viewJoinRequests = (room) => {
  activeTab.value = 'requests'
  loadJoinRequests()
}

const editRoom = (room) => {
  // 实现编辑功能
  ElMessage.info('编辑功能开发中...')
}

const viewMembers = (room) => {
  // 实现成员管理功能
  ElMessage.info('成员管理功能开发中...')
}

const leaveRoom = async (room) => {
  try {
    await ElMessageBox.confirm(
      `确定要退出群聊 "${room.name}" 吗？`,
      '确认退出',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 这里需要实现退出群聊的API
    ElMessage.success('已退出群聊')
    loadChatRooms()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败：' + (error.response?.data?.detail || error.message))
    }
  }
}

// 审批函数
const approveRequest = (request) => {
  currentRequest.value = request
  showReviewDialog.value = true
}

const rejectRequest = (request) => {
  currentRequest.value = request
  showReviewDialog.value = true
}

const submitReview = async (approve) => {
  try {
    if (!currentRequest.value) return
    
    const data = {
      approve,
      review_message: reviewForm.review_message
    }
    
    // 调用审批API
    await api.chatRooms.reviewJoinRequest(
      currentRequest.value.chat_room_id,
      currentRequest.value.request_id,
      data
    )
    
    ElMessage.success(approve ? '已批准加入申请' : '已拒绝加入申请')
    showReviewDialog.value = false
    reviewForm.review_message = ''
    currentRequest.value = null
    loadJoinRequests()
    loadChatRooms() // 刷新群聊数据
  } catch (error) {
    ElMessage.error('审批失败：' + (error.response?.data?.detail || error.message))
  }
}

// 初始化
onMounted(() => {
  loadChatRooms()
  if (activeTab.value === 'requests') {
    loadJoinRequests()
  }
})
</script>

<style scoped>
.chat-room-manage {
  padding: 20px;
}

.manage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.manage-header h2 {
  margin: 0;
  color: #333;
}

.manage-tabs {
  background: white;
  border-radius: 8px;
  padding: 20px;
}

.chat-rooms-list {
  min-height: 400px;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.chat-room-card {
  margin-bottom: 20px;
  height: 100%;
}

.room-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.room-avatar {
  margin-right: 12px;
}

.room-info {
  flex: 1;
}

.room-name {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.room-id {
  margin: 4px 0 0;
  font-size: 12px;
  color: #909399;
}

.room-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 12px 0;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.room-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.item-badge {
  margin-left: 4px;
}

.requests-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.requests-header h3 {
  margin: 0;
  color: #333;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.review-info {
  padding: 10px 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.user-details h4 {
  margin: 0 0 4px 0;
  color: #303133;
}

.user-details p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.request-message {
  margin-bottom: 16px;
}

.request-message label {
  font-weight: 500;
  color: #606266;
  margin-bottom: 8px;
  display: block;
}

.request-message p {
  margin: 0;
  padding: 8px 12px;
  background: #f4f4f5;
  border-radius: 4px;
  color: #606266;
  font-size: 14px;
}

@media (max-width: 768px) {
  .chat-room-manage {
    padding: 10px;
  }
  
  .manage-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
  
  .manage-tabs {
    padding: 10px;
  }
  
  .room-actions {
    flex-direction: column;
  }
  
  .requests-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
}
</style>