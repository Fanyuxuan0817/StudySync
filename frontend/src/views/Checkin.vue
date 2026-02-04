<template>
  <div class="checkin-container">
    <h1 class="page-title">学习打卡</h1>
    
    <div class="checkin-form-card">
      <el-card :body-style="{ padding: '30px' }">
        <h2 class="card-title">今日学习记录</h2>
        <el-form
          :model="checkinForm"
          :rules="checkinRules"
          ref="checkinFormRef"
          label-width="100px"
          class="checkin-form"
        >
          <el-form-item label="学习计划" prop="plan_id">
            <el-select
              v-model="checkinForm.plan_id"
              placeholder="请选择学习计划"
              style="width: 100%"
            >
              <el-option
                v-for="plan in plans"
                :key="plan.plan_id"
                :label="plan.title"
                :value="plan.plan_id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="学习时长（小时）" prop="hours">
            <el-input-number
              v-model.number="checkinForm.hours"
              :min="0.5"
              :max="12"
              :step="0.5"
              placeholder="请输入学习时长"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="学习内容" prop="content">
            <el-input
              v-model="checkinForm.content"
              type="textarea"
              placeholder="请输入学习内容"
              :rows="4"
            />
          </el-form-item>
          <el-form-item label="打卡日期" prop="checkin_date">
            <el-date-picker
              v-model="checkinForm.checkin_date"
              type="date"
              placeholder="选择打卡日期"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" class="submit-btn" @click="handleCheckin" :loading="loading">
              提交打卡
            </el-button>
          </el-form-item>
        </el-form>
        <el-alert
          v-if="error"
          type="error"
          :title="error"
          show-icon
          class="error-alert"
        />
        <el-alert
          v-if="success"
          type="success"
          :title="success"
          show-icon
          class="success-alert"
        />
      </el-card>
    </div>
    
    <div class="recent-checkins">
      <h2 class="card-title">最近打卡记录</h2>
      <el-card :body-style="{ padding: '20px' }">
        <div v-if="recentCheckins.length > 0">
          <el-table :data="recentCheckins" style="width: 100%">
            <el-table-column prop="date" label="打卡日期" width="150" />
            <el-table-column prop="hours" label="学习时长（小时）" width="150" />
            <el-table-column prop="content" label="学习内容" />
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="scope">
                <el-button type="primary" size="small" @click="handleEdit(scope.row)" style="margin-right: 8px">
                  编辑
                </el-button>
                <el-button type="danger" size="small" @click="handleDelete(scope.row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div v-else>
          <el-empty description="暂无打卡记录" />
        </div>
      </el-card>
    </div>
    
    <!-- 编辑打卡对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑打卡记录"
      width="500px"
    >
      <el-form
        :model="editForm"
        :rules="checkinRules"
        ref="editFormRef"
        label-width="100px"
      >
        <el-form-item label="学习计划" prop="plan_id">
          <el-select
            v-model="editForm.plan_id"
            placeholder="请选择学习计划"
            style="width: 100%"
          >
            <el-option
              v-for="plan in plans"
              :key="plan.plan_id"
              :label="plan.title"
              :value="plan.plan_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="学习时长（小时）" prop="hours">
          <el-input-number
            v-model.number="editForm.hours"
            :min="0.5"
            :max="12"
            :step="0.5"
            placeholder="请输入学习时长"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="学习内容" prop="content">
          <el-input
            v-model="editForm.content"
            type="textarea"
            placeholder="请输入学习内容"
            :rows="4"
          />
        </el-form-item>
        <el-form-item label="打卡日期" prop="checkin_date">
          <el-date-picker
            v-model="editForm.checkin_date"
            type="date"
            placeholder="选择打卡日期"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleUpdateCheckin" :loading="editLoading">保存修改</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 删除确认对话框 -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="确认删除"
      width="300px"
    >
      <p>您确定要删除这条打卡记录吗？</p>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deleteDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="confirmDelete" :loading="deleteLoading">确认删除</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/modules/auth'
import { useUserStore } from '../store/modules/user'
import api from '../api'

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()
const checkinFormRef = ref(null)
const editFormRef = ref(null)
const loading = ref(false)
const editLoading = ref(false)
const deleteLoading = ref(false)
const error = ref('')
const success = ref('')
const recentCheckins = ref([])
const editDialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const currentCheckinId = ref(null)

// 表单数据
const checkinForm = reactive({
  plan_id: '',
  hours: 2,
  content: '',
  checkin_date: new Date()
})

// 编辑表单数据
const editForm = reactive({
  plan_id: '',
  hours: 2,
  content: '',
  checkin_date: new Date()
})

