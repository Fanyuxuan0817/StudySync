<template>
  <div class="checkin-container">
    <!-- 页面标题 -->
    <div class="page-header animate-fadeInUp">
      <div class="header-content">
        <h1 class="page-title">
          <span class="title-icon">✏️</span>
          学习打卡
        </h1>
        <p class="page-subtitle">记录每一天的学习成果，见证自己的成长</p>
      </div>
      <div class="date-badge">
        <span class="date-icon">📅</span>
        <span class="date-text">{{ todayDate }}</span>
      </div>
    </div>

    <!-- 打卡表单 -->
    <div class="checkin-form-wrapper animate-fadeInUp delay-100">
      <h2 class="section-title">
        <span class="section-icon">📝</span>
        今日学习记录
      </h2>
      <el-card class="checkin-card" :body-style="{ padding: '32px' }">
        <el-form
          :model="checkinForm"
          :rules="checkinRules"
          ref="checkinFormRef"
          label-width="120px"
          class="checkin-form"
          @keyup.enter="handleCheckin"
        >
          <el-form-item label="学习计划" prop="plan_id">
            <el-select
              v-model="checkinForm.plan_id"
              placeholder="请选择学习计划"
              size="large"
              class="custom-select"
            >
              <el-option
                v-for="plan in plans"
                :key="plan.plan_id"
                :label="plan.title"
                :value="plan.plan_id"
              >
                <span class="option-icon">📚</span>
                {{ plan.title }}
              </el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="学习时长" prop="hours">
            <div class="hours-input-wrapper">
              <el-input-number
                v-model.number="checkinForm.hours"
                :min="0.5"
                :max="12"
                :step="0.5"
                placeholder="请输入学习时长"
                size="large"
                class="custom-input-number"
              />
              <span class="unit-label">小时</span>
            </div>
          </el-form-item>

          <el-form-item label="学习内容" prop="content">
            <el-input
              v-model="checkinForm.content"
              type="textarea"
              placeholder="记录今天学习了什么内容..."
              :rows="4"
              size="large"
              class="custom-textarea"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="打卡日期" prop="checkin_date">
            <el-date-picker
              v-model="checkinForm.checkin_date"
              type="date"
              placeholder="选择打卡日期"
              size="large"
              class="custom-date-picker"
            />
          </el-form-item>

          <el-form-item class="form-actions">
            <el-button
              type="primary"
              class="submit-btn"
              @click="handleCheckin"
              :loading="loading"
              size="large"
            >
              <span v-if="!loading" class="btn-content">
                <span class="btn-icon">✨</span>
                <span>提交打卡</span>
              </span>
              <span v-else>提交中...</span>
            </el-button>
          </el-form-item>
        </el-form>

        <el-alert
          v-if="error"
          type="error"
          :title="error"
          show-icon
          class="form-alert error"
          closable
          @close="error = ''"
        />
        <el-alert
          v-if="success"
          type="success"
          :title="success"
          show-icon
          class="form-alert success"
          closable
          @close="success = ''"
        />
      </el-card>
    </div>

    <!-- 最近打卡记录 -->
    <div class="recent-checkins-wrapper animate-fadeInUp delay-200">
      <h2 class="section-title">
        <span class="section-icon">📋</span>
        最近打卡记录
      </h2>
      <el-card class="records-card" :body-style="{ padding: '24px' }">
        <div v-if="recentCheckins.length > 0" class="records-list">
          <div
            v-for="(record, index) in recentCheckins"
            :key="record.checkin_id"
            class="record-item"
            :style="{ animationDelay: `${index * 100}ms` }"
          >
            <div class="record-icon">📖</div>
            <div class="record-content">
              <div class="record-header">
                <span class="record-date">{{ formatDate(record.date) }}</span>
                <span class="record-hours">{{ record.hours }} 小时</span>
              </div>
              <p class="record-text">{{ record.content }}</p>
            </div>
            <div class="record-actions">
              <el-button
                type="primary"
                link
                size="small"
                @click="handleEdit(record)"
                class="action-btn edit"
              >
                编辑
              </el-button>
              <el-button
                type="danger"
                link
                size="small"
                @click="handleDelete(record)"
                class="action-btn delete"
              >
                删除
              </el-button>
            </div>
          </div>
        </div>
        <div v-else class="no-records">
          <div class="empty-illustration">
            <span class="empty-icon">📝</span>
          </div>
          <p class="empty-text">暂无打卡记录</p>
          <p class="empty-tip">完成第一次打卡，开启你的学习之旅</p>
        </div>
      </el-card>
    </div>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑打卡记录"
      width="520px"
      class="custom-dialog"
      destroy-on-close
    >
      <el-form
        :model="editForm"
        :rules="checkinRules"
        ref="editFormRef"
        label-width="100px"
        class="edit-form"
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
        <el-form-item label="学习时长" prop="hours">
          <el-input-number
            v-model.number="editForm.hours"
            :min="0.5"
            :max="12"
            :step="0.5"
            placeholder="请输入学习时长"
            style="width: 150px"
          />
          <span class="form-unit">小时</span>
        </el-form-item>
        <el-form-item label="学习内容" prop="content">
          <el-input
            v-model="editForm.content"
            type="textarea"
            placeholder="请输入学习内容"
            :rows="4"
            maxlength="500"
            show-word-limit
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
        <div class="dialog-footer">
          <el-button @click="editDialogVisible = false" size="large">取消</el-button>
          <el-button type="primary" @click="handleUpdateCheckin" :loading="editLoading" size="large">
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
        <p class="confirm-text">确定要删除这条打卡记录吗？</p>
        <p class="confirm-subtext">删除后将无法恢复</p>
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

