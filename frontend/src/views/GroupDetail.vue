<template>
  <div class="group-detail-container">
    <!-- 顶部导航栏 -->
    <div class="group-detail-header">
      <el-button type="text" @click="goBack" class="back-button">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
      <h1 class="page-title">群聊详情</h1>
      <div class="header-actions">
        <el-button type="text" @click="showSettingsDialog" v-if="isOwner">
          <el-icon><Setting /></el-icon>
          设置
        </el-button>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <el-skeleton :loading="loading" animated>
      <template #template>
        <el-skeleton-item variant="image" style="width: 100px; height: 100px; border-radius: 50%; margin: 0 auto;" />
        <el-skeleton-item variant="h2" style="width: 60%; margin: 20px auto;" />
        <el-skeleton-item variant="p" style="width: 80%; margin: 0 auto;" />
        <el-skeleton-item variant="p" style="width: 70%; margin: 10px auto;" />
        <el-skeleton-item variant="h3" style="width: 40%; margin: 30px 0 20px;" />
        <el-skeleton-item variant="p" style="width: 100%;" />
        <el-skeleton-item variant="p" style="width: 100%;" />
        <el-skeleton-item variant="h3" style="width: 40%; margin: 30px 0 20px;" />
        <el-skeleton-item variant="p" style="width: 100%;" />
        <el-skeleton-item variant="p" style="width: 100%;" />
      </template>
      
      <!-- 群聊基本信息展示区 -->
      <div class="group-info-section">
        <div class="group-avatar-container">
          <el-avatar :size="100" class="group-avatar">
            {{ groupInfo.name?.charAt(0) || '群' }}
          </el-avatar>
        </div>
        <h2 class="group-name">{{ groupInfo.name }}</h2>
        <p class="group-description">{{ groupInfo.description || '暂无描述' }}</p>
        <div class="group-stats">
          <div class="stat-item">
            <span class="stat-value">{{ groupInfo.member_count || 0 }}</span>
            <span class="stat-label">成员</span>
          </div>
          <div class="stat-item" @click="goToGroupChat" style="cursor: pointer;">
            <span class="stat-value">{{ todayCheckinCount || 0 }}</span>
            <span class="stat-label">今日打卡</span>
          </div>
          <div class="stat-item" @click="goToGroupChat" style="cursor: pointer;">
            <span class="stat-value">{{ checkinRate || 0 }}%</span>
            <span class="stat-label">打卡率</span>
          </div>
        </div>
        <div class="group-actions">
          <el-button type="primary" @click="joinGroup" v-if="!isMember">
            加入群组
          </el-button>
          <el-button type="success" @click="goToGroupChat" v-if="isMember">
            进入群聊
          </el-button>
          <el-button type="danger" @click="leaveGroup" v-else-if="!isOwner">
            退出群组
          </el-button>
        </div>
      </div>
      
      <!-- 群公告 -->
      <div class="group-announcement-section">
        <h3 class="section-title">
          <el-icon><Bell /></el-icon>
          群公告
        </h3>
        <div class="announcement-content">
          {{ groupInfo.announcement || '暂无公告' }}
        </div>
        <el-button type="text" @click="editAnnouncement" v-if="isOwner">
          编辑公告
        </el-button>
      </div>
      
      <!-- 群成员管理区 -->
      <div class="group-members-section">
        <div class="section-header">
          <h3 class="section-title">
            <el-icon><UserFilled /></el-icon>
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
        
        <el-card :body-style="{ padding: '20px' }">
          <div v-if="filteredMembers.length > 0">
            <el-table :data="filteredMembers" style="width: 100%">
              <el-table-column label="头像" width="80">
                <template #default="scope">
                  <el-avatar :size="40">
                    {{ scope.row.username?.charAt(0) || '用' }}
                  </el-avatar>
                </template>
              </el-table-column>
              <el-table-column prop="username" label="用户名">
                <template #default="scope">
                  <div>
                    <span>{{ scope.row.username }}</span>
                    <el-tag v-if="scope.row.role === 'owner'" size="small" type="primary" class="role-tag">
                      群主
                    </el-tag>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="角色" width="100">
                <template #default="scope">
                  <span>{{ scope.row.role === 'owner' ? '群主' : '成员' }}</span>
                </template>
              </el-table-column>
              <el-table-column label="加入时间" width="180">
                <template #default="scope">
                  <span>{{ formatDate(scope.row.joined_at) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="最近打卡" width="180">
                <template #default="scope">
                  <span>{{ scope.row.last_checkin_date ? formatDate(scope.row.last_checkin_date) : '未打卡' }}</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120">
                <template #default="scope">
                  <el-button size="small" @click="viewMemberDetail(scope.row)">
                    详情
                  </el-button>
                  <el-button size="small" type="danger" @click="removeMember(scope.row.user_id)" v-if="isOwner && scope.row.role !== 'owner'">
                    移除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <div v-else class="no-members">
            <el-empty description="暂无成员" />
          </div>
        </el-card>
      </div>
    </el-skeleton>
    
    <!-- 群设置对话框 -->
    <el-dialog
      v-model="settingsDialogVisible"
      title="群设置"
      width="500px"
    >
      <el-form
        :model="settingsForm"
        :rules="settingsRules"
        ref="settingsFormRef"
        label-width="100px"
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
          />
        </el-form-item>
        <el-form-item label="每日打卡规则">
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
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="settingsDialogVisible = false">
            取消
          </el-button>
          <el-button type="primary" @click="saveSettings">
            保存
          </el-button>
          <el-button type="danger" @click="confirmDissolveGroup">
            解散群组
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 编辑公告对话框 -->
    <el-dialog
      v-model="announcementDialogVisible"
      title="编辑群公告"
      width="500px"
    >
      <el-form
        :model="announcementForm"
        :rules="announcementRules"
        ref="announcementFormRef"
        label-width="100px"
      >
        <el-form-item label="公告内容" prop="content">
          <el-input
            v-model="announcementForm.content"
            type="textarea"
            placeholder="请输入群公告"
            :rows="5"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="announcementDialogVisible = false">
            取消
          </el-button>
          <el-button type="primary" @click="saveAnnouncement">
            保存
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 成员详情对话框 -->
    <el-dialog
      v-model="memberDetailDialogVisible"
      title="成员详情"
      width="400px"
    >
      <div v-if="selectedMember" class="member-detail">
        <div class="member-avatar">
          <el-avatar :size="80">
            {{ selectedMember.username?.charAt(0) || '用' }}
          </el-avatar>
        </div>
        <h4 class="member-name">{{ selectedMember.username }}</h4>
        <div class="member-info-item">
          <span class="info-label">角色：</span>
          <span class="info-value">{{ selectedMember.role === 'owner' ? '群主' : '成员' }}</span>
        </div>
        <div class="member-info-item">
          <span class="info-label">加入时间：</span>
          <span class="info-value">{{ formatDate(selectedMember.joined_at) }}</span>
        </div>
        <div class="member-info-item">
          <span class="info-label">最近打卡：</span>
          <span class="info-value">{{ selectedMember.last_checkin_date ? formatDate(selectedMember.last_checkin_date) : '未打卡' }}</span>
        </div>
        <div class="member-info-item" v-if="selectedMember.week_checkin_days !== undefined">
          <span class="info-label">本周打卡：</span>
          <span class="info-value">{{ selectedMember.week_checkin_days }} 天</span>
        </div>
        <div class="member-info-item" v-if="selectedMember.avg_hours_per_day !== undefined">
          <span class="info-label">平均时长：</span>
          <span class="info-value">{{ selectedMember.avg_hours_per_day }} 小时/天</span>
        </div>
      </div>
      <div v-else>
        <el-empty description="暂无成员信息" />
      </div>
    </el-dialog>
    
    <!-- 确认对话框 -->
    <el-dialog
      v-model="confirmDialogVisible"
      :title="confirmDialogTitle"
      width="400px"
    >
      <p>{{ confirmDialogContent }}</p>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="confirmDialogVisible = false">
            取消
          </el-button>
          <el-button type="danger" @click="confirmAction">
            确认
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft, Bell, UserFilled, Search, Setting, UserFilled as UserIcon } from '@element-plus/icons-vue'
import { useAuthStore } from '../store/modules/auth'
import { useUserStore } from '../store/modules/user'
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
        elMessage.error('获取群组信息失败')
      }
    }
    
    // 获取群成员列表
    await fetchMembers()
    
    // 获取群组统计数据
    await fetchGroupStats()
  } catch (error) {
    console.error('获取群组信息失败:', error)
    elMessage.error('获取群组信息失败')
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
    elMessage.error('获取群成员失败')
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
    elMessage.success('加入群组成功')
    await fetchGroupInfo()
  } catch (error) {
    console.error('加入群组失败:', error)
    elMessage.error('加入群组失败')
  }
}

