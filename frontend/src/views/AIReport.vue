<template>
  <div class="ai-report-container">
    <h1 class="page-title">AI学习评估</h1>
    
    <div class="report-card">
      <el-card :body-style="{ padding: '30px' }">
        <h2 class="card-title">本周学习报告</h2>
        
        <el-form :inline="true" class="week-form">
          <el-form-item label="周开始日期">
            <el-date-picker
              v-model="weekStartDate"
              type="date"
              placeholder="选择周开始日期"
              @change="fetchWeeklyReport"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="fetchWeeklyReport" :loading="isGenerating">
              {{ weeklyReport ? '刷新报告' : '生成报告' }}
            </el-button>
          </el-form-item>
          <el-form-item>
            <el-button type="warning" @click="regenerateReport" :loading="isRegenerating">
              重新生成
            </el-button>
          </el-form-item>
        </el-form>
        
        <div v-if="weeklyReport" class="report-content">
          <!-- 学习评分 -->
          <div class="score-section">
            <h3 class="section-title">学习评分</h3>
            <div class="score-card">
              <div class="total-score">
                <el-progress
                  type="dashboard"
                  :percentage="weeklyReport.score.total"
                  :color="getScoreColor(weeklyReport.score.total)"
                  :format="formatScore"
                  :stroke-width="15"
                  :width="150"
                />
              </div>
              <div class="score-details">
                <div class="score-item">
                  <span class="score-label">打卡频率</span>
                  <el-progress
                    :percentage="weeklyReport.score.frequency"
                    :color="getScoreColor(weeklyReport.score.frequency)"
                  />
                </div>
                <div class="score-item">
                  <span class="score-label">学习时长</span>
                  <el-progress
                    :percentage="weeklyReport.score.duration"
                    :color="getScoreColor(weeklyReport.score.duration)"
                  />
                </div>
                <div class="score-item">
                  <span class="score-label">学习稳定性</span>
                  <el-progress
                    :percentage="weeklyReport.score.stability"
                    :color="getScoreColor(weeklyReport.score.stability)"
                  />
                </div>
              </div>
            </div>
          </div>
          
          <!-- 学习总结 -->
          <div class="summary-section">
            <h3 class="section-title">学习总结</h3>
            <el-card :body-style="{ padding: '20px' }" class="summary-card">
              <div class="summary-item">
                <span class="summary-label">打卡频率：</span>
                <span class="summary-value">{{ weeklyReport.summary.checkin_frequency }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">学习趋势：</span>
                <span class="summary-value">{{ weeklyReport.summary.learning_trend }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">稳定性：</span>
                <span class="summary-value">{{ weeklyReport.summary.stability_level }}</span>
              </div>
            </el-card>
          </div>
          
          <!-- 问题与建议 -->
          <div class="issues-suggestions">
            <div class="issues-section">
              <h3 class="section-title">存在问题</h3>
              <el-card :body-style="{ padding: '20px' }" class="issues-card">
                <ul v-if="weeklyReport.issues && weeklyReport.issues.length > 0">
                  <li v-for="(issue, index) in weeklyReport.issues" :key="index" class="issue-item">
                    {{ issue }}
                  </li>
                </ul>
                <p v-else class="no-issues">暂无问题</p>
              </el-card>
            </div>
            
            <div class="suggestions-section">
              <h3 class="section-title">改进建议</h3>
              <el-card :body-style="{ padding: '20px' }" class="suggestions-card">
                <ul v-if="weeklyReport.suggestions && weeklyReport.suggestions.length > 0">
                  <li v-for="(suggestion, index) in weeklyReport.suggestions" :key="index" class="suggestion-item">
                    {{ suggestion }}
                  </li>
                </ul>
                <p v-else class="no-suggestions">暂无建议</p>
              </el-card>
            </div>
          </div>
          
          <!-- 推荐学习时长 -->
          <div class="recommended-section">
            <h3 class="section-title">推荐学习时长</h3>
            <el-card :body-style="{ padding: '20px' }" class="recommended-card">
              <div class="recommended-hours">
                <span class="hours-label">建议每日学习时长：</span>
                <span class="hours-value">{{ weeklyReport.recommended_hours }} 小时</span>
              </div>
            </el-card>
          </div>
        </div>
        <div v-else class="loading-report">
          <el-empty description="点击生成报告" />
        </div>
        
        <el-alert
          v-if="error"
          type="error"
          :title="error"
          show-icon
          class="error-alert"
        ></el-alert>
      </el-card>
    </div>
    
    <!-- AI学习教练 -->
    <div class="ai-coach-card">
      <el-card :body-style="{ padding: '30px' }">
        <h2 class="card-title">AI学习教练</h2>
        
        <div class="learning-data-form">
          <el-form label-width="120px" class="data-form">
            <el-form-item label="学习目标">
              <el-input v-model="learningData.learning_goal" placeholder="例如：考研数学" />
            </el-form-item>
            <el-form-item label="本周总学习时长">
              <el-input-number v-model="learningData.weekly_total_hours" :min="0" :step="0.5" placeholder="小时" />
            </el-form-item>
            <el-form-item label="平均每日学习时长">
              <el-input-number v-model="learningData.average_daily_hours" :min="0" :step="0.5" placeholder="小时" />
            </el-form-item>
            <el-form-item label="目标每日学习时长">
              <el-input-number v-model="learningData.target_daily_hours" :min="0" :step="0.5" placeholder="小时" />
            </el-form-item>
            <el-form-item label="连续打卡天数">
              <el-input-number v-model="learningData.consecutive_checkin_days" :min="0" :step="1" placeholder="天" />
            </el-form-item>
            <el-form-item label="漏打卡天数">
              <el-input-number v-model="learningData.missed_checkin_days" :min="0" :step="1" placeholder="天" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="getLearningCoach" :loading="isLoading">
                获取学习指导
              </el-button>
            </el-form-item>
          </el-form>
        </div>
        
        <div v-if="aiCoachResponse" class="coach-response">
          <el-card :body-style="{ padding: '20px' }" class="response-card">
            <div v-html="aiCoachResponse" class="ai-content"></div>
          </el-card>
        </div>
        <div v-else-if="coachError" class="loading-coach">
          <el-alert
            type="error"
            :title="coachError"
            show-icon
            class="error-alert"
          />
        </div>
      </el-card>
    </div>
    
    <!-- AI打卡分析 -->
    <div class="ai-checkin-analysis-card">
      <el-card :body-style="{ padding: '30px' }">
        <h2 class="card-title">AI打卡分析</h2>
        
        <el-alert
          title="使用说明"
          description="选择分析日期范围，系统将自动分析您的打卡记录，识别学习模式和异常情况，并提供个性化的改进建议。"
          type="info"
          show-icon
          style="margin-bottom: 20px;"
        />
        
        <div class="analysis-controls">
          <el-form :inline="true" class="analysis-form">
            <el-form-item label="开始日期">
              <el-date-picker
                v-model="analysisStartDate"
                type="date"
                placeholder="选择开始日期"
              />
            </el-form-item>
            <el-form-item label="结束日期">
              <el-date-picker
                v-model="analysisEndDate"
                type="date"
                placeholder="选择结束日期"
              />
            </el-form-item>
            <el-form-item label="分析类型">
              <el-select v-model="analysisType" placeholder="选择分析类型">
                <el-option label="综合分析" value="comprehensive" />
                <el-option label="规律分析" value="pattern" />
                <el-option label="异常分析" value="anomaly" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="getCheckinAnalysis" :loading="isAnalysisLoading">
                开始分析
              </el-button>
            </el-form-item>
            <el-form-item>
              <el-button type="info" @click="testApiConnection">
                测试连接
              </el-button>
            </el-form-item>
          </el-form>
        </div>
        
        <div v-if="checkinAnalysis" class="analysis-results">
          <el-alert
            v-if="checkinAnalysis.stats.total_checkins === 0"
            title="暂无打卡数据"
            description="您选择的日期范围内没有打卡记录，请调整日期范围或开始打卡后再进行分析。"
            type="info"
            show-icon
            style="margin-bottom: 20px;"
          />
          <!-- 统计概览 -->
          <div class="stats-overview">
            <h3 class="section-title">打卡统计概览</h3>
            <el-row :gutter="20">
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-value">{{ checkinAnalysis.stats.total_checkins }}</div>
                  <div class="stat-label">总打卡次数</div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-value">{{ checkinAnalysis.stats.total_hours.toFixed(1) }}</div>
                  <div class="stat-label">总学习时长（小时）</div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-value">{{ checkinAnalysis.stats.checkin_rate.toFixed(1) }}%</div>
                  <div class="stat-label">打卡率</div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-value">{{ checkinAnalysis.stats.streak_days }}</div>
                  <div class="stat-label">最长连续打卡（天）</div>
                </el-card>
              </el-col>
            </el-row>
          </div>
          
          <!-- 洞察和建议 -->
          <div class="insights-section">
            <h3 class="section-title">AI洞察</h3>
            <el-card class="insights-card">
              <div v-for="(insight, index) in checkinAnalysis.insights" :key="index" class="insight-item">
                {{ insight }}
              </div>
            </el-card>
          </div>
          
          <div class="recommendations-section">
            <h3 class="section-title">改进建议</h3>
            <el-card class="recommendations-card">
              <div v-for="(recommendation, index) in checkinAnalysis.recommendations" :key="index" class="recommendation-item">
                {{ recommendation }}
              </div>
            </el-card>
          </div>
          
          <!-- 异常分析 -->
          <div v-if="checkinAnalysis.anomalies && checkinAnalysis.anomalies.length > 0" class="anomalies-section">
            <h3 class="section-title">异常打卡情况</h3>
            <el-card class="anomalies-card">
              <el-table :data="checkinAnalysis.anomalies" style="width: 100%">
                <el-table-column prop="date" label="日期" width="120">
                  <template #default="scope">
                    {{ new Date(scope.row.date).toLocaleDateString() }}
                  </template>
                </el-table-column>
                <el-table-column prop="type" label="异常类型" width="120" />
                <el-table-column prop="description" label="描述" />
                <el-table-column prop="severity" label="严重程度" width="100">
                  <template #default="scope">
                    <el-tag :type="scope.row.severity === 'high' ? 'danger' : 'warning'">
                      {{ scope.row.severity === 'high' ? '高' : '中' }}
                    </el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </div>
          
          <!-- AI总结 -->
          <div class="summary-section">
            <h3 class="section-title">AI总结</h3>
            <el-card class="summary-card">
              <div class="ai-summary-content">
                {{ checkinAnalysis.ai_summary }}
              </div>
            </el-card>
          </div>
        </div>
        <div v-else-if="analysisError" class="loading-analysis">
          <el-alert
            type="error"
            :title="analysisError"
            show-icon
            class="error-alert"
          />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../store/modules/auth'
import api from '../api'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()
const weekStartDate = ref(new Date())
const weeklyReport = ref(null)
const error = ref('')
const isGenerating = ref(false)
const isRegenerating = ref(false)

// AI学习教练相关
const learningData = ref({
  learning_goal: '考研数学',
  weekly_total_hours: 12,
  average_daily_hours: 1.7,
  target_daily_hours: 3,
  consecutive_checkin_days: 3,
  missed_checkin_days: 2
})
const aiCoachResponse = ref(null)
const coachError = ref('')
const isLoading = ref(false)

// AI打卡分析相关
const analysisStartDate = ref(new Date(Date.now() - 30 * 24 * 60 * 60 * 1000))
const analysisEndDate = ref(new Date())
const analysisType = ref('comprehensive')
const checkinAnalysis = ref(null)
const analysisError = ref('')
const isAnalysisLoading = ref(false)

// 方法
const fetchWeeklyReport = async () => {
  try {
    isGenerating.value = true
    error.value = ''
    // 将日期转换为ISO格式，只保留日期部分（YYYY-MM-DD）
    const weekDate = weekStartDate.value ? new Date(weekStartDate.value).toISOString().split('T')[0] : null
    const response = await api.ai.getWeeklyReport({
      week_date: weekDate
    })
    weeklyReport.value = response.data.data
  } catch (err) {
    error.value = err.response?.data?.message || '生成报告失败，请稍后重试'
    console.error('生成报告失败:', err)
  } finally {
    isGenerating.value = false
  }
}

const regenerateReport = async () => {
  try {
    isRegenerating.value = true
    error.value = ''
    
    // 计算周开始和结束日期
    const startDate = new Date(weekStartDate.value)
    const endDate = new Date(startDate)
    endDate.setDate(startDate.getDate() + 6)
    
    // 准备重新生成报告的数据
    const reportData = {
      week_start: startDate.toISOString().split('T')[0],
      week_end: endDate.toISOString().split('T')[0]
    }
    
    // 调用重新生成报告的API
    await api.ai.generateReport(reportData)
    
    // 重新获取报告
    await fetchWeeklyReport()
    
    // 显示成功消息
    ElMessage({
      message: '报告重新生成成功',
      type: 'success'
    })
  } catch (err) {
    error.value = err.response?.data?.message || '重新生成报告失败，请稍后重试'
    console.error('重新生成报告失败:', err)
    ElMessage.error('重新生成报告失败，请稍后重试')
  } finally {
    isRegenerating.value = false
  }
}

const getLearningCoach = async () => {
  try {
    isLoading.value = true
    coachError.value = ''
    
    // 使用 fetch API 直接处理流式响应
    const response = await fetch('/api/ai/learning_coach', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(learningData.value)
    })
    
    if (!response.ok) {
      throw new Error('API请求失败')
    }
    
    // 处理流式响应
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let fullResponse = ''
    
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      const chunk = decoder.decode(value, { stream: true })
      fullResponse += chunk
      // 可以在这里添加实时更新UI的逻辑
    }
    
    // 格式化响应
    let formattedResponse = fullResponse
      .replace(/\n/g, '<br>')
      .replace(/^- (.*?)<br>/gm, '<li>$1</li>')
      .replace(/(<li>.*?<\/li>)/gs, '<ul>$1</ul>')
    aiCoachResponse.value = formattedResponse
  } catch (err) {
    coachError.value = err.message || '获取学习指导失败，请稍后重试'
    console.error('获取学习指导失败:', err)
  } finally {
    isLoading.value = false
  }
}

