<template>
  <div class="home-container">
    <!-- 页面头部 -->
    <div class="home-header animate-fadeInUp">
      <div class="welcome-section">
        <h1 class="welcome-title">
          <span class="greeting">{{ greeting }}，</span>
          <span class="username">{{ user?.username || '同学' }}</span>
          <span class="wave">👋</span>
        </h1>
        <p class="welcome-subtitle">今天也是充满学习动力的一天！</p>
      </div>
      <el-button 
        type="primary" 
        @click="navigateToCheckin" 
        class="checkin-btn"
        size="large"
      >
        <span class="btn-icon">✏️</span>
        <span>去打卡</span>
      </el-button>
    </div>
    
    <div class="home-content">
      <!-- 今日打卡状态卡片 -->
      <div class="status-card-wrapper animate-fadeInUp delay-100">
        <h2 class="section-title">
          <span class="title-icon">📅</span>
          今日打卡状态
        </h2>
        <el-card class="status-card" :body-style="{ padding: '0' }">
          <div v-if="todayCheckin" class="checked-in">
            <div class="status-badge success">
              <span class="badge-icon">✓</span>
              <span>已打卡</span>
            </div>
            <div class="status-details">
              <div class="detail-item">
                <span class="detail-label">学习时长</span>
                <span class="detail-value highlight">{{ todayCheckin.total_hours }} 小时</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">打卡内容</span>
                <span class="detail-content">{{ todayCheckin.checkins[0]?.content || '无' }}</span>
              </div>
            </div>
          </div>
          <div v-else class="not-checked-in">
            <div class="status-badge warning">
              <span class="badge-icon">!</span>
              <span>未打卡</span>
            </div>
            <div class="encourage-text">
              <p>今日还未打卡哦～</p>
              <p class="sub-text">快去记录你的学习情况吧！</p>
            </div>
            <el-button type="primary" @click="navigateToCheckin" class="go-checkin-btn">
              立即打卡
            </el-button>
          </div>
        </el-card>
      </div>
      
      <!-- 本周学习进度 -->
      <div class="progress-card-wrapper animate-fadeInUp delay-200">
        <h2 class="section-title">
          <span class="title-icon">📊</span>
          本周学习进度
        </h2>
        <el-card class="progress-card" :body-style="{ padding: '24px' }">
          <div v-if="hasWeeklyProgress" class="chart-container">
            <div id="weeklyChart" ref="weeklyChartRef" style="width: 100%; height: 320px;"></div>
          </div>
          <div v-else class="no-progress">
            <div class="empty-illustration">
              <span class="empty-icon">📈</span>
            </div>
            <p class="empty-text">暂无进度数据</p>
            <p class="empty-tip">添加学习计划并完成打卡后，将显示本周学习进度</p>
          </div>
        </el-card>
      </div>
      
      <!-- AI学习评估 -->
      <div class="ai-evaluation-wrapper animate-fadeInUp delay-300">
        <h2 class="section-title">
          <span class="title-icon">🤖</span>
          AI 学习评估
        </h2>
        <el-card class="ai-card" :body-style="{ padding: '24px' }">
          <div v-if="isAiAnalyzing" class="ai-loading">
            <div class="loading-animation">
              <div class="loading-brain">🧠</div>
              <div class="loading-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
            <p class="loading-text">AI 正在分析您的学习数据...</p>
            <div class="loading-progress">
              <el-progress 
                :percentage="loadingProgress" 
                :stroke-width="8" 
                status="success"
                class="custom-progress"
              />
              <span class="loading-step">{{ loadingStep }}</span>
            </div>
          </div>
          
          <div v-else-if="aiEvaluation" class="ai-evaluation-content">
            <!-- 学习评分 -->
            <div class="score-section">
              <div class="total-score">
                <div class="score-circle" :style="getScoreStyle(aiEvaluation.score.total)">
                  <div class="score-inner">
                    <span class="score-number">{{ aiEvaluation.score.total }}</span>
                    <span class="score-label">综合评分</span>
                  </div>
                </div>
              </div>
              <div class="score-details">
                <div class="score-item">
                  <div class="item-header">
                    <span class="item-name">打卡频率</span>
                    <span class="item-value">{{ aiEvaluation.score.frequency }}%</span>
                  </div>
                  <el-progress 
                    :percentage="aiEvaluation.score.frequency" 
                    :color="getScoreColor(aiEvaluation.score.frequency)"
                    :show-text="false"
                    :stroke-width="8"
                    class="item-progress"
                  />
                </div>
                <div class="score-item">
                  <div class="item-header">
                    <span class="item-name">学习时长</span>
                    <span class="item-value">{{ aiEvaluation.score.duration }}%</span>
                  </div>
                  <el-progress 
                    :percentage="aiEvaluation.score.duration" 
                    :color="getScoreColor(aiEvaluation.score.duration)"
                    :show-text="false"
                    :stroke-width="8"
                    class="item-progress"
                  />
                </div>
                <div class="score-item">
                  <div class="item-header">
                    <span class="item-name">学习稳定性</span>
                    <span class="item-value">{{ aiEvaluation.score.stability }}%</span>
                  </div>
                  <el-progress 
                    :percentage="aiEvaluation.score.stability" 
                    :color="getScoreColor(aiEvaluation.score.stability)"
                    :show-text="false"
                    :stroke-width="8"
                    class="item-progress"
                  />
                </div>
              </div>
            </div>
            
            <!-- 学习总结 -->
            <div class="summary-section">
              <h3 class="subsection-title">
                <span class="subsection-icon">📋</span>
                学习总结
              </h3>
              <div class="summary-grid">
                <div class="summary-item">
                  <span class="summary-label">打卡频率</span>
                  <span class="summary-value">{{ aiEvaluation.summary.checkin_frequency }}</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label">学习趋势</span>
                  <span class="summary-value">{{ aiEvaluation.summary.learning_trend }}</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label">稳定性</span>
                  <span class="summary-value">{{ aiEvaluation.summary.stability_level }}</span>
                </div>
              </div>
            </div>
            
            <!-- 问题与建议 -->
            <div class="feedback-section">
              <div class="feedback-column" v-if="aiEvaluation.issues && aiEvaluation.issues.length > 0">
                <h3 class="subsection-title warning">
                  <span class="subsection-icon">⚠️</span>
                  存在问题
                </h3>
                <ul class="feedback-list">
                  <li v-for="(issue, index) in aiEvaluation.issues" :key="index" class="feedback-item">
                    <span class="item-bullet">•</span>
                    {{ issue }}
                  </li>
                </ul>
              </div>
              
              <div class="feedback-column" v-if="aiEvaluation.suggestions && aiEvaluation.suggestions.length > 0">
                <h3 class="subsection-title success">
                  <span class="subsection-icon">💡</span>
                  改进建议
                </h3>
                <ul class="feedback-list">
                  <li v-for="(suggestion, index) in aiEvaluation.suggestions" :key="index" class="feedback-item">
                    <span class="item-bullet">•</span>
                    {{ suggestion }}
                  </li>
                </ul>
              </div>
            </div>
            
            <!-- 推荐学习时长 -->
            <div class="recommendation-section">
              <div class="recommendation-card">
                <span class="rec-icon">⏰</span>
                <div class="rec-content">
                  <span class="rec-label">建议每日学习时长</span>
                  <span class="rec-value">{{ aiEvaluation.recommended_hours }} 小时</span>
                </div>
              </div>
            </div>
            
            <!-- 重新分析按钮 -->
            <div class="reanalyze-section">
              <el-button 
                type="primary" 
                @click="fetchAiEvaluation" 
                class="reanalyze-btn"
                :disabled="isAiAnalyzing"
                plain
              >
                <span class="btn-icon">🔄</span>
                重新分析
              </el-button>
            </div>
          </div>
          
          <div v-else class="ai-no-data">
            <div class="empty-illustration large">
              <span class="empty-icon">🤖</span>
            </div>
            <p class="empty-text">AI 学习分析</p>
            <p class="empty-tip">点击下方按钮，让 AI 为您生成个性化学习报告</p>
            <el-button 
              type="primary" 
              @click="fetchAiEvaluation" 
              class="analyze-btn"
              :disabled="isAiAnalyzing"
              size="large"
            >
              <span class="btn-icon">✨</span>
              开始学习分析
            </el-button>
          </div>
          
          <el-alert
            v-if="aiError"
            type="error"
            :title="aiError"
            show-icon
            class="ai-error-alert"
            closable
            @close="aiError = ''"
          />
        </el-card>
      </div>
      
      <!-- 学习计划 -->
      <div class="plans-wrapper animate-fadeInUp delay-400">
        <h2 class="section-title">
          <span class="title-icon">📝</span>
          我的学习计划
        </h2>
        <el-card class="plans-card" :body-style="{ padding: '24px' }">
          <div v-if="plans.length > 0" class="plans-content">
            <div class="plans-header">
              <el-button type="primary" @click="showCreatePlanDialog" class="create-btn">
                <span class="btn-icon">+</span>
                创建计划
              </el-button>
              <el-button @click="goToChatRooms" class="chat-btn">
                <span class="btn-icon">💬</span>
                群聊中心
              </el-button>
            </div>
            <div class="plans-table-wrapper">
              <el-table :data="plans" class="custom-table" stripe>
                <el-table-column prop="title" label="计划名称" min-width="180">
                  <template #default="scope">
                    <div class="plan-name-cell">
                      <span class="plan-icon">📚</span>
                      <span class="plan-title">{{ scope.row.title }}</span>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column prop="daily_goal_hours" label="每日目标" width="120">
                  <template #default="scope">
                    <span class="goal-badge">{{ scope.row.daily_goal_hours }} 小时</span>
                  </template>
                </el-table-column>
                <el-table-column prop="start_date" label="开始日期" width="120" />
                <el-table-column prop="end_date" label="结束日期" width="120" />
                <el-table-column prop="progress" label="进度" min-width="200">
                  <template #default="scope">
                    <div v-if="scope.row.progress && scope.row.progress.completion_rate !== undefined" class="progress-cell">
                      <el-progress 
                        :percentage="scope.row.progress.completion_rate" 
                        :format="formatProgress"
                        :stroke-width="10"
                        class="plan-progress"
                      />
                    </div>
                    <div v-else class="no-progress-tag">
                      <el-tag type="info" effect="plain" size="small">未开始</el-tag>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="100" fixed="right">
                  <template #default="scope">
                    <el-button 
                      type="danger" 
                      link
                      @click="handleDeletePlan(scope.row.plan_id)"
                      class="delete-btn"
                    >
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
          <div v-else class="no-plans">
            <div class="empty-illustration">
              <span class="empty-icon">📝</span>
            </div>
            <p class="empty-text">暂无学习计划</p>
            <p class="empty-tip">创建您的第一个学习计划，开始高效学习之旅</p>
            <div class="plan-actions">
              <el-button type="primary" @click="showCreatePlanDialog" size="large">
                <span class="btn-icon">+</span>
                创建计划
              </el-button>
              <el-button @click="goToChatRooms" size="large">
                <span class="btn-icon">💬</span>
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
      width="520px"
      class="custom-dialog"
      destroy-on-close
    >
      <el-form
        :model="planForm"
        :rules="planRules"
        ref="planFormRef"
        label-width="120px"
        class="plan-form"
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
        <el-form-item label="每日目标" prop="daily_goal_hours">
          <el-input-number
            v-model="planForm.daily_goal_hours"
            :min="0.5"
            :max="10"
            :step="0.5"
            placeholder="请输入每日目标"
            style="width: 150px"
          />
          <span class="form-unit">小时</span>
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
            placeholder="选择结束日期（可选）"
            style="width: 100%"
            clearable
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="createPlanDialogVisible = false" size="large">
            取消
          </el-button>
          <el-button type="primary" @click="handleCreatePlan" size="large">
            <span class="btn-icon">✓</span>
            创建计划
          </el-button>
        </div>
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

