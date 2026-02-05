<template>
  <div class="chatroom-manage-container">
    <!-- 页面头部 -->
    <div class="page-header animate-fadeInUp">
      <div class="header-content">
        <h1 class="page-title">
          <span class="title-icon">💬</span>
          群聊中心
        </h1>
        <p class="page-subtitle">加入学习群组，与志同道合的伙伴一起进步</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog" class="create-btn">
          <span class="btn-icon">+</span>
          创建群聊
        </el-button>
        <el-button @click="goToSearch" class="search-btn">
          <span class="btn-icon">🔍</span>
          搜索群聊
        </el-button>
      </div>
    </div>

    <!-- 标签页 -->
    <div class="tabs-wrapper animate-fadeInUp delay-100">
      <el-tabs v-model="activeTab" class="custom-tabs">
        <el-tab-pane label="我创建的" name="created">
          <div v-if="createdRooms.length > 0" class="rooms-grid">
            <div
              v-for="room in createdRooms"
              :key="room.room_id"
              class="room-card"
              @click="enterRoom(room)"
            >
              <div class="card-header">
                <div class="room-avatar">
                  <span class="avatar-text">{{ room.name.charAt(0) }}</span>
                </div>
                <div class="room-info">
                  <h3 class="room-name">{{ room.name }}</h3>
                  <p class="room-id">ID: {{ room.room_id }}</p>
                </div>
              </div>
              <div class="card-body">
                <p class="room-desc">{{ room.description || '暂无描述' }}</p>
                <div class="room-stats">
                  <span class="stat-item">
                    <span class="stat-icon">👥</span>
                    {{ room.member_count }} 人
                  </span>
                  <span class="stat-item">
                    <span class="stat-icon">🕐</span>
                    {{ formatDate(room.created_at) }}
                  </span>
                </div>
              </div>
              <div class="card-footer">
                <el-button type="primary" link class="enter-btn">
                  进入群聊 →
                </el-button>
                <el-dropdown @command="handleCommand($event, room)" trigger="click" @click.stop>
                  <el-button link class="more-btn">
                    <el-icon><More /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu class="custom-dropdown-menu">
                      <el-dropdown-item command="edit">
                        <span class="menu-icon">✏️</span>
                        编辑
                      </el-dropdown-item>
                      <el-dropdown-item command="delete" divided>
                        <span class="menu-icon">🗑️</span>
                        删除
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <div class="empty-illustration">
              <span class="empty-icon">🏠</span>
            </div>
            <p class="empty-text">还没有创建群聊</p>
            <p class="empty-tip">创建一个群聊，邀请朋友一起学习</p>
            <el-button type="primary" @click="showCreateDialog" size="large">
              <span class="btn-icon">+</span>
              创建群聊
            </el-button>
          </div>
        </el-tab-pane>

        <el-tab-pane label="我加入的" name="joined">
          <div v-if="joinedRooms.length > 0" class="rooms-grid">
            <div
              v-for="room in joinedRooms"
              :key="room.room_id"
              class="room-card"
              @click="enterRoom(room)"
            >
              <div class="card-header">
                <div class="room-avatar joined">
                  <span class="avatar-text">{{ room.name.charAt(0) }}</span>
                </div>
                <div class="room-info">
                  <h3 class="room-name">{{ room.name }}</h3>
                  <p class="room-id">ID: {{ room.room_id }}</p>
                </div>
              </div>
              <div class="card-body">
                <p class="room-desc">{{ room.description || '暂无描述' }}</p>
                <div class="room-stats">
                  <span class="stat-item">
                    <span class="stat-icon">👥</span>
                    {{ room.member_count }} 人
                  </span>
                  <span class="stat-item">
                    <span class="stat-icon">🕐</span>
                    {{ formatDate(room.created_at) }}
                  </span>
                </div>
              </div>
              <div class="card-footer">
                <el-button type="primary" link class="enter-btn">
                  进入群聊 →
                </el-button>
                <el-button 
                  type="danger" 
                  link 
                  @click.stop="handleLeaveRoom(room)"
                  class="leave-btn"
                >
                  退出
                </el-button>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <div class="empty-illustration">
              <span class="empty-icon">🤝</span>
            </div>
            <p class="empty-text">还没有加入群聊</p>
            <p class="empty-tip">搜索并加入感兴趣的群聊</p>
            <el-button type="primary" @click="goToSearch" size="large">
              <span class="btn-icon">🔍</span>
              搜索群聊
            </el-button>
          </div>
        </el-tab-pane>

        <el-tab-pane label="入群审批" name="approvals">
          <div v-if="pendingApprovals.length > 0" class="approvals-list">
            <div
              v-for="approval in pendingApprovals"
              :key="approval.approval_id"
              class="approval-item"
            >
              <div class="approval-info">
                <div class="user-info">
                  <el-avatar :size="48" class="user-avatar">
                    {{ approval.user_name.charAt(0) }}
                  </el-avatar>
                  <div class="user-details">
                    <span class="user-name">{{ approval.user_name }}</span>
                    <span class="room-name">申请加入：{{ approval.room_name }}</span>
                  </div>
                </div>
                <div class="approval-actions">
                  <el-button
                    type="success"
                    @click="handleApprove(approval.approval_id, approval.room_id, true)"
                    class="approve-btn"
                  >
                    <span class="btn-icon">✓</span>
                    同意
                  </el-button>
                  <el-button
                    type="danger"
                    @click="handleApprove(approval.approval_id, approval.room_id, false)"
                    class="reject-btn"
                  >
                    <span class="btn-icon">✕</span>
                    拒绝
                  </el-button>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <div class="empty-illustration">
              <span class="empty-icon">📋</span>
            </div>
            <p class="empty-text">暂无入群申请</p>
            <p class="empty-tip">当有用户申请加入您的群聊时，会显示在这里</p>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 创建群聊对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      title="创建群聊"
      width="520px"
      class="custom-dialog"
      destroy-on-close
    >
      <el-form
        :model="createForm"
        :rules="createRules"
        ref="createFormRef"
        label-width="100px"
        class="create-form"
      >
        <el-form-item label="群聊名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入群聊名称" />
        </el-form-item>
        <el-form-item label="群聊描述" prop="description">
          <el-input
            v-model="createForm.description"
            type="textarea"
            placeholder="请输入群聊描述"
            :rows="4"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="createDialogVisible = false" size="large">取消</el-button>
          <el-button type="primary" @click="handleCreateRoom" :loading="createLoading" size="large">
            <span class="btn-icon">✨</span>
            创建
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 编辑群聊对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑群聊"
      width="520px"
      class="custom-dialog"
      destroy-on-close
    >
      <el-form
        :model="editForm"
        :rules="createRules"
        ref="editFormRef"
        label-width="100px"
        class="edit-form"
      >
        <el-form-item label="群聊名称" prop="name">
          <el-input v-model="editForm.name" placeholder="请输入群聊名称" />
        </el-form-item>
        <el-form-item label="群聊描述" prop="description">
          <el-input
            v-model="editForm.description"
            type="textarea"
            placeholder="请输入群聊描述"
            :rows="4"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="editDialogVisible = false" size="large">取消</el-button>
          <el-button type="primary" @click="handleUpdateRoom" :loading="editLoading" size="large">
            保存修改
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 删除确认对话框 -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="确认删除"
      width="360px"
      class="custom-dialog confirm-dialog"
    >
      <div class="confirm-content">
        <div class="confirm-icon">🗑️</div>
        <p class="confirm-text">确定要删除这个群聊吗？</p>
        <p class="confirm-subtext">删除后所有聊天记录将被清除</p>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="deleteDialogVisible = false" size="large">取消</el-button>
          <el-button type="danger" @click="confirmDelete" :loading="deleteLoading" size="large">
            确认删除
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { More } from '@element-plus/icons-vue'
import api from '../api'