// 今天的日期
const todayDate = computed(() => {
  const date = new Date()
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  const weekday = weekdays[date.getDay()]
  const month = date.getMonth() + 1
  const day = date.getDate()
  return `${month}月${day}日 ${weekday}`
})

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

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  const month = date.getMonth() + 1
  const day = date.getDate()
  return `${month}月${day}日`
}

// 提交打卡
const handleCheckin = async () => {
  if (!checkinFormRef.value) return

  try {
    await checkinFormRef.value.validate()
    loading.value = true
    error.value = ''
    success.value = ''

    const formattedDate = new Date(checkinForm.checkin_date)
    const dateOnly = formattedDate.toISOString().split('T')[0]

    await userStore.createCheckin({
      ...checkinForm,
      checkin_date: dateOnly
    })
    success.value = '🎉 打卡成功！继续保持！'

    // 重置表单
    setTimeout(() => {
      checkinForm.hours = 2
      checkinForm.content = ''
      checkinForm.checkin_date = new Date()
    }, 1500)

    // 刷新记录
    await fetchRecentCheckins()
  } catch (err) {
    error.value = err.response?.data?.detail || '打卡失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 获取最近打卡记录
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

    const formattedDate = new Date(editForm.checkin_date)
    const dateOnly = formattedDate.toISOString().split('T')[0]

    await api.checkins.updateCheckin(currentCheckinId.value, {
      ...editForm,
      checkin_date: dateOnly
    })

    success.value = '✅ 编辑成功！'
    editDialogVisible.value = false

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

    success.value = '🗑️ 删除成功！'
    deleteDialogVisible.value = false

    await fetchRecentCheckins()
  } catch (err) {
    error.value = err.response?.data?.detail || '删除失败，请稍后重试'
  } finally {
    deleteLoading.value = false
  }
}

// 生命周期
onMounted(async () => {
  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.fetchUserInfo()
  }
  await userStore.fetchPlans()
  await fetchRecentCheckins()
})
</script>

<style scoped>
.checkin-container {
  padding: 0;
}

/* ===== 页面头部 ===== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding: 24px 32px;
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.05) 0%, rgba(107, 203, 119, 0.05) 100%);
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

.date-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}

.date-icon {
  font-size: 20px;
}

.date-text {
  font-size: 15px;
  font-weight: 600;
  color: #2D3436;
}

/* ===== 区块标题 ===== */
.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #2D3436;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.section-icon {
  font-size: 20px;
}

/* ===== 打卡表单 ===== */
.checkin-form-wrapper {
  margin-bottom: 32px;
}

.checkin-card {
  border-radius: 20px;
}

.checkin-form {
  max-width: 600px;
}

.hours-input-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.unit-label {
  font-size: 14px;
  color: #636E72;
}

.form-unit {
  margin-left: 8px;
  color: #636E72;
  font-size: 14px;
}

.form-actions {
  margin-top: 8px;
  margin-bottom: 0;
}

.submit-btn {
  height: 52px;
  padding: 0 40px;
  border-radius: 16px !important;
  font-size: 16px;
  font-weight: 600;
}

.btn-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-icon {
  font-size: 18px;
}

.form-alert {
  margin-top: 16px;
  border-radius: 12px !important;
}

.form-alert.error {
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
  20%, 40%, 60%, 80% { transform: translateX(5px); }
}

/* ===== 选择器选项 ===== */
.option-icon {
  margin-right: 8px;
}

/* ===== 最近打卡记录 ===== */
.recent-checkins-wrapper {
  margin-bottom: 32px;
}

.records-card {
  border-radius: 20px;
}

.records-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.record-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 16px;
  transition: all 0.3s ease;
  animation: slideIn 0.4s ease-out forwards;
  opacity: 0;
  transform: translateX(-20px);
}

@keyframes slideIn {
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.record-item:hover {
  background: rgba(255, 107, 107, 0.05);
  transform: translateX(4px);
}

.record-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.record-content {
  flex: 1;
  min-width: 0;
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.record-date {
  font-size: 14px;
  font-weight: 600;
  color: #2D3436;
}

.record-hours {
  font-size: 13px;
  color: #FF6B6B;
  font-weight: 600;
  padding: 4px 12px;
  background: rgba(255, 107, 107, 0.1);
  border-radius: 20px;
}

.record-text {
  font-size: 14px;
  color: #636E72;
  line-height: 1.6;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.record-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.action-btn {
  font-size: 13px;
}

.action-btn.edit {
  color: #4D96FF !important;
}

.action-btn.delete {
  color: #FF6B6B !important;
}

/* ===== 无记录状态 ===== */
.no-records {
  text-align: center;
  padding: 48px 24px;
}

.empty-illustration {
  width: 80px;
  height: 80px;
  margin: 0 auto 16px;
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(107, 203, 119, 0.1) 100%);
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
  margin-bottom: 8px;
}

.empty-tip {
  font-size: 14px;
  color: #636E72;
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
.delay-200 { animation-delay: 0.2s; }

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
    gap: 16px;
    text-align: center;
    padding: 20px;
  }

  .page-title {
    font-size: 22px;
  }

  .checkin-form :deep(.el-form-item__label) {
    float: none;
    display: block;
    text-align: left;
    margin-bottom: 8px;
  }

  .checkin-form :deep(.el-form-item__content) {
    margin-left: 0 !important;
  }

  .record-item {
    flex-direction: column;
    gap: 12px;
  }

  .record-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
