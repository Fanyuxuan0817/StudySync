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
          <el-button @click="debugSearch" type="info" size="small">
            调试搜索
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="search-results" v-loading="loading">
      <!-- 骨架屏 -->
      <div v-if="showSkeleton && chatRooms.length === 0" class="skeleton-container">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="i in 8" :key="i">
            <el-card class="chat-room-card" shadow="never">
              <template #body>
                <el-skeleton :rows="4" animated />
              </template>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <div v-if="chatRooms.length === 0 && !showSkeleton" class="no-results">
        <el-empty description="暂无搜索结果" />
      </div>
      <div v-else>
        <div v-if="chatRooms.length > 100" class="performance-notice">
          <el-alert
            title="数据量较大"
            type="info"
            description="当前显示 {{ chatRooms.length }} 条群聊，建议使用搜索功能筛选"
            show-icon
            :closable="false"
          />
        </div>
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="room in chatRooms" :key="room.chat_room_id">
            <el-card class="chat-room-card" shadow="hover">
              <div class="room-header">
                <div class="room-avatar">
                  <el-avatar :size="50" :src="room.avatar_url || defaultAvatar">
                    {{ room.name?.charAt(0) || '群' }}
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
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Plus, User } from '@element-plus/icons-vue'
import { useAuthStore } from '@/store/modules/auth'
import api from '@/api'

const router = useRouter()
const authStore = useAuthStore()

// 默认头像
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

// 搜索防抖
let searchTimeout = null

// 搜索表单
const searchForm = reactive({
  chatId: '',
  keyword: ''
})

// 监听搜索表单变化，实现防抖搜索
watch([() => searchForm.chatId, () => searchForm.keyword], () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    if (searchForm.chatId || searchForm.keyword) {
      console.log('[防抖搜索] 表单变化触发搜索')
      handleSearch()
    }
  }, 500) // 500ms防抖
})

// 搜索完成回调
const emit = defineEmits(['search-complete', 'search-error'])