const testApiConnection = async () => {
  try {
    console.log('测试API连接开始...')
    const token = localStorage.getItem('token')
    console.log('Token存在:', !!token)
    
    // 测试一个简单的GET请求
    const response = await api.users.getMe()
    console.log('用户API测试成功:', response)
    
    // 如果用户API成功，再测试打卡分析API
    const testRequest = {
      start_date: '2024-01-01',
      end_date: '2024-01-31',
      analysis_type: 'comprehensive'
    }
    
    console.log('测试打卡分析API，请求数据:', testRequest)
    const analysisResponse = await api.ai.getCheckinAnalysis(testRequest)
    console.log('打卡分析API测试成功:', analysisResponse)
    
    alert('API连接测试成功！')
  } catch (err) {
    console.error('API测试失败:', err)
    console.error('错误详情:', err.response || err)
    alert(`API测试失败: ${err.message || '未知错误'}`)
  }
}

const getCheckinAnalysis = async () => {
  try {
    isAnalysisLoading.value = true
    analysisError.value = ''
    
    // 检查认证状态
    const token = localStorage.getItem('token')
    console.log('当前token:', token)
    if (!token) {
      analysisError.value = '请先登录系统'
      return
    }
    
    // 转换日期格式
    const startDate = analysisStartDate.value ? new Date(analysisStartDate.value).toISOString().split('T')[0] : null
    const endDate = analysisEndDate.value ? new Date(analysisEndDate.value).toISOString().split('T')[0] : null
    
    const requestData = {
      start_date: startDate,
      end_date: endDate,
      analysis_type: analysisType.value
    }
    
    console.log('请求数据:', requestData)
    
    const response = await api.ai.getCheckinAnalysis(requestData)
    console.log('打卡分析响应:', response)
    checkinAnalysis.value = response.data.data
  } catch (err) {
    console.error('打卡分析失败详情:', err)
    console.error('错误响应:', err.response)
    console.error('错误数据:', err.response?.data)
    
    if (err.response?.status === 401) {
      analysisError.value = '登录已过期，请重新登录'
      // 清除过期的token
      localStorage.removeItem('token')
      // 可以添加自动跳转到登录页面的逻辑
      setTimeout(() => {
        window.location.href = '/auth/login'
      }, 2000)
    } else {
      analysisError.value = err.response?.data?.message || err.message || '打卡分析失败，请稍后重试'
    }
  } finally {
    isAnalysisLoading.value = false
  }
}

