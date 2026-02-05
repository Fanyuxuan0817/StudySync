<template>
  <div class="chat-room-search">
    <div class="search-header">
      <h2>搜索群聊</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        创建群聊
      </el-button>
    </div>

    <div class="search-form">
      <el-form :inline="true" @submit.prevent="handleSearch">
        <el-form-item label="群聊ID">
          <el-input
            v-model="searchForm.chatId"
            placeholder="输入6-8位群聊ID"
            maxlength="8"
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="群聊名称或描述"
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" :loading="loading">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="search-results" v-loading="loading">
      <div v-if="chatRooms.length === 0" class="no-results">
        <el-empty description="暂无搜索结果" />
      </div>
      <div v-else>
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="room in chatRooms" :key="room.chat_room_id">
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
              
              <p class="room-description" v-if="room.description">
                {{ room.description }}
              </p>
              
              <div class="room-stats">
                <span class="member-count">
                  <el-icon><User /></el-icon>
                  {{ room.current_members }}/{{ room.max_members }}
                </span>
                <el-tag size="small" :type="room.is_public ? 'success' : 'warning'">
                  {{ room.is_public ? '公开' : '私密' }}
                </el-tag>
              </div>
              
              <div class="room-actions">
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="handleJoinRoom(room)"
                  :disabled="isAlreadyMember(room)"
                >
                  {{ isAlreadyMember(room) ? '已加入' : '加入群聊' }}
                </el-button>
                <el-button size="small" @click="viewRoomDetails(room)">
                  查看详情
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
        
        <div class="pagination" v-if="total > pageSize">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="total"
            layout="prev, pager, next"
            @current-change="handlePageChange"
          />
        </div>
      </div>
    </div>

    <!-- 创建群聊对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="创建群聊"
      width="500px"
      @close="resetCreateForm"
    >
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="80px">
        <el-form-item label="群聊名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入群聊名称" maxlength="100" />
        </el-form-item>
        <el-form-item label="群聊描述" prop="description">
          <el-input
            v-model="createForm.description"
            type="textarea"
            placeholder="请输入群聊描述（可选）"
            maxlength="500"
            :rows="3"
          />
        </el-form-item>
        <el-form-item label="群聊头像" prop="avatar_url">
          <el-input v-model="createForm.avatar_url" placeholder="头像URL（可选）" />
        </el-form-item>
        <el-form-item label="最大成员数" prop="max_members">
          <el-input-number
            v-model="createForm.max_members"
            :min="10"
            :max="1000"
            :step="10"
          />
        </el-form-item>
        <el-form-item label="是否公开" prop="is_public">
          <el-switch v-model="createForm.is_public" />
          <span class="form-tip">公开群聊可被搜索到</span>
        </el-form-item>
        <el-form-item label="关联群组" prop="group_id" v-if="userGroups.length > 0">
          <el-select v-model="createForm.group_id" placeholder="选择关联的学习群组（可选）">
            <el-option
              v-for="group in userGroups"
              :key="group.group_id"
              :label="group.name"
              :value="group.group_id"
            />
          </el-select>
          <div class="form-tip">关联后可同步群组成员</div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateChatRoom" :loading="createLoading">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 加入群聊对话框 -->
    <el-dialog
      v-model="showJoinDialog"
      title="加入群聊"
      width="400px"
    >
      <div v-if="selectedRoom" class="join-room-info">
        <div class="room-header">
          <el-avatar :size="40" :src="selectedRoom.avatar_url || defaultAvatar">
            {{ selectedRoom.name.charAt(0) }}
          </el-avatar>
          <div class="room-info">
            <h3>{{ selectedRoom.name }}</h3>
            <p>ID: {{ formatChatId(selectedRoom.chat_id) }}</p>
          </div>
        </div>
        
        <el-form :model="joinForm" label-width="80px">
          <el-form-item label="申请理由" prop="message">
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
          发送申请
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Plus, User } from '@element-plus/icons-vue'
import { useAuthStore } from '@/store/modules/auth'
import api from '@/api'

const router = useRouter()
const authStore = useAuthStore()

// 默认头像
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

// 搜索表单
const searchForm = reactive({
  chatId: '',
  keyword: ''
})