const router = useRouter()
const activeTab = ref('created')
const createdRooms = ref([])
const joinedRooms = ref([])
const pendingApprovals = ref([])
const createDialogVisible = ref(false)
const editDialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const createLoading = ref(false)
const editLoading = ref(false)
const deleteLoading = ref(false)
const createFormRef = ref(null)
const editFormRef = ref(null)
const currentRoom = ref(null)

const createForm = ref({
  name: '',
  description: ''
})

const editForm = ref({
  name: '',
  description: ''
})

const createRules = {
  name: [
    { required: true, message: '请输入群聊名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 200, message: '描述最多 200 个字符', trigger: 'blur' }
  ]
}

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  const month = date.getMonth() + 1
  const day = date.getDate()
  return `${month}月${day}日`
}

// 获取群聊列表
const fetchChatRooms = async () => {
  try {
    const response = await api.chatRooms.getChatRooms()
    createdRooms.value = response.data.data.created || []
    joinedRooms.value = response.data.data.joined || []
  } catch (error) {
    console.error('获取群聊列表失败:', error)
    ElMessage.error('获取群聊列表失败')
  }
}

// 获取入群申请列表
const fetchPendingApprovals = async () => {
  try {
    const response = await api.chatRooms.getPendingApprovals()
    pendingApprovals.value = response.data.data?.approvals || []
  } catch (error) {
    console.error('获取入群申请失败:', error)
  }
}

