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
      
      <!-- AI学习评估 -->
      <div class="ai-evaluation-card">
        <h2 class="card-title">AI学习评估</h2>
        <el-card :body-style="{ padding: '20px' }" class="ai-card-content">
          <div v-if="isAiAnalyzing" class="ai-loading">
            <div class="loading-container">
              <el-skeleton :rows="10" animated />
              <div class="loading-text">
                <el-icon class="loading-icon"><Loading /></el-icon>
                <span>AI正在分析您的学习数据...</span>
              </div>
              <div class="loading-steps">
                <el-progress :percentage="loadingProgress" :stroke-width="8" status="success" />
                <span class="loading-step-text">{{ loadingStep }}</span>
              </div>
            </div>
          </div>
          <div v-else-if="aiEvaluation" class="ai-evaluation-content">
            <!-- 学习评分 -->
            <div class="ai-score-section">
              <h3 class="ai-section-title">学习评分</h3>
              <div class="ai-score-card">
                <div class="ai-total-score">
                  <el-progress
                    type="dashboard"
                    :percentage="aiEvaluation.score.total"
                    :color="getAiScoreColor(aiEvaluation.score.total)"
                    :format="formatAiScore"
                    :stroke-width="15"
                    :width="120"
                  />
                </div>
                <div class="ai-score-details">
                  <div class="ai-score-item">
                    <span class="ai-score-label">打卡频率</span>
                    <el-progress
                      :percentage="aiEvaluation.score.frequency"
                      :color="getAiScoreColor(aiEvaluation.score.frequency)"
                      :show-text="false"
                      :stroke-width="8"
                    />
                    <span class="ai-score-value">{{ aiEvaluation.score.frequency }}%</span>
                  </div>
                  <div class="ai-score-item">
                    <span class="ai-score-label">学习时长</span>
                    <el-progress
                      :percentage="aiEvaluation.score.duration"
                      :color="getAiScoreColor(aiEvaluation.score.duration)"
                      :show-text="false"
                      :stroke-width="8"
                    />
                    <span class="ai-score-value">{{ aiEvaluation.score.duration }}%</span>
                  </div>
                  <div class="ai-score-item">
                    <span class="ai-score-label">学习稳定性</span>
                    <el-progress
                      :percentage="aiEvaluation.score.stability"
                      :color="getAiScoreColor(aiEvaluation.score.stability)"
                      :show-text="false"
                      :stroke-width="8"
                    />
                    <span class="ai-score-value">{{ aiEvaluation.score.stability }}%</span>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 学习总结 -->
            <div class="ai-summary-section">
              <h3 class="ai-section-title">学习总结</h3>
              <el-card :body-style="{ padding: '15px' }" class="ai-summary-card">
                <div class="ai-summary-item">
                  <span class="ai-summary-label">打卡频率：</span>
                  <span class="ai-summary-value">{{ aiEvaluation.summary.checkin_frequency }}</span>
                </div>
                <div class="ai-summary-item">
                  <span class="ai-summary-label">学习趋势：</span>
                  <span class="ai-summary-value">{{ aiEvaluation.summary.learning_trend }}</span>
                </div>
                <div class="ai-summary-item">
                  <span class="ai-summary-label">稳定性：</span>
                  <span class="ai-summary-value">{{ aiEvaluation.summary.stability_level }}</span>
                </div>
              </el-card>
            </div>
            
            <!-- 问题与建议 -->
            <div class="ai-issues-suggestions">
              <div class="ai-issues-section">
                <h3 class="ai-section-title">存在问题</h3>
                <el-card :body-style="{ padding: '15px' }" class="ai-issues-card">
                  <ul v-if="aiEvaluation.issues && aiEvaluation.issues.length > 0">
                    <li v-for="(issue, index) in aiEvaluation.issues" :key="index" class="ai-issue-item">
                      {{ issue }}
                    </li>
                  </ul>
                  <p v-else class="ai-no-issues">暂无问题</p>
                </el-card>
              </div>
              
              <div class="ai-suggestions-section">
                <h3 class="ai-section-title">改进建议</h3>
                <el-card :body-style="{ padding: '15px' }" class="ai-suggestions-card">
                  <ul v-if="aiEvaluation.suggestions && aiEvaluation.suggestions.length > 0">
                    <li v-for="(suggestion, index) in aiEvaluation.suggestions" :key="index" class="ai-suggestion-item">
                      {{ suggestion }}
                    </li>
                  </ul>
                  <p v-else class="ai-no-suggestions">暂无建议</p>
                </el-card>
              </div>
            </div>
            
            <!-- 推荐学习时长 -->
            <div class="ai-recommended-section">
              <h3 class="ai-section-title">推荐学习时长</h3>
              <el-card :body-style="{ padding: '15px' }" class="ai-recommended-card">
                <div class="ai-recommended-hours">
                  <span class="ai-hours-label">建议每日学习时长：</span>
                  <span class="ai-hours-value">{{ aiEvaluation.recommended_hours }} 小时</span>
                </div>
              </el-card>
            </div>
            
            <!-- 重新分析按钮 -->
            <div class="ai-reanalyze-section">
              <el-button 
                type="primary" 
                @click="fetchAiEvaluation" 
                class="reanalyze-btn"
                :disabled="isAiAnalyzing"
              >
                <el-icon v-if="isAiAnalyzing"><Loading /></el-icon>
                {{ isAiAnalyzing ? '分析中...' : '重新分析' }}
              </el-button>
            </div>
          </div>
          <div v-else class="ai-no-data">
            <el-empty description="点击下方按钮开始AI学习分析" />
            <el-button 
              type="primary" 
              @click="fetchAiEvaluation" 
              class="analyze-btn"
              :disabled="isAiAnalyzing"
            >
              开始学习分析
            </el-button>
          </div>
          <el-alert
            v-if="aiError"
            type="error"
            :title="aiError"
            show-icon
            class="ai-error-alert"
          ></el-alert>
        </el-card>
      </div>
      
      <!-- 学习计划 -->
      <div class="plans-card">
        <h2 class="card-title">我的学习计划</h2>
        <el-card :body-style="{ padding: '20px' }" class="plans-card-content">
          <div v-if="plans.length > 0">
            <div class="plans-header">
              <el-button type="primary" @click="showCreatePlanDialog" class="create-plan-btn">
                创建计划
              </el-button>
              <el-button @click="goToChatRooms">
                <el-icon><ChatDotRound /></el-icon>
                群聊中心
              </el-button>
            </div>
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
            <div class="plan-actions">
              <el-button type="primary" @click="showCreatePlanDialog">
                创建计划
              </el-button>
              <el-button @click="goToChatRooms">
                <el-icon><ChatDotRound /></el-icon>
                群聊中心
              </el-button>
            </div>
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
import { Loading } from '@element-plus/icons-vue'
import api from '../api'

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()
const weeklyChartRef = ref(null)
const weeklyChart = ref(null)
const createPlanDialogVisible = ref(false)
const planFormRef = ref(null)

