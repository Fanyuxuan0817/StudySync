<template>
  <div class="home-container">
    <div class="home-header">
      <h1>欢迎回来，{{ user?.username || '用户' }}</h1>
      <el-button type="primary" @click="navigateToCheckin" class="checkin-btn">
        去打卡
      </el-button>
    </div>
    
    <div class="home-content">
      <!-- 今日打卡状态 -->
      <div class="status-card">
        <h2 class="card-title">今日打卡状态</h2>
        <el-card :body-style="{ padding: '20px' }" class="status-card-content">
          <div v-if="todayCheckin" class="checked-in">
            <el-tag type="success" effect="dark">已打卡</el-tag>
            <p>今日学习时长：{{ todayCheckin.total_hours }} 小时</p>
            <p>打卡内容：{{ todayCheckin.checkins[0]?.content || '无' }}</p>
          </div>
          <div v-else class="not-checked-in">
            <el-tag type="warning" effect="dark">未打卡</el-tag>
            <p>今日还未打卡，快去记录你的学习情况吧！</p>
          </div>
        </el-card>
      </div>
      
      <!-- 本周学习进度 -->
      <div class="progress-card">
        <h2 class="card-title">本周学习进度</h2>
        <el-card :body-style="{ padding: '20px' }" class="progress-card-content">
          <div v-if="hasWeeklyProgress" class="chart-container">
            <div id="weeklyChart" ref="weeklyChartRef" style="width: 100%; height: 300px;"></div>
          </div>
          <div v-else class="no-progress">
            <el-empty description="无进度数据" />
            <p class="no-progress-tip">添加学习计划并完成打卡后，将显示本周学习进度</p>
          </div>
        </el-card>
      </div>
      
      <!-- 学习计划 -->
      <div class="plans-card">
        <h2 class="card-title">我的学习计划</h2>
        <el-card :body-style="{ padding: '20px' }" class="plans-card-content">
          <div v-if="plans.length > 0">
            <el-table :data="plans" style="width: 100%">
              <el-table-column prop="title" label="计划名称" width="200" />
              <el-table-column prop="daily_goal_hours" label="每日目标" />
              <el-table-column prop="start_date" label="开始日期" />
              <el-table-column prop="end_date" label="结束日期" />
              <el-table-column prop="progress" label="进度" min-width="200">
                <template #default="scope">
                  <div v-if="scope.row.progress && scope.row.progress.completion_rate !== undefined" class="progress-container">
                    <el-progress 
                      :percentage="scope.row.progress.completion_rate" 
                      :format="formatProgress"
                    />
                  </div>
                  <div v-else class="plan-no-progress">
                    <el-tag type="info" effect="plain">无进度</el-tag>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120">
                <template #default="scope">
                  <el-button 
                    type="danger" 
                    size="small" 
                    @click="handleDeletePlan(scope.row.plan_id)"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <div v-else class="no-plans">
            <el-empty description="暂无学习计划" />
            <el-button type="primary" @click="showCreatePlanDialog">
              创建计划
            </el-button>
          </div>
        </el-card>
      </div>
    </div>
    
    <!-- 创建计划对话框 -->
    <el-dialog
      v-model="createPlanDialogVisible"
      title="创建学习计划"
      width="500px"
    >
      <el-form
        :model="planForm"
        :rules="planRules"
        ref="planFormRef"
        label-width="100px"
      >
        <el-form-item label="计划名称" prop="title">
          <el-input v-model="planForm.title" placeholder="请输入计划名称" />
        </el-form-item>
        <el-form-item label="计划描述" prop="description">
          <el-input
            v-model="planForm.description"
            type="textarea"
            placeholder="请输入计划描述"
            :rows="3"
          />
        </el-form-item>
        <el-form-item label="每日目标（小时）" prop="daily_goal_hours">
          <el-input-number
            v-model="planForm.daily_goal_hours"
            :min="0.5"
            :max="10"
            :step="0.5"
            placeholder="请输入每日目标"
          />
        </el-form-item>
        <el-form-item label="开始日期" prop="start_date">
          <el-date-picker
            v-model="planForm.start_date"
            type="date"
            placeholder="选择开始日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束日期" prop="end_date">
          <el-date-picker
            v-model="planForm.end_date"
            type="date"
            placeholder="选择结束日期"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="createPlanDialogVisible = false">
            取消
          </el-button>
          <el-button type="primary" @click="handleCreatePlan">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/modules/auth'