// 显示创建对话框
const showCreateDialog = () => {
  createForm.value = { name: '', description: '' }
  createDialogVisible.value = true
}

// 创建群聊
const handleCreateRoom = async () => {
  if (!createFormRef.value) return

  try {
    await createFormRef.value.validate()
    createLoading.value = true

    await api.chatRooms.createChatRoom(createForm.value)
    ElMessage.success('群聊创建成功')
    createDialogVisible.value = false
    await fetchChatRooms()
  } catch (error) {
    console.error('创建群聊失败:', error)
    ElMessage.error(error.response?.data?.detail || '创建群聊失败')
  } finally {
    createLoading.value = false
  }
}

// 处理下拉菜单命令
const handleCommand = (command, room) => {
  if (command === 'edit') {
    currentRoom.value = room
    editForm.value = { name: room.name, description: room.description }
    editDialogVisible.value = true
  } else if (command === 'delete') {
    currentRoom.value = room
    deleteDialogVisible.value = true
  }
}

// 更新群聊
const handleUpdateRoom = async () => {
  if (!editFormRef.value) return

  try {
    await editFormRef.value.validate()
    editLoading.value = true

    await api.chatRooms.updateChatRoom(currentRoom.value.room_id, editForm.value)
    ElMessage.success('群聊更新成功')
    editDialogVisible.value = false
    await fetchChatRooms()
  } catch (error) {
    console.error('更新群聊失败:', error)
    ElMessage.error(error.response?.data?.detail || '更新群聊失败')
  } finally {
    editLoading.value = false
  }
}

// 确认删除
const confirmDelete = async () => {
  try {
    deleteLoading.value = true
    await api.chatRooms.deleteChatRoom(currentRoom.value.room_id)
    ElMessage.success('群聊删除成功')
    deleteDialogVisible.value = false
    await fetchChatRooms()
  } catch (error) {
    console.error('删除群聊失败:', error)
    ElMessage.error(error.response?.data?.detail || '删除群聊失败')
  } finally {
    deleteLoading.value = false
  }
}

// 退出群聊
const handleLeaveRoom = async (room) => {
  try {
    await ElMessageBox.confirm('确定要退出这个群聊吗？', '退出群聊', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await api.chatRooms.leaveChatRoom(room.room_id)
    ElMessage.success('已退出群聊')
    await fetchChatRooms()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('退出群聊失败:', error)
      ElMessage.error(error.response?.data?.detail || '退出群聊失败')
    }
  }
}

// 处理入群申请
const handleApprove = async (approvalId, roomId, approved) => {
  try {
    await api.chatRooms.reviewJoinRequest(roomId, approvalId, { approve: approved })
    ElMessage.success(approved ? '已同意入群申请' : '已拒绝入群申请')
    await fetchPendingApprovals()
  } catch (error) {
    console.error('处理入群申请失败:', error)
    ElMessage.error(error.response?.data?.detail || '处理失败')
  }
}

// 进入群聊
const enterRoom = (room) => {
  router.push(`/chat-rooms/${room.room_id}`)
}

// 跳转到搜索页面
const goToSearch = () => {
  router.push('/chat-rooms/search')
}

// 生命周期
onMounted(() => {
  fetchChatRooms()
  fetchPendingApprovals()
})
</script>

<style scoped>
.chatroom-manage-container {
  padding: 0;
}

