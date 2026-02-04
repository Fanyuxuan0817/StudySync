<template>
  <div class="groups-container">
    <h1 class="page-title">学习群组</h1>
    
    <div class="groups-header">
      <el-button type="primary" @click="showCreateGroupDialog" class="create-group-btn">
        创建群组
      </el-button>
    </div>
    
    <div class="groups-content">
      <!-- 我的群组 -->
      <div class="my-groups">
        <h2 class="card-title">我的群组</h2>
        <el-card :body-style="{ padding: '20px' }">
          <div v-if="groups.created.length > 0 || groups.joined.length > 0">
            <!-- 我创建的群组 -->
            <div v-if="groups.created.length > 0" class="created-groups">
              <h3 class="section-title">我创建的群组</h3>
              <el-grid :column="3" :gutter="20">
                <el-grid-item v-for="group in groups.created" :key="group.group_id">
                  <el-card :body-style="{ padding: '15px' }" class="group-card">
                    <h4 class="group-name">{{ group.name }}</h4>
                    <p class="group-description">{{ group.description || '暂无描述' }}</p>
                    <p class="group-members">成员: {{ group.member_count }} 人</p>
                    <div class="group-actions">
                      <el-button size="small" @click="viewGroupMembers(group.group_id)">
                        查看成员
                      </el-button>
                      <el-button size="small" type="primary" @click="viewGroupCheckins(group.group_id)">
                        查看打卡
                      </el-button>
                    </div>
                  </el-card>
                </el-grid-item>
              </el-grid>
            </div>
            
            <!-- 我加入的群组 -->
            <div v-if="groups.joined.length > 0" class="joined-groups">
              <h3 class="section-title">我加入的群组</h3>
              <el-grid :column="3" :gutter="20">
                <el-grid-item v-for="group in groups.joined" :key="group.group_id">
                  <el-card :body-style="{ padding: '15px' }" class="group-card">
                    <h4 class="group-name">{{ group.name }}</h4>
                    <p class="group-description">{{ group.description || '暂无描述' }}</p>
                    <p class="group-members">成员: {{ group.member_count }} 人</p>
                    <p class="group-joined">加入时间: {{ group.joined_at }}</p>
                    <div class="group-actions">
                      <el-button size="small" @click="viewGroupMembers(group.group_id)">
                        查看成员
                      </el-button>
                      <el-button size="small" type="primary" @click="viewGroupCheckins(group.group_id)">
                        查看打卡
                      </el-button>
                    </div>
                  </el-card>
                </el-grid-item>
              </el-grid>
            </div>
          </div>
          <div v-else class="no-groups">
            <el-empty description="暂无群组" />
            <el-button type="primary" @click="showCreateGroupDialog">
              创建群组
            </el-button>
          </div>
        </el-card>
      </div>
      
      <!-- 群组打卡情况 -->
      <div v-if="selectedGroupId" class="group-checkins">
        <h2 class="card-title">{{ selectedGroupName }} - 打卡情况</h2>
        <el-card :body-style="{ padding: '20px' }">
          <el-form :inline="true" class="date-form">
            <el-form-item label="日期">
              <el-date-picker
                v-model="checkinDate"
                type="date"
                placeholder="选择日期"
                @change="fetchGroupCheckins"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="fetchGroupCheckins">
                查询
              </el-button>
            </el-form-item>
          </el-form>
          
          <div v-if="groupCheckins.checked_in.length > 0 || groupCheckins.not_checked_in.length > 0">
            <el-tabs v-model="activeTab">
              <el-tab-pane label="已打卡" name="checked_in">
                <el-table :data="groupCheckins.checked_in" style="width: 100%">
                  <el-table-column prop="username" label="用户名" width="150" />
                  <el-table-column prop="hours" label="学习时长（小时）" width="150" />
                  <el-table-column prop="checkin_time" label="打卡时间" />
                </el-table>
              </el-tab-pane>
              <el-tab-pane label="未打卡" name="not_checked_in">
                <el-table :data="groupCheckins.not_checked_in" style="width: 100%">
                  <el-table-column prop="username" label="用户名" />
                </el-table>
              </el-tab-pane>
            </el-tabs>
          </div>
          <div v-else class="no-checkins">
            <el-empty description="暂无打卡数据" />
          </div>
        </el-card>
      </div>
    </div>
    
    <!-- 创建群组对话框 -->
    <el-dialog
      v-model="createGroupDialogVisible"
      title="创建学习群组"
      width="500px"
    >
      <el-form
        :model="groupForm"
        :rules="groupRules"
        ref="groupFormRef"
        label-width="100px"
      >
        <el-form-item label="群组名称" prop="name">
          <el-input v-model="groupForm.name" placeholder="请输入群组名称" />
        </el-form-item>
        <el-form-item label="群组描述" prop="description">
          <el-input
            v-model="groupForm.description"
            type="textarea"
            placeholder="请输入群组描述"
            :rows="3"
          />
        </el-form-item>
        <el-form-item label="每日打卡规则">
          <el-checkbox v-model="groupForm.daily_checkin_required">
            每天至少 1 次打卡
          </el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="createGroupDialogVisible = false">
            取消
          </el-button>
          <el-button type="primary" @click="handleCreateGroup">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useAuthStore } from '../store/modules/auth'