import { useUserStore } from '../store/modules/user'
import * as echarts from 'echarts'
import { ElMessageBox, ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()
const weeklyChartRef = ref(null)
const weeklyChart = ref(null)
const createPlanDialogVisible = ref(false)
const planFormRef = ref(null)

// 表单数据
const planForm = ref({
  title: '',
  description: '',
  daily_goal_hours: 2,
  start_date: new Date(),
  end_date: null
})

const planRules = {
  title: [
    { required: true, message: '请输入计划名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  daily_goal_hours: [
    { required: true, message: '请输入每日目标', trigger: 'blur' }
  ],
  start_date: [
    { required: true, message: '请选择开始日期', trigger: 'change' }
  ]
}

// 计算属性
const user = computed(() => authStore.user)
const todayCheckin = computed(() => userStore.todayCheckin)
const plans = computed(() => userStore.plans)
const hasWeeklyProgress = computed(() => {
  // 检查是否有学习计划
  if (plans.value.length === 0) return false
  // 检查是否有今日打卡
  if (!todayCheckin.value) return false
  // 检查是否有学习时长
  return todayCheckin.value.total_hours > 0
})

// 方法
const navigateToCheckin = () => {
  router.push('/checkin')
}

const showCreatePlanDialog = () => {
  createPlanDialogVisible.value = true
}

const handleCreatePlan = async () => {
  if (!planFormRef.value) return
  
  try {
    await planFormRef.value.validate()
    
    // 转换日期格式为ISO字符串 (YYYY-MM-DD)
    const planData = {
      ...planForm.value,
      start_date: planForm.value.start_date.toISOString().split('T')[0],
      end_date: planForm.value.end_date ? planForm.value.end_date.toISOString().split('T')[0] : null
    }
    
    await userStore.createPlan(planData)
    createPlanDialogVisible.value = false
    // 重置表单
    planForm.value = {
      title: '',
      description: '',
      daily_goal_hours: 2,
      start_date: new Date(),
      end_date: null
    }
  } catch (error) {
    console.error('创建计划失败:', error)
    ElMessage.error('创建计划失败，请检查输入信息')
  }
}

const handleDeletePlan = async (planId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个学习计划吗？', '删除计划', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await userStore.deletePlan(planId)
    ElMessage.success('计划删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除计划失败:', error)
      ElMessage.error('删除计划失败')
    }
  }
}

const formatProgress = (percentage) => {
  return `${percentage}%`
}

// 初始化图表
const initWeeklyChart = () => {
  if (!weeklyChartRef.value) return
  
  weeklyChart.value = echarts.init(weeklyChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      }
    },
    legend: {
      data: ['学习时长（小时）']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: [
      {
        type: 'category',
        boundaryGap: false,
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      }
    ],
    yAxis: [
      {
        type: 'value',
        name: '学习时长（小时）'
      }
    ],
    series: [
      {
        name: '学习时长（小时）',
        type: 'line',
        stack: 'Total',
        areaStyle: {},
        emphasis: {
          focus: 'series'
        },
        data: [2, 3, 1.5, 4, 2.5, 3, 2.5]
      }
    ]
  }
  
  weeklyChart.value.setOption(option)
  
  // 响应式调整
  window.addEventListener('resize', () => {
    weeklyChart.value?.resize()
  })
}

// 生命周期
onMounted(async () => {
  // 获取用户信息
  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.fetchUserInfo()
  }
  // 获取今日打卡
  await userStore.fetchTodayCheckin()
  // 获取计划
  await userStore.fetchPlans()
  // 只有在有学习进度数据时才初始化图表
  if (hasWeeklyProgress.value) {
    initWeeklyChart()
  }
})
</script>

<style scoped>
.home-container {
  padding: 0;
}

.home-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.home-header h1 {
  font-size: 24px;
  color: #333;
}

.checkin-btn {
  font-size: 16px;
  padding: 10px 20px;
}

.home-content {
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

.status-card-content,
.progress-card-content,
.plans-card-content {
  min-height: 200px;
}

.checked-in {
  text-align: center;
  padding: 20px 0;
}

.not-checked-in {
  text-align: center;
  padding: 20px 0;
}

.no-plans {
  text-align: center;
  padding: 20px 0;
}

.no-plans .el-button {
  margin-top: 20px;
}

.no-progress {
  text-align: center;
  padding: 30px 0;
}

.no-progress-tip {
  margin-top: 15px;
  color: #909399;
  font-size: 14px;
}

.plan-no-progress {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 40px;
}

.chart-container {
  min-height: 300px;
}

@media (max-width: 768px) {
  .home-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .checkin-btn {
    align-self: flex-start;
  }
}
</style>