const getScoreColor = (score) => {
  if (score >= 80) {
    return '#67C23A'
  } else if (score >= 60) {
    return '#E6A23C'
  } else {
    return '#F56C6C'
  }
}

const formatScore = (percentage) => {
  return `${percentage}分`
}

// 生命周期
onMounted(async () => {
  // 获取用户信息
  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.fetchUserInfo()
  }
  // 生成本周报告
  fetchWeeklyReport()
})
</script>

<style scoped>
.ai-report-container {
  padding: 20px;
}

.page-title {
  font-size: 24px;
  color: #333;
  margin-bottom: 30px;
}

.report-card {
  margin-bottom: 30px;
}

.card-title {
  font-size: 18px;
  color: #333;
  margin-bottom: 20px;
  font-weight: 500;
}

.week-form {
  margin-bottom: 30px;
}

.report-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.section-title {
  font-size: 16px;
  color: #666;
  margin-bottom: 15px;
  font-weight: 500;
}

.score-card {
  display: flex;
  gap: 40px;
  align-items: center;
}

.total-score {
  flex-shrink: 0;
}

.score-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.score-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.score-label {
  font-size: 14px;
  color: #666;
}

.summary-section,
.recommended-section {
  margin-top: 20px;
}

.summary-card,
.issues-card,
.suggestions-card,
.recommended-card {
  min-height: 100px;
}

