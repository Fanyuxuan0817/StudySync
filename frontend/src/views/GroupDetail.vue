<template>
  <div class="group-detail-container">
    <!-- 顶部导航栏 -->
    <div class="group-detail-header animate-fadeInUp">
      <el-button type="text" @click="goBack" class="back-button">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
      <h1 class="page-title">
        <span class="title-icon">👥</span>
        群聊详情
      </h1>
      <div class="header-actions">
        <el-button type="text" @click="showSettingsDialog" v-if="isOwner" class="settings-btn">
          <el-icon><Setting /></el-icon>
          设置
        </el-button>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <el-skeleton :loading="loading" animated>
      <template #template>
        <div class="skeleton-wrapper">
          <el-skeleton-item variant="image" class="skeleton-avatar" />
          <el-skeleton-item variant="h2" class="skeleton-title" />
          <el-skeleton-item variant="p" class="skeleton-desc" />
          <el-skeleton-item variant="p" class="skeleton-stats" />
        </div>
      </template>
      
      <!-- 群聊基本信息展示区 -->
      <div class="group-info-section animate-fadeInUp delay-100">
        <div class="group-avatar-container">
          <div class="avatar-wrapper">
            <el-avatar :size="100" class="group-avatar">
              {{ groupInfo.name?.charAt(0) || '群' }}
            </el-avatar>
            <div class="avatar-ring"></div>
          </div>
        </div>
        <h2 class="group-name">{{ groupInfo.name }}</h2>
        <p class="group-description">{{ groupInfo.description || '暂无描述' }}</p>
        <div class="group-stats">
          <div class="stat-item">
            <span class="stat-value">{{ groupInfo.member_count || 0 }}</span>
            <span class="stat-label">成员</span>
          </div>
          <div class="stat-item clickable" @click="goToGroupChat">
            <span class="stat-value">{{ todayCheckinCount || 0 }}</span>
            <span class="stat-label">今日打卡</span>
          </div>
          <div class="stat-item clickable" @click="goToGroupChat">
            <span class="stat-value">{{ checkinRate || 0 }}%</span>
            <span class="stat-label">打卡率</span>
          </div>
        </div>
        <div class="group-actions">
          <el-button type="primary" @click="joinGroup" v-if="!isMember" size="large" class="action-btn">
            <span class="btn-icon">➕</span>
            加入群组
          </el-button>
          <el-button type="success" @click="goToGroupChat" v-if="isMember" size="large" class="action-btn">
            <span class="btn-icon">💬</span>
            进入群聊
          </el-button>
          <el-button type="danger" @click="leaveGroup" v-else-if="!isOwner" size="large" class="action-btn">
            <span class="btn-icon">🚪</span>
            退出群组
          </el-button>
        </div>
      </div>
      
      <!-- 群公告 -->
      <div class="group-announcement-section animate-fadeInUp delay-200">
        <div class="section-header">
          <h3 class="section-title">
            <span class="title-icon">📢</span>
            群公告
          </h3>
          <el-button type="primary" link @click="editAnnouncement" v-if="isOwner" class="edit-btn">
            <span class="btn-icon">✏️</span>
            编辑
          </el-button>
        </div>
        <div class="announcement-card">
          <div class="announcement-content">
            {{ groupInfo.announcement || '暂无公告' }}
          </div>
        </div>
      </div>
      
      <!-- 群成员管理区 -->
      <div class="group-members-section animate-fadeInUp delay-300">
        <div class="section-header">
          <h3 class="section-title">
            <span class="title-icon">👤</span>
            群成员
          </h3>
          <el-input
            v-model="memberSearchQuery"
            placeholder="搜索成员"
            clearable
            class="member-search"
            @input="searchMembers"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
        
        <el-card :body-style="{ padding: '0' }" class="members-card">
          <div v-if="filteredMembers.length > 0">
            <el-table :data="filteredMembers" class="custom-table" stripe>
              <el-table-column label="头像" width="80">
                <template #default="scope">
                  <el-avatar :size="44" class="member-avatar">
                    {{ scope.row.username?.charAt(0) || '用' }}
                  </el-avatar>
                </template>
              </el-table-column>
              <el-table-column prop="username" label="用户名" min-width="120">
                <template #default="scope">
                  <div class="user-cell">
                    <span class="username">{{ scope.row.username }}</span>
                    <el-tag v-if="scope.row.role === 'owner'" size="small" class="owner-tag">
                      群主
                    </el-tag>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="角色" width="100">
                <template #default="scope">
                  <span class="role-text">{{ scope.row.role === 'owner' ? '群主' : '成员' }}</span>
                </template>
              </el-table-column>
              <el-table-column label="加入时间" width="140">
                <template #default="scope">
                  <span class="time-text">{{ formatDate(scope.row.joined_at) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="最近打卡" width="140">
                <template #default="scope">
                  <span class="checkin-text" :class="{ 'no-checkin': !scope.row.last_checkin_date }">
                    {{ scope.row.last_checkin_date ? formatDate(scope.row.last_checkin_date) : '未打卡' }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="scope">
                  <el-button size="small" @click="viewMemberDetail(scope.row)" class="detail-btn">
                    详情
                  </el-button>
                  <el-button 
                    size="small" 
                    type="danger" 
                    @click="removeMember(scope.row.user_id)" 
                    v-if="isOwner && scope.row.role !== 'owner'"
                    class="remove-btn"
                  >
                    移除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <div v-else class="no-members">
            <div class="empty-state">
              <div class="empty-illustration">
                <span class="empty-icon">👤</span>
              </div>
              <p class="empty-text">暂无成员</p>
            </div>
          </div>
        </el-card>
      </div>
    </el-skeleton>
    
    <!-- 群设置对话框 -->
    <el-dialog
      v-model="settingsDialogVisible"
      title="群设置"
      width="520px"
      class="custom-dialog"
      destroy-on-close
    >
      <el-form
        :model="settingsForm"
        :rules="settingsRules"
        ref="settingsFormRef"
        label-width="100px"
        class="settings-form"
      >
        <el-form-item label="群名称" prop="name">
          <el-input v-model="settingsForm.name" placeholder="请输入群名称" />
        </el-form-item>
        <el-form-item label="群描述" prop="description">
          <el-input
            v-model="settingsForm.description"
            type="textarea"
            placeholder="请输入群描述"
            :rows="3"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="每日打卡">
          <el-checkbox v-model="settingsForm.daily_checkin_required">
            每天至少 1 次打卡
          </el-checkbox>
        </el-form-item>
        <el-form-item label="群公告">
          <el-input
            v-model="settingsForm.announcement"
            type="textarea"
            placeholder="请输入群公告"
            :rows="3"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="settingsDialogVisible = false" size="large">取消</el-button>
          <el-button type="primary" @click="saveSettings" size="large">
            <span class="btn-icon">💾</span>
            保存
          </el-button>
          <el-button type="danger" @click="confirmDissolveGroup" size="large">
            <span class="btn-icon">🗑️</span>
            解散
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 编辑公告对话框 -->
    <el-dialog
      v-model="announcementDialogVisible"
      title="编辑群公告"
      width="520px"
      class="custom-dialog"
      destroy-on-close
    >
      <el-form
        :model="announcementForm"
        :rules="announcementRules"
        ref="announcementFormRef"
        label-width="100px"
        class="announcement-form"
      >
        <el-form-item label="公告内容" prop="content">
          <el-input
            v-model="announcementForm.content"
            type="textarea"
            placeholder="请输入群公告"
            :rows="5"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="announcementDialogVisible = false" size="large">取消</el-button>
          <el-button type="primary" @click="saveAnnouncement" size="large">
            <span class="btn-icon">💾</span>
            保存
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 成员详情对话框 -->
    <el-dialog
      v-model="memberDetailDialogVisible"
      title="成员详情"
      width="400px"
      class="custom-dialog"
    >
      <div v-if="selectedMember" class="member-detail">
        <div class="member-avatar-large">
          <el-avatar :size="80" class="detail-avatar">
            {{ selectedMember.username?.charAt(0) || '用' }}
          </el-avatar>
          <div class="avatar-ring"></div>
        </div>
        <h4 class="member-name">{{ selectedMember.username }}</h4>
        <div class="detail-info">
          <div class="info-item">
            <span class="info-label">角色</span>
            <span class="info-value">{{ selectedMember.role === 'owner' ? '群主' : '成员' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">加入时间</span>
            <span class="info-value">{{ formatDate(selectedMember.joined_at) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">最近打卡</span>
            <span class="info-value" :class="{ 'no-checkin': !selectedMember.last_checkin_date }">
              {{ selectedMember.last_checkin_date ? formatDate(selectedMember.last_checkin_date) : '未打卡' }}
            </span>
          </div>
          <div class="info-item" v-if="selectedMember.week_checkin_days !== undefined">
            <span class="info-label">本周打卡</span>
            <span class="info-value">{{ selectedMember.week_checkin_days }} 天</span>
          </div>
          <div class="info-item" v-if="selectedMember.avg_hours_per_day !== undefined">
            <span class="info-label">平均时长</span>
            <span class="info-value">{{ selectedMember.avg_hours_per_day }} 小时/天</span>
          </div>
        </div>
      </div>
      <div v-else class="empty-detail">
        <div class="empty-illustration">
          <span class="empty-icon">👤</span>
        </div>
        <p class="empty-text">暂无成员信息</p>
      </div>
    </el-dialog>
    
    <!-- 确认对话框 -->
    <el-dialog
      v-model="confirmDialogVisible"
      :title="confirmDialogTitle"
      width="360px"
      class="custom-dialog confirm-dialog"
    >
      <div class="confirm-content">
        <div class="confirm-icon">⚠️</div>
        <p class="confirm-text">{{ confirmDialogContent }}</p>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="confirmDialogVisible = false" size="large">取消</el-button>
          <el-button type="danger" @click="confirmAction" size="large">
            确认
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft, Bell, UserFilled, Search, Setting } from '@element-plus/icons-vue'
import { useAuthStore } from '../store/modules/auth'
import { useUserStore } from '../store/modules/user'
import { ElMessage } from 'element-plus'
import api from '../api'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const userStore = useUserStore()

// 状态变量
const loading = ref(true)
const groupId = ref(route.params.id)
const groupInfo = ref({})
const members = ref([])
const filteredMembers = ref([])
const memberSearchQuery = ref('')
const todayCheckinCount = ref(0)
const checkinRate = ref(0)
const isMember = ref(false)
const isOwner = ref(false)

// 对话框状态
const settingsDialogVisible = ref(false)
const announcementDialogVisible = ref(false)
const memberDetailDialogVisible = ref(false)
const confirmDialogVisible = ref(false)

// 表单数据
const settingsForm = reactive({
  name: '',
  description: '',
  daily_checkin_required: true,
  announcement: ''
})

const announcementForm = reactive({
  content: ''
})

const selectedMember = ref(null)

// 确认对话框数据
const confirmDialogTitle = ref('')
const confirmDialogContent = ref('')
const confirmActionCallback = ref(null)

// 表单验证规则
const settingsRules = {
  name: [
    { required: true, message: '请输入群名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ]
}

const announcementRules = {
  content: [
    { max: 500, message: '公告内容不能超过 500 个字符', trigger: 'blur' }
  ]
}

// 计算属性
const settingsFormRef = ref(null)
const announcementFormRef = ref(null)

// 方法
const goBack = () => {
  router.back()
}

const fetchGroupInfo = async () => {
  loading.value = true
  try {
    // 获取群组基本信息
    const groupResponse = await api.groups.getGroups()
    const allGroups = [...groupResponse.data.data.created, ...groupResponse.data.data.joined]
    const currentGroup = allGroups.find(g => g.group_id == groupId.value)
    
    if (currentGroup) {
      groupInfo.value = currentGroup
      
      // 检查用户是否是成员
      isMember.value = true
      
      // 检查用户是否是群主
      isOwner.value = currentGroup.creator_id === authStore.user?.id
    } else {
      // 如果不在用户的群组列表中，尝试获取群组详情
      try {
        const membersResponse = await api.groups.getGroupMembers(groupId.value)
        groupInfo.value = {
          group_id: groupId.value,
          name: '未知群组',
          description: '',
          member_count: membersResponse.data.data.total_members
        }
        isMember.value = false
        isOwner.value = false
      } catch (error) {
        console.error('获取群组信息失败:', error)
        ElMessage.error('获取群组信息失败')
      }
    }
    
    // 获取群成员列表
    await fetchMembers()
    
    // 获取群组统计数据
    await fetchGroupStats()
  } catch (error) {
    console.error('获取群组信息失败:', error)
    ElMessage.error('获取群组信息失败')
  } finally {
    loading.value = false
  }
}

const fetchMembers = async () => {
  try {
    const response = await api.groups.getGroupMembers(groupId.value)
    members.value = response.data.data.members
    filteredMembers.value = [...members.value]
  } catch (error) {
    console.error('获取群成员失败:', error)
    ElMessage.error('获取群成员失败')
  }
}

const fetchGroupStats = async () => {
  try {
    const response = await api.groups.getGroupStats(groupId.value)
    todayCheckinCount.value = response.data.data.today_checked_in_count
    checkinRate.value = response.data.data.checkin_rate
  } catch (error) {
    console.error('获取群组统计数据失败:', error)
    // 静默失败，使用默认值
  }
}

const searchMembers = () => {
  if (!memberSearchQuery.value) {
    filteredMembers.value = [...members.value]
    return
  }
  
  const query = memberSearchQuery.value.toLowerCase()
  filteredMembers.value = members.value.filter(member => 
    member.username.toLowerCase().includes(query)
  )
}

const joinGroup = async () => {
  try {
    await api.groups.joinGroup(groupId.value)
    ElMessage.success('加入群组成功')
    await fetchGroupInfo()
  } catch (error) {
    console.error('加入群组失败:', error)
    ElMessage.error('加入群组失败')
  }
}

const leaveGroup = () => {
  confirmDialogTitle.value = '退出群组'
  confirmDialogContent.value = '确定要退出该群组吗？'
  confirmActionCallback.value = async () => {
    try {
      await api.groups.leaveGroup(groupId.value)
      ElMessage.success('退出群组成功')
      router.push('/groups')
    } catch (error) {
      console.error('退出群组失败:', error)
      ElMessage.error('退出群组失败')
    }
  }
  confirmDialogVisible.value = true
}

const showSettingsDialog = () => {
  settingsForm.name = groupInfo.value.name || ''
  settingsForm.description = groupInfo.value.description || ''
  settingsForm.daily_checkin_required = groupInfo.value.daily_checkin_required !== false
  settingsForm.announcement = groupInfo.value.announcement || ''
  settingsDialogVisible.value = true
}

const saveSettings = async () => {
  if (!settingsFormRef.value) return
  
  try {
    await settingsFormRef.value.validate()
    
    // 调用更新群组API
    await api.groups.updateGroup(groupId.value, {
      name: settingsForm.name,
      description: settingsForm.description,
      daily_checkin_required: settingsForm.daily_checkin_required
    })
    
    // 更新本地数据
    groupInfo.value.name = settingsForm.name
    groupInfo.value.description = settingsForm.description
    groupInfo.value.daily_checkin_required = settingsForm.daily_checkin_required
    groupInfo.value.announcement = settingsForm.announcement
    
    settingsDialogVisible.value = false
    ElMessage.success('保存设置成功')
  } catch (error) {
    console.error('保存设置失败:', error)
    ElMessage.error(error.response?.data?.detail || '保存设置失败')
  }
}

const editAnnouncement = () => {
  announcementForm.content = groupInfo.value.announcement || ''
  announcementDialogVisible.value = true
}

const saveAnnouncement = async () => {
  if (!announcementFormRef.value) return
  
  try {
    await announcementFormRef.value.validate()
    
    // 这里需要实现更新群公告的API调用
    // 暂时使用模拟数据
    groupInfo.value.announcement = announcementForm.content
    
    announcementDialogVisible.value = false
    ElMessage.success('保存公告成功')
  } catch (error) {
    console.error('保存公告失败:', error)
    ElMessage.error('保存公告失败')
  }
}

const viewMemberDetail = (member) => {
  selectedMember.value = member
  memberDetailDialogVisible.value = true
}

const removeMember = (userId) => {
  confirmDialogTitle.value = '移除成员'
  confirmDialogContent.value = '确定要移除该成员吗？'
  confirmActionCallback.value = async () => {
    try {
      await api.groups.removeMember(groupId.value, userId)
      ElMessage.success('移除成员成功')
      await fetchMembers()
    } catch (error) {
      console.error('移除成员失败:', error)
      ElMessage.error('移除成员失败')
    }
  }
  confirmDialogVisible.value = true
}

const confirmDissolveGroup = () => {
  confirmDialogTitle.value = '解散群组'
  confirmDialogContent.value = '确定要解散该群组吗？此操作不可恢复。'
  confirmActionCallback.value = async () => {
    try {
      // 调用后端删除群组API
      await api.groups.deleteGroup(groupId.value)
      ElMessage.success('解散群组成功')
      router.push('/groups')
    } catch (error) {
      console.error('解散群组失败:', error)
      ElMessage.error(error.response?.data?.detail || '解散群组失败')
    }
  }
  confirmDialogVisible.value = true
}

const confirmAction = () => {
  if (confirmActionCallback.value) {
    confirmActionCallback.value()
  }
  confirmDialogVisible.value = false
}

const goToGroupChat = () => {
  router.push({
    path: `/chat/${groupId.value}`,
    query: { name: groupInfo.value.name }
  })
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
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
  
  // 获取群组信息
  await fetchGroupInfo()
})
</script>

<style scoped>
.group-detail-container {
  padding: 0;
}

/* ===== 页面头部 ===== */
.group-detail-header {
  display: flex;
  align-items: center;
  margin-bottom: 32px;
  padding: 24px 32px;
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.05) 0%, rgba(77, 150, 255, 0.05) 100%);
  border-radius: 24px;
  border: 1px solid rgba(255, 107, 107, 0.1);
}

.back-button {
  margin-right: 20px;
  font-size: 15px;
  color: #636E72;
}

.back-button:hover {
  color: #FF6B6B;
}

.page-title {
  flex: 1;
  font-size: 24px;
  font-weight: 700;
  color: #2D3436;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-icon {
  font-size: 28px;
}

.header-actions {
  margin-left: 20px;
}

.settings-btn {
  font-size: 15px;
  color: #636E72;
}

.settings-btn:hover {
  color: #FF6B6B;
}

/* ===== 骨架屏 ===== */
.skeleton-wrapper {
  padding: 40px;
  text-align: center;
}

.skeleton-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  margin: 0 auto 20px;
}

.skeleton-title {
  width: 60%;
  margin: 20px auto;
  height: 28px;
}

.skeleton-desc {
  width: 80%;
  margin: 0 auto 10px;
  height: 20px;
}

.skeleton-stats {
  width: 70%;
  margin: 10px auto;
  height: 60px;
}

/* ===== 群聊信息区 ===== */
.group-info-section {
  text-align: center;
  margin-bottom: 40px;
  padding: 40px;
  background: white;
  border-radius: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.group-avatar-container {
  margin-bottom: 24px;
}

.avatar-wrapper {
  position: relative;
  display: inline-block;
}

.group-avatar {
  font-size: 40px;
  font-weight: 700;
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
  color: white;
  border: 4px solid white;
  box-shadow: 0 4px 16px rgba(255, 107, 107, 0.3);
}

.avatar-ring {
  position: absolute;
  inset: -6px;
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

.group-name {
  font-size: 26px;
  font-weight: 700;
  margin-bottom: 12px;
  color: #2D3436;
}

.group-description {
  font-size: 15px;
  color: #636E72;
  margin-bottom: 28px;
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
}

/* ===== 统计信息 ===== */
.group-stats {
  display: flex;
  justify-content: center;
  gap: 48px;
  margin-bottom: 32px;
}

.stat-item {
  text-align: center;
  padding: 16px 24px;
  border-radius: 16px;
  background: rgba(0, 0, 0, 0.02);
  transition: all 0.3s ease;
  min-width: 100px;
}

.stat-item:hover,
.stat-item.clickable:hover {
  background: rgba(255, 107, 107, 0.08);
  transform: translateY(-2px);
}

.stat-item.clickable {
  cursor: pointer;
}

.stat-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.2;
}

.stat-label {
  display: block;
  font-size: 14px;
  color: #636E72;
  margin-top: 8px;
}

/* ===== 操作按钮 ===== */
.group-actions {
  margin-top: 24px;
  display: flex;
  gap: 16px;
  justify-content: center;
}

.action-btn {
  height: 48px;
  padding: 0 28px;
  border-radius: 14px !important;
  font-size: 15px;
  font-weight: 600;
}

.action-btn .btn-icon {
  margin-right: 6px;
  font-size: 16px;
}

/* ===== 区块标题 ===== */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #2D3436;
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
}

.section-title .title-icon {
  font-size: 22px;
}

.edit-btn {
  font-weight: 500;
}

.edit-btn .btn-icon {
  margin-right: 4px;
}

/* ===== 群公告 ===== */
.group-announcement-section {
  margin-bottom: 40px;
}

.announcement-card {
  background: linear-gradient(135deg, rgba(255, 217, 61, 0.08) 0%, rgba(255, 179, 71, 0.08) 100%);
  border-radius: 16px;
  padding: 24px;
  border: 1px solid rgba(255, 179, 71, 0.15);
}

.announcement-content {
  font-size: 15px;
  color: #2D3436;
  line-height: 1.8;
  white-space: pre-wrap;
}

/* ===== 群成员 ===== */
.group-members-section {
  margin-bottom: 40px;
}

.member-search {
  width: 280px;
}

.member-search :deep(.el-input__wrapper) {
  border-radius: 12px !important;
}

.members-card {
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

.custom-table :deep(.el-table__header th) {
  background: linear-gradient(180deg, #FFF8F5 0%, #FAFAF8 100%);
  font-weight: 600;
  color: #2D3436;
}

.custom-table :deep(.el-table__row) {
  transition: background-color 0.2s ease;
}

.custom-table :deep(.el-table__row:hover) {
  background-color: rgba(255, 107, 107, 0.03) !important;
}

.member-avatar {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
  color: white;
  font-weight: 600;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.username {
  font-weight: 500;
  color: #2D3436;
}

.owner-tag {
  background: rgba(255, 107, 107, 0.15);
  border-color: rgba(255, 107, 107, 0.3);
  color: #FF6B6B;
  border-radius: 12px;
}

.role-text {
  color: #636E72;
}

.time-text,
.checkin-text {
  color: #636E72;
  font-size: 13px;
}

.checkin-text.no-checkin {
  color: #B2BEC3;
}

.detail-btn {
  border-radius: 8px;
}

.remove-btn {
  border-radius: 8px;
}

/* ===== 空状态 ===== */
.no-members {
  padding: 48px 24px;
}

.empty-state {
  text-align: center;
}

.empty-illustration {
  width: 80px;
  height: 80px;
  margin: 0 auto 16px;
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(77, 150, 255, 0.1) 100%);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-icon {
  font-size: 40px;
}

.empty-text {
  font-size: 16px;
  font-weight: 600;
  color: #2D3436;
  margin: 0;
}

/* ===== 成员详情对话框 ===== */
.member-detail {
  text-align: center;
  padding: 20px 0;
}

.member-avatar-large {
  position: relative;
  display: inline-block;
  margin-bottom: 20px;
}

.detail-avatar {
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
  color: white;
  border: 4px solid white;
  box-shadow: 0 4px 16px rgba(255, 107, 107, 0.3);
}

.member-avatar-large .avatar-ring {
  inset: -6px;
}

.member-name {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 24px;
  color: #2D3436;
}

.detail-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 12px;
}

.info-label {
  color: #636E72;
  font-size: 14px;
}

.info-value {
  font-weight: 600;
  color: #2D3436;
  font-size: 14px;
}

.info-value.no-checkin {
  color: #B2BEC3;
}

.empty-detail {
  text-align: center;
  padding: 40px 0;
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
  color: #2D3436;
  margin: 0;
}

.dialog-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.settings-form :deep(.el-input__wrapper),
.settings-form :deep(.el-textarea__inner),
.announcement-form :deep(.el-input__wrapper),
.announcement-form :deep(.el-textarea__inner) {
  border-radius: 12px !important;
}

/* ===== 动画类 ===== */
.animate-fadeInUp {
  animation: fadeInUp 0.6s ease-out forwards;
}

.delay-100 { animation-delay: 0.1s; }
.delay-200 { animation-delay: 0.2s; }
.delay-300 { animation-delay: 0.3s; }

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
  .group-detail-header {
    flex-direction: column;
    gap: 16px;
    text-align: center;
    padding: 20px;
  }
  
  .back-button {
    margin-right: 0;
  }
  
  .page-title {
    font-size: 20px;
  }
  
  .header-actions {
    margin-left: 0;
  }
  
  .group-info-section {
    padding: 24px;
  }
  
  .group-name {
    font-size: 22px;
  }
  
  .group-stats {
    flex-direction: column;
    gap: 16px;
  }
  
  .stat-item {
    width: 100%;
  }
  
  .group-actions {
    flex-direction: column;
  }
  
  .action-btn {
    width: 100%;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .member-search {
    width: 100%;
  }
}
</style>