const checkinRules = {
  plan_id: [
    { required: true, message: '请选择学习计划', trigger: 'change' }
  ],
  hours: [
    { required: true, message: '请输入学习时长', trigger: ['blur', 'change'] },
    { type: 'number', min: 0.5, message: '学习时长至少 0.5 小时', trigger: ['blur', 'change'] }
  ],
  content: [
    { required: true, message: '请输入学习内容', trigger: 'blur' },
    { min: 5, message: '学习内容至少 5 个字符', trigger: 'blur' }
  ],
  checkin_date: [
    { required: true, message: '请选择打卡日期', trigger: 'change' }
  ]
}

// 计算属性
const plans = computed(() => userStore.plans)

// 方法
const handleCheckin = async () => {
  if (!checkinFormRef.value) return
  
  try {
    await checkinFormRef.value.validate()
    loading.value = true
    error.value = ''
    success.value = ''
    
    // 处理日期格式，只保留日期部分
    const formattedDate = new Date(checkinForm.checkin_date)
    const dateOnly = formattedDate.toISOString().split('T')[0]
    
    await userStore.createCheckin({
      ...checkinForm,
      checkin_date: dateOnly
    })
    success.value = '打卡成功！'
    
    // 重置表单
    setTimeout(() => {
      checkinForm.hours = 2
      checkinForm.content = ''
      checkinForm.checkin_date = new Date()
    }, 1500)
  } catch (err) {
    error.value = err.response?.data?.detail || '打卡失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

const fetchRecentCheckins = async () => {
  try {
    const response = await api.checkins.getCheckins({ page_size: 10 })
    recentCheckins.value = response.data.data.items.map(item => ({
      checkin_id: item.checkin_id,
      date: item.date,
      hours: item.hours,
      content: item.content,
      plan_id: item.plan_id
    }))
  } catch (error) {
    console.error('获取最近打卡记录失败:', error)
  }
}

// 编辑打卡记录
const handleEdit = (row) => {
  currentCheckinId.value = row.checkin_id
  editForm.plan_id = row.plan_id
  editForm.hours = row.hours
  editForm.content = row.content
  editForm.checkin_date = new Date(row.date)
  editDialogVisible.value = true
}

// 更新打卡记录
const handleUpdateCheckin = async () => {
  if (!editFormRef.value) return
  
  try {
    await editFormRef.value.validate()
    editLoading.value = true
    error.value = ''
    
    // 处理日期格式，只保留日期部分
    const formattedDate = new Date(editForm.checkin_date)
    const dateOnly = formattedDate.toISOString().split('T')[0]
    
    await api.checkins.updateCheckin(currentCheckinId.value, {
      ...editForm,
      checkin_date: dateOnly
    })
    
    success.value = '编辑成功！'
    editDialogVisible.value = false
    
    // 重新获取打卡记录
    await fetchRecentCheckins()
  } catch (err) {
    error.value = err.response?.data?.detail || '编辑失败，请稍后重试'
  } finally {
    editLoading.value = false
  }
}

// 删除打卡记录
const handleDelete = (row) => {
  currentCheckinId.value = row.checkin_id
  deleteDialogVisible.value = true
}

// 确认删除
const confirmDelete = async () => {
  try {
    deleteLoading.value = true
    error.value = ''
    
    await api.checkins.deleteCheckin(currentCheckinId.value)
    
    success.value = '删除成功！'
    deleteDialogVisible.value = false
    
    // 重新获取打卡记录
    await fetchRecentCheckins()
  } catch (err) {
    error.value = err.response?.data?.detail || '删除失败，请稍后重试'
  } finally {
    deleteLoading.value = false
  }
}

// 生命周期
onMounted(async () => {
  // 获取用户信息
  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.fetchUserInfo()
  }
  // 获取计划
  await userStore.fetchPlans()
  // 获取最近打卡
  await fetchRecentCheckins()
})
</script>

<style scoped>
.checkin-container {
  padding: 0;
}

.page-title {
  font-size: 24px;
  color: #333;
  margin-bottom: 30px;
}

.checkin-form-card {
  margin-bottom: 30px;
}

.card-title {
  font-size: 18px;
  color: #333;
  margin-bottom: 20px;
  font-weight: 500;
}

.checkin-form {
  max-width: 600px;
}

.submit-btn {
  width: 100%;
  font-size: 16px;
  padding: 10px 0;
}

.error-alert,
.success-alert {
  margin-top: 20px;
}

.recent-checkins {
  margin-top: 40px;
}
</style>