.summary-item {
  margin-bottom: 10px;
  font-size: 14px;
}

.summary-label {
  font-weight: 500;
  color: #333;
  margin-right: 10px;
}

.summary-value {
  color: #666;
}

.issues-suggestions {
  display: flex;
  gap: 30px;
  margin-top: 20px;
}

.issues-section,
.suggestions-section {
  flex: 1;
}

.issue-item,
.suggestion-item {
  margin-bottom: 12px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  position: relative;
  line-height: 1.5;
  transition: all 0.3s ease;
}

.issue-item {
  border-left: 4px solid #F56C6C;
}

.suggestion-item {
  border-left: 4px solid #67C23A;
}

.issue-item:hover,
.suggestion-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.no-issues,
.no-suggestions {
  text-align: center;
  color: #999;
  padding: 30px 0;
  font-style: italic;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px dashed #ddd;
}

.recommended-hours {
  text-align: center;
  font-size: 16px;
}

.hours-label {
  color: #666;
  margin-right: 10px;
}

.hours-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.loading-report {
  text-align: center;
  padding: 40px 0;
}

.error-alert {
  margin-top: 20px;
}

@media (max-width: 768px) {
  .score-card {
    flex-direction: column;
    text-align: center;
  }
  
  .issues-suggestions {
    flex-direction: column;
  }
}