// 搜索结果
const chatRooms = ref([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = 20

// 创建群聊
const showCreateDialog = ref(false)
const createLoading = ref(false)
const createFormRef = ref()
const userGroups = ref([])

const createForm = reactive({
  name: '',
  description: '',
  avatar_url: '',
  max_members: 500,
  is_public: true,
  group_id: null
})

const createRules = {
  name: [
    { required: true, message: '请输入群聊名称', trigger: 'blur' },
    { min: 1, max: 100, message: '群聊名称长度不能超过100个字符', trigger: 'blur' }
  ]
}

// 加入群聊
const showJoinDialog = ref(false)
const joinLoading = ref(false)
const selectedRoom = ref(null)
const joinForm = reactive({
  message: ''
})

// 格式化群聊ID显示
const formatChatId = (chatId) => {
  if (!chatId || chatId.length <= 4) return chatId
  
  // 每3位添加分隔符
  let formatted = ''
  for (let i = 0; i < chatId.length; i++) {
    if (i > 0 && i % 3 === 0) {
      formatted += '-'
    }
    formatted += chatId[i]
  }
  return formatted
}

// 搜索群聊
const handleSearch = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize
    }
    
    // 优先使用群聊ID精确搜索
    if (searchForm.chatId) {
      try {
        const response = await api.chatRooms.searchByChatId(searchForm.chatId)
        chatRooms.value = [response.data]
        total.value = 1
      } catch (error) {
        if (error.response?.status === 404) {
          chatRooms.value = []
          total.value = 0
          ElMessage.warning('未找到该群聊ID')
        } else {
          throw error
        }
      }
    } else if (searchForm.keyword) {
      // 使用关键词模糊搜索
      params.keyword = searchForm.keyword
      const response = await api.chatRooms.searchChatRooms(params)
      chatRooms.value = response.data.chat_rooms
      total.value = response.data.total
    } else {
      // 获取公开群聊列表
      const response = await api.chatRooms.searchChatRooms(params)
      chatRooms.value = response.data.chat_rooms
      total.value = response.data.total
    }
  } catch (error) {
    ElMessage.error('搜索失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 重置搜索
const handleReset = () => {
  searchForm.chatId = ''
  searchForm.keyword = ''
  currentPage.value = 1
  handleSearch()
}

// 分页变化
const handlePageChange = (page) => {
  currentPage.value = page
  handleSearch()
}

// 获取用户群组列表
const loadUserGroups = async () => {
  try {
    const response = await api.groups.getGroups()
    // 合并创建的和加入的群组
    userGroups.value = [
      ...response.data.created.map(g => ({ ...g, isCreated: true })),
      ...response.data.joined.map(g => ({ ...g, isJoined: true }))
    ]
  } catch (error) {
    console.error('获取用户群组失败:', error)
  }
}

// 创建群聊
const handleCreateChatRoom = async () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录后再创建群聊')
    router.push('/login')
    return
  }
  
  if (!createFormRef.value) return
  
  await createFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    createLoading.value = true
    try {
      const response = await api.chatRooms.createChatRoom(createForm)
      ElMessage.success('群聊创建成功！')
      ElMessage.info(`群聊ID: ${formatChatId(response.data.chat_id)}`)
      showCreateDialog.value = false
      resetCreateForm()
      handleSearch() // 刷新列表
    } catch (error) {
      ElMessage.error('创建失败：' + (error.response?.data?.detail || error.message))
    } finally {
      createLoading.value = false
    }
  })
}

// 重置创建表单
const resetCreateForm = () => {
  createForm.name = ''
  createForm.description = ''
  createForm.avatar_url = ''
  createForm.max_members = 500
  createForm.is_public = true
  createForm.group_id = null
  if (createFormRef.value) {
    createFormRef.value.clearValidate()
  }
}

// 检查是否已加入群聊
const isAlreadyMember = (room) => {
  // 检查用户是否已登录
  if (!authStore.isAuthenticated) {
    return false
  }
  
  // TODO: 实现完整的检查逻辑
  // 理想情况下，应该通过API获取用户的群聊列表，然后检查当前群聊是否在列表中
  // 或者在前端维护一个已加入群聊的ID列表
  return false
}

// 加入群聊
const handleJoinRoom = (room) => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录后再加入群聊')
    router.push('/login')
    return
  }
  
  selectedRoom.value = room
  showJoinDialog.value = true
}

// 提交加入申请
const submitJoinRequest = async () => {
  joinLoading.value = true
  try {
    await api.chatRooms.createJoinRequest(selectedRoom.value.chat_room_id, {
      message: joinForm.message
    })
    ElMessage.success('加入申请已发送，请等待审批')
    showJoinDialog.value = false
    joinForm.message = ''
  } catch (error) {
    ElMessage.error('申请失败：' + (error.response?.data?.detail || error.message))
  } finally {
    joinLoading.value = false
  }
}

// 查看群聊详情
const viewRoomDetails = (room) => {
  router.push(`/chat-rooms/${room.chat_room_id}`)
}

// 初始化
onMounted(async () => {
  await loadUserGroups()
  handleSearch()
})
</script>

<style scoped>
.chat-room-search {
  padding: 20px;
}

.search-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-header h2 {
  margin: 0;
  color: #333;
}

.search-form {
  background: #f5f7fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.search-results {
  min-height: 400px;
}

.no-results {
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

.room-description {
  font-size: 14px;
  color: #606266;
  margin: 12px 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.room-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 12px 0;
}

.member-count {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #606266;
}

.member-count .el-icon {
  margin-right: 4px;
}

.room-actions {
  display: flex;
  gap: 8px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-left: 8px;
}

.join-room-info {
  padding: 10px 0;
}

.join-room-info .room-header {
  margin-bottom: 20px;
}

@media (max-width: 768px) {
  .chat-room-search {
    padding: 10px;
  }
  
  .search-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
  
  .search-form .el-form-item {
    margin-bottom: 10px;
  }
  
  .room-actions {
    flex-direction: column;
  }
}
</style>