// 搜索结果
const chatRooms = ref([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = 20

// 骨架屏显示控制
const showSkeleton = ref(false)
const skeletonDelay = 200 // 200ms后开始显示骨架屏

// 加载状态监控
const loadStats = ref({
  attemptCount: 0,
  lastError: null,
  avgLoadTime: 0,
  successCount: 0
})

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

// 格式化群聊ID显示（优化性能）
const formatChatId = (chatId) => {
  if (!chatId || chatId.length <= 4) return chatId
  
  // 使用更高效的字符串处理方法
  return chatId.replace(/(\d{3})(?=\d)/g, '$1-')
}

// 搜索群聊
const handleSearch = async (retryCount = 0) => {
  const startTime = Date.now()
  loading.value = true
  loadStats.value.attemptCount++
  
  // 延迟显示骨架屏，避免闪烁
  const skeletonTimer = setTimeout(() => {
    showSkeleton.value = true
  }, skeletonDelay)
  
  // 详细调试信息
  console.log(`[搜索开始] 参数:`, {
    chatId: searchForm.chatId,
    keyword: searchForm.keyword,
    page: currentPage.value,
    pageSize: pageSize,
    retryCount: retryCount
  })
  
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize
    }
    
    // 优先使用群聊ID精确搜索
    if (searchForm.chatId) {
      try {
        const response = await api.chatRooms.searchByChatId(searchForm.chatId)
        chatRooms.value = [response.data?.data]
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
      console.log(`[API请求] 关键词搜索参数:`, params)
      const response = await api.chatRooms.searchChatRooms(params)
      console.log(`[API响应] 关键词搜索结果:`, response)
      // 增强数据完整性验证 - API返回结构: response.data.data.chat_rooms
      const responseData = response.data?.data || {}
      chatRooms.value = responseData.chat_rooms || []
      total.value = responseData.total || 0

      // 更新成功统计
      loadStats.value.successCount++
      loadStats.value.lastError = null

      // 详细调试信息
      console.log(`[搜索成功] 结果:`, {
        dataCount: chatRooms.value.length,
        totalCount: total.value,
        responseData: responseData,
        loadTime: Date.now() - startTime + 'ms'
      })

      // 数据验证
      if (chatRooms.value.length === 0 && total.value > 0) {
        console.warn('[数据异常] 总计数大于0但实际数据为空')
      }

      // 触发搜索完成事件
      emit('search-complete', {
        results: chatRooms.value,
        total: total.value,
        loadTime: Date.now() - startTime,
        stats: loadStats.value
      })
    } else {
      // 获取公开群聊列表
      console.log(`[API请求] 公开群聊列表参数:`, params)
      const response = await api.chatRooms.searchChatRooms(params)
      console.log(`[API响应] 公开群聊列表结果:`, response)
      // 增强数据完整性验证 - API返回结构: response.data.data.chat_rooms
      const responseData = response.data?.data || {}
      chatRooms.value = responseData.chat_rooms || []
      total.value = responseData.total || 0
    }
  } catch (error) {
    // 确保即使出错也清空结果，避免显示旧数据
    chatRooms.value = []
    total.value = 0
    
    // 网络超时错误
    if (error.code === 'ECONNABORTED') {
      console.error(`[网络超时] 错误详情:`, error)
      if (retryCount < 2) {
        ElMessage.warning(`搜索超时，正在重试(${retryCount + 1}/2)...`)
        setTimeout(() => {
          handleSearch(retryCount + 1)
        }, 1000)
        return
      } else {
        ElMessage.error('搜索超时，请检查网络连接后重试')
        return
      }
    }
    
    // 网络连接错误
    if (error.message.includes('Network Error')) {
      console.error(`[网络错误] 详细信息:`, error)
      if (retryCount < 2) {
        ElMessage.warning(`网络连接失败，正在重试(${retryCount + 1}/2)...`)
        setTimeout(() => {
          handleSearch(retryCount + 1)
        }, 1000)
        return
      } else {
        ElMessage.error('网络连接失败，请检查网络设置后重试')
        return
      }
    }
    
    // 服务器错误
    if (error.response?.status >= 500) {
      ElMessage.error('服务器繁忙，请稍后再试')
      return
    }
    
    // 其他错误
    const errorMessage = error.response?.data?.detail || error.message
    ElMessage.error('搜索失败：' + errorMessage)
    loadStats.value.lastError = errorMessage
    
    // 触发搜索错误事件
    emit('search-error', {
      error: errorMessage,
      stats: loadStats.value,
      retryCount: retryCount
    })
  } finally {
    clearTimeout(skeletonTimer)
    showSkeleton.value = false
    loading.value = false
    const loadTime = Date.now() - startTime
    if (loadTime > 3000) {
      console.warn(`群聊搜索加载耗时: ${loadTime}ms，建议优化`)
    }
    // 更新平均加载时间
    const totalTime = loadStats.value.avgLoadTime * (loadStats.value.attemptCount - 1) + loadTime
    loadStats.value.avgLoadTime = totalTime / loadStats.value.attemptCount
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
      ElMessage.info(`群聊ID: ${formatChatId(response.data.data.chat_id)}`)
      showCreateDialog.value = false
      resetCreateForm()
      
      // 刷新用户信息（确保有creator_id用于筛选）
      if (authStore.isAuthenticated && !authStore.user) {
        try {
          await authStore.fetchUserInfo()
        } catch (error) {
          console.error('获取用户信息失败:', error)
        }
      }
      
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

// 调试搜索功能
const debugSearch = () => {
  console.log('=== 群聊搜索调试信息 ===')
  console.log('当前搜索状态:', {
    chatId: searchForm.chatId,
    keyword: searchForm.keyword,
    loading: loading.value,
    chatRoomsCount: chatRooms.value.length,
    total: total.value,
    currentPage: currentPage.value
  })
  console.log('加载统计:', loadStats.value)
  console.log('用户群组:', userGroups.value)
  
  // 手动触发搜索
  console.log('手动触发搜索...')
  handleSearch().then(() => {
    console.log('搜索完成，当前结果:', {
      chatRoomsCount: chatRooms.value.length,
      total: total.value,
      results: chatRooms.value
    })
  })
}

// 初始化
onMounted(async () => {
  // 并行加载，避免阻塞
  Promise.all([
    loadUserGroups(),
    handleSearch()
  ]).catch(error => {
    console.error('初始化加载失败:', error)
  })
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

/* 性能优化样式 */
.virtual-scroll-container {
  max-height: 600px;
  overflow-y: auto;
}

.scroll-hint {
  background: #f0f9ff;
  border: 1px solid #91d5ff;
  border-radius: 4px;
  padding: 8px 12px;
  margin-bottom: 16px;
  color: #1890ff;
  font-size: 14px;
}

.performance-notice {
  margin-bottom: 16px;
}

.skeleton-container {
  padding: 20px 0;
}

/* 卡片渲染优化 */
.chat-room-card {
  contain: layout style;
  will-change: transform;
}

/* 减少重排重绘 */
.room-header,
.room-stats,
.room-actions {
  contain: layout;
}
</style>