/* AI学习教练样式 */
.ai-coach-card {
  margin-top: 30px;
}

.learning-data-form {
  margin-bottom: 30px;
}

.data-form {
  max-width: 600px;
}

.coach-response {
  margin-top: 30px;
}

.response-card {
  min-height: 400px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 12px;
  overflow: hidden;
}

.ai-content {
  line-height: 1.8;
  white-space: pre-wrap;
  padding: 30px;
  font-size: 16px;
  color: #333;
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  margin: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.ai-content h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 20px 0 15px;
  color: #409EFF;
  border-bottom: 2px solid #e6f7ff;
  padding-bottom: 8px;
}

.ai-content p {
  margin-bottom: 15px;
  text-align: justify;
}

.ai-content ul {
  margin: 15px 0;
  padding-left: 25px;
}

.ai-content li {
  margin-bottom: 10px;
  position: relative;
  padding-left: 10px;
}

.ai-content li::before {
  content: '•';
  position: absolute;
  left: -15px;
  color: #409EFF;
  font-weight: bold;
}

.ai-content br {
  line-height: 2;
}

/* AI打卡分析样式 */
.ai-checkin-analysis-card {
  margin-top: 30px;
}

.analysis-controls {
  margin-bottom: 30px;
}

.analysis-form {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.stats-overview {
  margin-bottom: 30px;
}

.stat-card {
  text-align: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 10px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.insights-section,
.recommendations-section,
.anomalies-section,
.summary-section {
  margin-bottom: 30px;
}

.insights-card,
.recommendations-card,
.anomalies-card,
.summary-card {
  min-height: 100px;
}

.insight-item,
.recommendation-item {
  margin-bottom: 15px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 10px;
  position: relative;
  line-height: 1.6;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.insight-item {
  border-left: 4px solid #667eea;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf4 100%);
}

.recommendation-item {
  border-left: 4px solid #28a745;
  background: linear-gradient(135deg, #f0fff4 0%, #e6f7ee 100%);
}

.insight-item:hover,
.recommendation-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.insight-item::before {
  content: '💡';
  position: absolute;
  left: -15px;
  top: 15px;
  font-size: 18px;
  background-color: white;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.recommendation-item::before {
  content: '✅';
  position: absolute;
  left: -15px;
  top: 15px;
  font-size: 16px;
  background-color: white;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.ai-summary-content {
  line-height: 1.8;
  font-size: 16px;
  color: #333;
  padding: 30px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f2 100%);
  border-radius: 12px;
  position: relative;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  text-align: justify;
  border-left: 4px solid #667eea;
}

.ai-summary-content::before {
  content: '📊';
  position: absolute;
  top: -15px;
  left: 20px;
  font-size: 24px;
  background-color: white;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.ai-summary-content p {
  margin-bottom: 15px;
}

.ai-summary-content p:last-child {
  margin-bottom: 0;
}
</style>
