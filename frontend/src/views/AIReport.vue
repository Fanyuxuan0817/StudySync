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
            <el-button type="primary" @click="fetchWeeklyReport">
              生成报告
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
        />
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../store/modules/auth'
import api from '../api'

const authStore = useAuthStore()
const weekStartDate = ref(new Date())
const weeklyReport = ref(null)
const error = ref('')

// 方法
const fetchWeeklyReport = async () => {
  try {
    error.value = ''
    const response = await api.ai.getWeeklyReport({
      week_date: weekStartDate.value
    })
    weeklyReport.value = response.data.data
  } catch (err) {
    error.value = err.response?.data?.message || '生成报告失败，请稍后重试'
    console.error('生成报告失败:', err)
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
  margin-bottom: 10px;
  padding-left: 20px;
  position: relative;
}

.issue-item::before,
.suggestion-item::before {
  content: '•';
  position: absolute;
  left: 0;
  color: #666;
}

.no-issues,
.no-suggestions {
  text-align: center;
  color: #999;
  padding: 20px 0;
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
</style>