// 问候语
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '夜深了'
  if (hour < 9) return '早上好'
  if (hour < 12) return '上午好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

// 防抖函数
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
  if (plans.value.length === 0) return false
  if (!todayCheckin.value) return false
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
    
    const planData = {
      ...planForm.value,
      start_date: planForm.value.start_date.toISOString().split('T')[0],
      end_date: planForm.value.end_date ? planForm.value.end_date.toISOString().split('T')[0] : null
    }
    
    await userStore.createPlan(planData)
    createPlanDialogVisible.value = false
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

// 获取评分颜色
const getScoreColor = (score) => {
  if (score >= 80) return '#6BCB77'
  if (score >= 60) return '#FFB347'
  return '#FF6B6B'
}

// 获取评分样式
const getScoreStyle = (score) => {
  const color = getScoreColor(score)
  return {
    background: `conic-gradient(${color} ${score * 3.6}deg, #f0f0f0 0deg)`
  }
}

// AI评估相关方法
const fetchAiEvaluation = async () => {
  try {
    isAiAnalyzing.value = true
    aiError.value = ''
    loadingProgress.value = 0
    loadingStep.value = '准备分析数据...'
    
    const token = localStorage.getItem('token')
    if (!token) {
      aiError.value = '请先登录系统'
      isAiAnalyzing.value = false
      return
    }
    
    const now = new Date()
    const weekStart = new Date(now)
    weekStart.setDate(now.getDate() - now.getDay())
    const weekStartDate = weekStart.toISOString().split('T')[0]
    
    const updateProgress = (progress, step) => {
      loadingProgress.value = progress
      loadingStep.value = step
    }
    
    try {
      updateProgress(20, '获取打卡数据...')
      
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
        
        const lines = buffer.split('\n')
        buffer = lines.pop()
        
        for (const line of lines) {
          if (!line.trim()) continue
          
          try {
            const data = JSON.parse(line)
            
            switch (data.type) {
              case 'basic':
                aiEvaluation.value.score = data.data.score
                updateProgress(70, '计算学习评分...')
                break
              case 'analysis':
                fullAnalysis += data.data.content
                updateAiEvaluationFromAnalysis(fullAnalysis)
                updateProgress(85, '生成分析报告...')
                break
              case 'complete':
                updateProgress(100, '分析完成')
                break
              case 'error':
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

const updateAiEvaluationFromAnalysis = debounce((analysis) => {
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
  
  aiEvaluation.value.summary = {
    checkin_frequency: '分析完成',
    learning_trend: '分析完成',
    stability_level: '分析完成'
  }
}, 300)

// 初始化图表
const initWeeklyChart = () => {
  if (!weeklyChartRef.value) return
  
  weeklyChart.value = echarts.init(weeklyChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#FFE5E5',
      borderWidth: 1,
      textStyle: {
        color: '#2D3436'
      },
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#FF6B6B'
        }
      }
    },
    legend: {
      data: ['学习时长（小时）'],
      bottom: 0,
      textStyle: {
        color: '#636E72'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      top: '10%',
      containLabel: true
    },
    xAxis: [
      {
        type: 'category',
        boundaryGap: false,
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
        axisLine: {
          lineStyle: {
            color: '#E8E8E8'
          }
        },
        axisLabel: {
          color: '#636E72'
        }
      }
    ],
    yAxis: [
      {
        type: 'value',
        name: '学习时长（小时）',
        nameTextStyle: {
          color: '#636E72'
        },
        axisLine: {
          show: false
        },
        axisTick: {
          show: false
        },
        axisLabel: {
          color: '#636E72'
        },
        splitLine: {
          lineStyle: {
            color: '#F0F0F0'
          }
        }
      }
    ],
    series: [
      {
        name: '学习时长（小时）',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 10,
        lineStyle: {
          width: 4,
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#FF6B6B' },
            { offset: 1, color: '#FF8E8E' }
          ])
        },
        itemStyle: {
          color: '#FF6B6B',
          borderWidth: 3,
          borderColor: '#fff'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(255, 107, 107, 0.3)' },
            { offset: 1, color: 'rgba(255, 107, 107, 0.05)' }
          ])
        },
        emphasis: {
          focus: 'series',
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(255, 107, 107, 0.5)'
          }
        },
        data: [2, 3, 1.5, 4, 2.5, 3, 2.5]
      }
    ]
  }
  
  weeklyChart.value.setOption(option)
  
  window.addEventListener('resize', () => {
    weeklyChart.value?.resize()
  })
}