const leaveGroup = () => {
  confirmDialogTitle.value = '退出群组'
  confirmDialogContent.value = '确定要退出该群组吗？'
  confirmActionCallback.value = async () => {
    try {
      await api.groups.leaveGroup(groupId.value)
      elMessage.success('退出群组成功')
      router.push('/groups')
    } catch (error) {
      console.error('退出群组失败:', error)
      elMessage.error('退出群组失败')
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
    
    // 这里需要实现更新群组设置的API调用
    // 暂时使用模拟数据
    groupInfo.value.name = settingsForm.name
    groupInfo.value.description = settingsForm.description
    groupInfo.value.daily_checkin_required = settingsForm.daily_checkin_required
    groupInfo.value.announcement = settingsForm.announcement
    
    settingsDialogVisible.value = false
    elMessage.success('保存设置成功')
  } catch (error) {
    console.error('保存设置失败:', error)
    elMessage.error('保存设置失败')
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
    elMessage.success('保存公告成功')
  } catch (error) {
    console.error('保存公告失败:', error)
    elMessage.error('保存公告失败')
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
      elMessage.success('移除成员成功')
      await fetchMembers()
    } catch (error) {
      console.error('移除成员失败:', error)
      elMessage.error('移除成员失败')
    }
  }
  confirmDialogVisible.value = true
}