/* ===== 页面头部 ===== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding: 24px 32px;
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.05) 0%, rgba(77, 150, 255, 0.05) 100%);
  border-radius: 24px;
  border: 1px solid rgba(255, 107, 107, 0.1);
}

.header-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #2D3436;
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0;
}

.title-icon {
  font-size: 32px;
}

.page-subtitle {
  font-size: 15px;
  color: #636E72;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.create-btn .btn-icon,
.search-btn .btn-icon {
  margin-right: 4px;
}

/* ===== 标签页 ===== */
.tabs-wrapper {
  margin-bottom: 32px;
}

.custom-tabs :deep(.el-tabs__header) {
  margin-bottom: 24px;
}

.custom-tabs :deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 500;
  padding: 0 24px;
  height: 44px;
  line-height: 44px;
}

/* ===== 群聊卡片网格 ===== */
.rooms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.room-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(0, 0, 0, 0.04);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.room-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.room-avatar {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.room-avatar.joined {
  background: linear-gradient(135deg, #4D96FF 0%, #6BCB77 100%);
}

.avatar-text {
  font-size: 24px;
  font-weight: 700;
  color: white;
}

.room-info {
  min-width: 0;
}

.room-name {
  font-size: 17px;
  font-weight: 600;
  color: #2D3436;
  margin: 0 0 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.room-id {
  font-size: 13px;
  color: #636E72;
  margin: 0;
}

.card-body {
  margin-bottom: 16px;
}

.room-desc {
  font-size: 14px;
  color: #636E72;
  margin: 0 0 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.6;
}

.room-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #636E72;
}

.stat-icon {
  font-size: 14px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid rgba(0, 0, 0, 0.04);
}

.enter-btn {
  font-weight: 500;
}

.more-btn {
  padding: 8px;
}

.leave-btn {
  color: #FF6B6B !important;
}

/* ===== 入群申请列表 ===== */
.approvals-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.approval-item {
  background: white;
  border-radius: 16px;
  padding: 20px 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.approval-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-avatar {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
  color: white;
  font-weight: 600;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.user-name {
  font-size: 15px;
  font-weight: 600;
  color: #2D3436;
}

.user-details .room-name {
  font-size: 13px;
  color: #636E72;
}

.approval-actions {
  display: flex;
  gap: 12px;
}

.approve-btn,
.reject-btn {
  padding: 10px 20px;
  border-radius: 12px;
}

.approve-btn .btn-icon,
.reject-btn .btn-icon {
  margin-right: 4px;
}

/* ===== 空状态 ===== */
.empty-state {
  text-align: center;
  padding: 64px 24px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

.empty-illustration {
  width: 100px;
  height: 100px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(77, 150, 255, 0.1) 100%);
  border-radius: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-icon {
  font-size: 48px;
}

.empty-text {
  font-size: 18px;
  font-weight: 600;
  color: #2D3436;
  margin-bottom: 8px;
}

.empty-tip {
  font-size: 14px;
  color: #636E72;
  margin-bottom: 24px;
}

/* ===== 下拉菜单 ===== */
.custom-dropdown-menu {
  border-radius: 12px;
  padding: 8px;
}

.custom-dropdown-menu :deep(.el-dropdown-menu__item) {
  border-radius: 8px;
  padding: 10px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.menu-icon {
  font-size: 16px;
}

/* ===== 对话框 ===== */
.custom-dialog :deep(.el-dialog) {
  border-radius: 24px;
}

.confirm-dialog :deep(.el-dialog__body) {
  padding: 0 24px 24px;
}

.confirm-content {
  text-align: center;
  padding: 16px 0;
}

.confirm-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.confirm-text {
  font-size: 16px;
  font-weight: 600;
  color: #2D3436;
  margin-bottom: 8px;
}

.confirm-subtext {
  font-size: 14px;
  color: #636E72;
  margin: 0;
}

.dialog-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* ===== 动画类 ===== */
.animate-fadeInUp {
  animation: fadeInUp 0.6s ease-out forwards;
}

.delay-100 { animation-delay: 0.1s; }

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ===== 响应式设计 ===== */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 20px;
    text-align: center;
    padding: 20px;
  }

  .page-title {
    font-size: 22px;
  }

  .header-actions {
    width: 100%;
    justify-content: center;
  }

  .rooms-grid {
    grid-template-columns: 1fr;
  }

  .approval-info {
    flex-direction: column;
    align-items: flex-start;
  }

  .approval-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