// 生命周期
onMounted(async () => {
  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.fetchUserInfo()
  }
  await userStore.fetchTodayCheckin()
  await userStore.fetchPlans()
  if (hasWeeklyProgress.value) {
    initWeeklyChart()
  }
})
</script>

<style scoped>
.home-container {
  padding: 0;
}

/* ===== 页面头部 ===== */
.home-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding: 24px 32px;
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.05) 0%, rgba(255, 217, 61, 0.05) 100%);
  border-radius: 24px;
  border: 1px solid rgba(255, 107, 107, 0.1);
}

.welcome-section {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.welcome-title {
  font-size: 28px;
  font-weight: 700;
  color: #2D3436;
  display: flex;
  align-items: center;
  gap: 8px;
}

.greeting {
  color: #636E72;
}

.username {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.wave {
  display: inline-block;
  animation: wave 2s ease-in-out infinite;
}

@keyframes wave {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(20deg); }
  75% { transform: rotate(-10deg); }
}

.welcome-subtitle {
  font-size: 15px;
  color: #636E72;
}

.checkin-btn {
  height: 48px;
  padding: 0 24px;
  border-radius: 16px !important;
  font-size: 15px;
  font-weight: 600;
}

.checkin-btn .btn-icon {
  margin-right: 6px;
  font-size: 16px;
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

.title-icon {
  font-size: 20px;
}

/* ===== 打卡状态卡片 ===== */
.status-card-wrapper {
  margin-bottom: 32px;
}

.status-card {
  border-radius: 20px;
  overflow: hidden;
}

.checked-in, .not-checked-in {
  padding: 32px;
  text-align: center;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 50px;
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 24px;
}

.status-badge.success {
  background: rgba(107, 203, 119, 0.15);
  color: #4CAF50;
}

.status-badge.warning {
  background: rgba(255, 179, 71, 0.15);
  color: #FF9800;
}

.badge-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.status-badge.success .badge-icon {
  background: #4CAF50;
  color: white;
}

.status-badge.warning .badge-icon {
  background: #FF9800;
  color: white;
}

.status-details {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 400px;
  margin: 0 auto;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 16px;
}

.detail-label {
  font-size: 14px;
  color: #636E72;
}

.detail-value {
  font-size: 18px;
  font-weight: 700;
  color: #FF6B6B;
}

.detail-value.highlight {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.detail-content {
  font-size: 14px;
  color: #2D3436;
  max-width: 200px;
  text-align: right;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.not-checked-in .encourage-text {
  margin-bottom: 24px;
}

.not-checked-in .encourage-text p {
  font-size: 16px;
  color: #2D3436;
  margin-bottom: 4px;
}

.not-checked-in .encourage-text .sub-text {
  font-size: 14px;
  color: #636E72;
}

.go-checkin-btn {
  height: 44px;
  padding: 0 32px;
  border-radius: 12px !important;
}

/* ===== 学习进度 ===== */
.progress-card-wrapper {
  margin-bottom: 32px;
}

.progress-card {
  border-radius: 20px;
}

.chart-container {
  min-height: 320px;
}

.no-progress {
  text-align: center;
  padding: 48px 24px;
}

.empty-illustration {
  width: 80px;
  height: 80px;
  margin: 0 auto 16px;
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(255, 217, 61, 0.1) 100%);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-illustration.large {
  width: 100px;
  height: 100px;
  border-radius: 32px;
}

.empty-icon {
  font-size: 40px;
}

.empty-illustration.large .empty-icon {
  font-size: 50px;
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

/* ===== AI 评估 ===== */
.ai-evaluation-wrapper {
  margin-bottom: 32px;
}

.ai-card {
  border-radius: 20px;
  min-height: 400px;
}

/* AI 加载动画 */
.ai-loading {
  text-align: center;
  padding: 48px 24px;
}

.loading-animation {
  margin-bottom: 24px;
}

.loading-brain {
  font-size: 64px;
  animation: pulse 2s ease-in-out infinite;
  display: inline-block;
}

.loading-dots {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 16px;
}

.loading-dots span {
  width: 12px;
  height: 12px;
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
  border-radius: 50%;
  animation: loadingDot 1.4s ease-in-out infinite;
}

.loading-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes loadingDot {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.loading-text {
  font-size: 16px;
  color: #2D3436;
  font-weight: 500;
  margin-bottom: 24px;
}

.loading-progress {
  max-width: 300px;
  margin: 0 auto;
}

.loading-step {
  display: block;
  margin-top: 12px;
  font-size: 13px;
  color: #636E72;
}

/* AI 评估内容 */
.ai-evaluation-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.score-section {
  display: flex;
  gap: 32px;
  align-items: center;
  flex-wrap: wrap;
}

.total-score {
  flex-shrink: 0;
}

.score-circle {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  padding: 8px;
  position: relative;
}

.score-inner {
  width: 100%;
  height: 100%;
  background: white;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.score-number {
  font-size: 36px;
  font-weight: 700;
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
}

.score-label {
  font-size: 13px;
  color: #636E72;
  margin-top: 4px;
}

.score-details {
  flex: 1;
  min-width: 280px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.score-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.item-name {
  font-size: 14px;
  color: #636E72;
}

.item-value {
  font-size: 14px;
  font-weight: 600;
  color: #2D3436;
}

.item-progress :deep(.el-progress-bar__outer) {
  border-radius: 6px !important;
  background-color: rgba(0, 0, 0, 0.04) !important;
}

.item-progress :deep(.el-progress-bar__inner) {
  border-radius: 6px !important;
}

/* 总结区域 */
.summary-section {
  padding: 24px;
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.03) 0%, rgba(255, 217, 61, 0.03) 100%);
  border-radius: 16px;
}

.subsection-title {
  font-size: 15px;
  font-weight: 600;
  color: #2D3436;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.subsection-title.warning {
  color: #FF9800;
}

.subsection-title.success {
  color: #4CAF50;
}

.subsection-icon {
  font-size: 18px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.summary-label {
  font-size: 13px;
  color: #636E72;
}

.summary-value {
  font-size: 14px;
  font-weight: 600;
  color: #2D3436;
}

/* 反馈区域 */
.feedback-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}

.feedback-column {
  padding: 20px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 16px;
}

.feedback-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.feedback-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 14px;
  color: #2D3436;
  line-height: 1.6;
}

.item-bullet {
  color: #FF6B6B;
  font-weight: bold;
  flex-shrink: 0;
}

/* 推荐区域 */
.recommendation-section {
  display: flex;
  justify-content: center;
}

.recommendation-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 32px;
  background: linear-gradient(135deg, rgba(107, 203, 119, 0.1) 0%, rgba(77, 150, 255, 0.1) 100%);
  border-radius: 16px;
  border: 1px solid rgba(107, 203, 119, 0.2);
}

.rec-icon {
  font-size: 32px;
}

.rec-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.rec-label {
  font-size: 13px;
  color: #636E72;
}

.rec-value {
  font-size: 20px;
  font-weight: 700;
  color: #4CAF50;
}

/* 重新分析按钮 */
.reanalyze-section {
  display: flex;
  justify-content: center;
  padding-top: 8px;
}

.reanalyze-btn {
  height: 44px;
  padding: 0 24px;
  border-radius: 12px !important;
}

.reanalyze-btn .btn-icon {
  margin-right: 6px;
}

/* AI 无数据状态 */
.ai-no-data {
  text-align: center;
  padding: 48px 24px;
}

.analyze-btn {
  margin-top: 24px;
  height: 48px;
  padding: 0 32px;
  border-radius: 16px !important;
}

.analyze-btn .btn-icon {
  margin-right: 6px;
}

/* ===== 学习计划 ===== */
.plans-wrapper {
  margin-bottom: 32px;
}

.plans-card {
  border-radius: 20px;
}

.plans-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.plans-header {
  display: flex;
  gap: 12px;
}

.create-btn .btn-icon,
.chat-btn .btn-icon {
  margin-right: 4px;
}

.plans-table-wrapper {
  overflow-x: auto;
}

.custom-table {
  border-radius: 16px;
  overflow: hidden;
}

.plan-name-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.plan-icon {
  font-size: 20px;
}

.plan-title {
  font-weight: 500;
  color: #2D3436;
}

.goal-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  background: rgba(255, 107, 107, 0.1);
  color: #FF6B6B;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.progress-cell {
  padding-right: 16px;
}

.plan-progress :deep(.el-progress-bar__outer) {
  border-radius: 6px !important;
}

.plan-progress :deep(.el-progress-bar__inner) {
  border-radius: 6px !important;
}

.no-progress-tag {
  display: inline-block;
}

.delete-btn {
  color: #FF6B6B !important;
}

/* 无计划状态 */
.no-plans {
  text-align: center;
  padding: 48px 24px;
}

.plan-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 24px;
}

/* ===== 对话框 ===== */
.custom-dialog :deep(.el-dialog) {
  border-radius: 24px;
}

.plan-form :deep(.el-input__wrapper),
.plan-form :deep(.el-textarea__inner),
.plan-form :deep(.el-input-number .el-input__wrapper) {
  border-radius: 12px !important;
}

.form-unit {
  margin-left: 8px;
  color: #636E72;
  font-size: 14px;
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
.delay-300 { animation-delay: 0.3s; }
.delay-400 { animation-delay: 0.4s; }

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
  .home-header {
    flex-direction: column;
    gap: 16px;
    text-align: center;
    padding: 20px;
  }
  
  .welcome-title {
    font-size: 22px;
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .score-section {
    flex-direction: column;
    align-items: center;
  }
  
  .feedback-section {
    grid-template-columns: 1fr;
  }
  
  .summary-grid {
    grid-template-columns: 1fr;
  }
  
  .plans-header {
    flex-direction: column;
  }
  
  .plan-actions {
    flex-direction: column;
  }
}
</style>