const confirmDissolveGroup = () => {
  confirmDialogTitle.value = '解散群组'
  confirmDialogContent.value = '确定要解散该群组吗？此操作不可恢复。'
  confirmActionCallback.value = async () => {
    try {
      // 这里需要实现解散群组的API调用
      // 暂时使用模拟数据
      elMessage.success('解散群组成功')
      router.push('/groups')
    } catch (error) {
      console.error('解散群组失败:', error)
      elMessage.error('解散群组失败')
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
    path: `/groups/${groupId.value}/chat`,
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

// 导入 Element Plus 消息组件
import { ElMessage } from 'element-plus'
</script>

<style scoped>
.group-detail-container {
  padding: 0 20px 20px;
}

.group-detail-header {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  padding-top: 20px;
}

.back-button {
  margin-right: 20px;
}

.page-title {
  flex: 1;
  font-size: 24px;
  color: #333;
  margin: 0;
}

.header-actions {
  margin-left: 20px;
}

.group-info-section {
  text-align: center;
  margin-bottom: 40px;
  padding: 30px;
  background-color: #f9f9f9;
  border-radius: 12px;
}

.group-avatar-container {
  margin-bottom: 20px;
}

.group-avatar {
  font-size: 40px;
  background-color: #409eff;
}

.group-name {
  font-size: 24px;
  font-weight: 500;
  margin-bottom: 10px;
  color: #333;
}

.group-description {
  font-size: 16px;
  color: #666;
  margin-bottom: 20px;
}

.group-stats {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-bottom: 30px;
}

.stat-item {
  text-align: center;
  padding: 10px;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.stat-item:hover {
  background-color: #f0f0f0;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 500;
  color: #409eff;
}

.stat-label {
  display: block;
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}

.group-actions {
  margin-top: 20px;
}

.group-announcement-section,
.group-members-section {
  margin-bottom: 40px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  font-size: 18px;
  font-weight: 500;
  color: #333;
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.section-title el-icon {
  margin-right: 10px;
}

.announcement-content {
  padding: 20px;
  background-color: #f0f9ff;
  border-radius: 8px;
  margin-bottom: 10px;
  line-height: 1.6;
}

.member-search {
  width: 300px;
}

.member-detail {
  text-align: center;
  padding: 20px 0;
}

.member-avatar {
  margin-bottom: 20px;
}

.member-name {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 20px;
  color: #333;
}

.member-info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  padding: 0 20px;
}

.info-label {
  color: #666;
}

.info-value {
  font-weight: 500;
  color: #333;
}

.role-tag {
  margin-left: 10px;
}

@media (max-width: 768px) {
  .group-detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .group-stats {
    flex-direction: column;
    gap: 20px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .member-search {
    width: 100%;
  }
  
  .el-table {
    font-size: 14px;
  }
  
  .el-table__column {
    padding: 8px;
  }
}
</style>