// AI评估相关状态
const aiEvaluation = ref(null)
const isAiAnalyzing = ref(false)
const aiError = ref('')
const loadingProgress = ref(0)
const loadingStep = ref('准备分析数据...')

// 性能优化：使用防抖函数
const debounce = (func, delay) => {
  let timeoutId
  return (...args) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => func.apply(null, args), delay)
  }
}

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

const goToChatRooms = () => {
  router.push('/chat-rooms')
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
    ElMessage.success('学习计划创建成功！')
  } catch (error) {
    console.error('创建计划失败:', error)
    const errorMessage = error.response?.data?.message || '创建计划失败，请稍后重试'
    ElMessage.error(errorMessage)
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

// AI评估相关方法
const fetchAiEvaluation = async () => {
  try {
    isAiAnalyzing.value = true
    aiError.value = ''
    loadingProgress.value = 0
    loadingStep.value = '准备分析数据...'
    
    // 检查认证状态
    const token = localStorage.getItem('token')
    if (!token) {
      aiError.value = '请先登录系统'
      isAiAnalyzing.value = false
      return
    }
    
    // 获取本周开始日期
    const now = new Date()
    const weekStart = new Date(now)
    weekStart.setDate(now.getDate() - now.getDay())
    const weekStartDate = weekStart.toISOString().split('T')[0]
    
    // 模拟进度更新
    const updateProgress = (progress, step) => {
      loadingProgress.value = progress
      loadingStep.value = step
    }
    
    // 尝试使用流式API
    try {
      updateProgress(20, '获取打卡数据...')
      
      // 使用fetch API直接处理流式响应
      const response = await fetch(`/api/ai/weekly_report/stream?week_date=${weekStartDate}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (!response.ok) {
        throw new Error('API请求失败')
      }
      
      updateProgress(40, '解析打卡数据...')
      
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let fullAnalysis = ''
      
      // 初始化AI评估数据
      aiEvaluation.value = {
        week_start: weekStart,
        week_end: new Date(weekStart.getTime() + 6 * 24 * 60 * 60 * 1000),
        generated_at: new Date(),
        score: {
          total: 0,
          frequency: 0,
          duration: 0,
          stability: 0
        },
        summary: {
          checkin_frequency: '分析中...',
          learning_trend: '分析中...',
          stability_level: '分析中...'
        },
        issues: [],
        suggestions: [],
        recommended_hours: 0
      }
      
      updateProgress(60, 'AI正在分析数据...')
      
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        
        buffer += decoder.decode(value, { stream: true })
        
        // 处理每一行JSON数据
        const lines = buffer.split('\n')
        buffer = lines.pop() // 保存最后一行不完整的数据
        
        for (const line of lines) {
          if (!line.trim()) continue
          
          try {
            const data = JSON.parse(line)
            
            switch (data.type) {
              case 'basic':
                // 更新基本数据
                aiEvaluation.value.score = data.data.score
                updateProgress(70, '计算学习评分...')
                break
              case 'analysis':
                // 累积分析内容
                fullAnalysis += data.data.content
                // 简单解析分析内容，更新UI
                updateAiEvaluationFromAnalysis(fullAnalysis)
                updateProgress(85, '生成分析报告...')
                break
              case 'complete':
                // 分析完成
                updateProgress(100, '分析完成')
                break
              case 'error':
                // 分析错误
                aiError.value = data.data.message
                break
            }
          } catch (parseError) {
            console.error('解析流式数据失败:', parseError)
          }
        }
      }
    } catch (streamError) {
      console.error('流式API失败，使用传统API:', streamError)
      updateProgress(70, '使用传统API获取数据...')
      // 回退到传统API
      const response = await api.ai.getWeeklyReport({ week_date: weekStartDate })
      aiEvaluation.value = response.data.data
      updateProgress(100, '分析完成')
    }
  } catch (err) {
    console.error('获取AI评估失败:', err)
    aiError.value = err.response?.data?.message || '获取AI评估失败，请稍后重试'
  } finally {
    isAiAnalyzing.value = false
  }
}

// 使用防抖优化UI更新
const updateAiEvaluationFromAnalysis = debounce((analysis) => {
  // 简单解析分析内容，更新UI
  // 这里可以根据实际的AI输出格式进行更复杂的解析
  if (analysis.includes('存在问题')) {
    const issuesMatch = analysis.match(/存在问题[\s\S]*?(?=改进建议|$)/)
    if (issuesMatch) {
      const issuesText = issuesMatch[0]
      const issues = issuesText
        .split('\n')
        .filter(line => line.trim() && !line.includes('存在问题'))
        .map(line => line.trim().replace(/^[•-\s]+/, ''))
      if (issues.length > 0) {
        aiEvaluation.value.issues = issues
      }
    }
  }
  
  if (analysis.includes('改进建议')) {
    const suggestionsMatch = analysis.match(/改进建议[\s\S]*?(?=推荐学习时长|$)/)
    if (suggestionsMatch) {
      const suggestionsText = suggestionsMatch[0]
      const suggestions = suggestionsText
        .split('\n')
        .filter(line => line.trim() && !line.includes('改进建议'))
        .map(line => line.trim().replace(/^[•-\s]+/, ''))
      if (suggestions.length > 0) {
        aiEvaluation.value.suggestions = suggestions
      }
    }
  }
  
  if (analysis.includes('推荐学习时长')) {
    const hoursMatch = analysis.match(/推荐学习时长.*?(\d+(\.\d+)?)小时/)
    if (hoursMatch) {
      aiEvaluation.value.recommended_hours = parseFloat(hoursMatch[1])
    }
  }
  
  // 更新学习总结
  aiEvaluation.value.summary = {
    checkin_frequency: '分析完成',
    learning_trend: '分析完成',
    stability_level: '分析完成'
  }
}, 300) // 300ms防抖，减少UI更新频率

const getAiScoreColor = (score) => {
  if (score >= 80) {
    return '#67C23A'
  } else if (score >= 60) {
    return '#E6A23C'
  } else {
    return '#F56C6C'
  }
}

const formatAiScore = (percentage) => {
  return `${percentage}分`
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

.plans-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.plan-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 20px;
}

.create-plan-btn {
  font-size: 14px;
}

.chart-container {
  min-height: 300px;
}

/* AI学习评估样式 */
.ai-evaluation-card {
  margin-top: 30px;
}

.ai-card-content {
  min-height: 400px;
}

.ai-loading {
  padding: 20px 0;
}

.loading-container {
  position: relative;
}

.loading-text {
  text-align: center;
  margin-top: 20px;
  color: #666;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.loading-icon {
  animation: rotate 1.5s linear infinite;
}

.loading-steps {
  margin-top: 20px;
}

.loading-step-text {
  text-align: center;
  margin-top: 10px;
  color: #909399;
  font-size: 14px;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.ai-evaluation-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.ai-section-title {
  font-size: 16px;
  color: #666;
  margin-bottom: 15px;
  font-weight: 500;
}

.ai-score-section {
  margin-bottom: 20px;
}

.ai-score-card {
  display: flex;
  gap: 30px;
  align-items: center;
  flex-wrap: wrap;
}

.ai-total-score {
  flex-shrink: 0;
}

.ai-score-details {
  flex: 1;
  min-width: 300px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.ai-score-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.ai-score-label {
  font-size: 14px;
  color: #666;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ai-score-value {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.ai-summary-section,
.ai-recommended-section {
  margin-top: 20px;
}

.ai-summary-card,
.ai-issues-card,
.ai-suggestions-card,
.ai-recommended-card {
  min-height: 100px;
}

.ai-summary-item {
  margin-bottom: 10px;
  font-size: 14px;
}

.ai-summary-label {
  font-weight: 500;
  color: #333;
  margin-right: 10px;
}

.ai-summary-value {
  color: #666;
}

.ai-issues-suggestions {
  display: flex;
  gap: 20px;
  margin-top: 20px;
  flex-wrap: wrap;
}

.ai-issues-section,
.ai-suggestions-section {
  flex: 1;
  min-width: 300px;
}

.ai-issue-item,
.ai-suggestion-item {
  margin-bottom: 10px;
  padding-left: 20px;
  position: relative;
}

.ai-issue-item::before,
.ai-suggestion-item::before {
  content: '•';
  position: absolute;
  left: 0;
  color: #666;
}

.ai-no-issues,
.ai-no-suggestions {
  text-align: center;
  color: #999;
  padding: 20px 0;
}

.ai-recommended-hours {
  text-align: center;
  font-size: 16px;
}

.ai-hours-label {
  color: #666;
  margin-right: 10px;
}

.ai-hours-value {
  font-size: 20px;
  font-weight: bold;
  color: #409EFF;
}

.ai-no-data {
  text-align: center;
  padding: 40px 0;
}

.ai-error-alert {
  margin-top: 20px;
}

.analyze-btn {
  margin-top: 20px;
}

.ai-reanalyze-section {
  margin-top: 20px;
  text-align: center;
}

.reanalyze-btn {
  font-size: 14px;
  padding: 10px 20px;
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
  
  .ai-score-card {
    flex-direction: column;
    text-align: center;
  }
  
  .ai-issues-suggestions {
    flex-direction: column;
  }
}
</style>