import { useUserStore } from '../store/modules/user'
import api from '../api'

const authStore = useAuthStore()
const userStore = useUserStore()
const createGroupDialogVisible = ref(false)
const groupFormRef = ref(null)
const selectedGroupId = ref(null)
const selectedGroupName = ref('')
const activeTab = ref('checked_in')
const checkinDate = ref(new Date())
const groupCheckins = ref({
  checked_in: [],
  not_checked_in: []
})

// 表单数据
const groupForm = reactive({
  name: '',
  description: '',
  daily_checkin_required: true
})

const groupRules = {
  name: [
    { required: true, message: '请输入群组名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ]
}

// 计算属性
const groups = computed(() => userStore.groups || { created: [], joined: [] })

// 方法
const showCreateGroupDialog = () => {
  createGroupDialogVisible.value = true
}

const handleCreateGroup = async () => {
  if (!groupFormRef.value) return
  
  try {
    await groupFormRef.value.validate()
    
    const groupData = {
      name: groupForm.name,
      description: groupForm.description,
      daily_checkin_rule: {
        min_checkins_per_day: groupForm.daily_checkin_required ? 1 : 0
      }
    }
    
    await api.groups.createGroup(groupData)
    await userStore.fetchGroups()
    createGroupDialogVisible.value = false
    
    // 重置表单
    groupForm.name = ''
    groupForm.description = ''
    groupForm.daily_checkin_required = true
  } catch (error) {
    console.error('创建群组失败:', error)
  }
}

const viewGroupMembers = (groupId) => {
  // 查看群组成员
  console.log('查看群组成员:', groupId)
}

const viewGroupCheckins = (groupId, groupName) => {
  selectedGroupId.value = groupId
  selectedGroupName.value = groupName || groups.value.created.find(g => g.group_id === groupId)?.name || groups.value.joined.find(g => g.group_id === groupId)?.name || ''
  fetchGroupCheckins()
}

const fetchGroupCheckins = async () => {
  if (!selectedGroupId.value) return
  
  try {
    const response = await api.groups.getGroupCheckins(selectedGroupId.value, {
      date: checkinDate.value
    })
    groupCheckins.value = {
      checked_in: response.data.data.checked_in || [],
      not_checked_in: response.data.data.not_checked_in || []
    }
  } catch (error) {
    console.error('获取群组打卡情况失败:', error)
  }
}

// 生命周期
onMounted(async () => {
  // 获取用户信息
  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.fetchUserInfo()
  }
  // 获取群组
  await userStore.fetchGroups()
})
</script>

<style scoped>
.groups-container {
  padding: 0;
}

.page-title {
  font-size: 24px;
  color: #333;
  margin-bottom: 30px;
}

.groups-header {
  margin-bottom: 30px;
}

.create-group-btn {
  font-size: 16px;
  padding: 10px 20px;
}

.groups-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.card-title {
  font-size: 18px;
  color: #333;
  margin-bottom: 15px;
  font-weight: 500;
}

.section-title {
  font-size: 16px;
  color: #666;
  margin-bottom: 15px;
  margin-top: 20px;
}

.group-card {
  min-height: 200px;
}

.group-name {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 10px;
  color: #333;
}

.group-description {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
  line-height: 1.4;
}

.group-members {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.group-joined {
  font-size: 14px;
  color: #666;
  margin-bottom: 15px;
}

.group-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

.no-groups {
  text-align: center;
  padding: 40px 0;
}

.no-groups .el-button {
  margin-top: 20px;
}

.date-form {
  margin-bottom: 20px;
}

.no-checkins {
  text-align: center;
  padding: 40px 0;
}

@media (max-width: 768px) {
  .el-grid {
    grid-template-columns: 1fr;
  }
}
</style>
