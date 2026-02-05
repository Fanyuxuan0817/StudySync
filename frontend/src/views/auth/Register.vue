<template>
  <div class="register-form">
    <h2 class="form-title">创建账号 🚀</h2>
    <p class="form-subtitle">加入 StudySync，开启学习之旅</p>
    
    <el-form
      :model="registerForm"
      :rules="registerRules"
      ref="registerFormRef"
      class="auth-form"
      @keyup.enter="handleRegister"
    >
      <el-form-item prop="username">
        <div class="input-wrapper">
          <span class="input-icon">👤</span>
          <el-input 
            v-model="registerForm.username" 
            placeholder="请输入用户名"
            size="large"
            class="custom-input"
          />
        </div>
      </el-form-item>
      
      <el-form-item prop="email">
        <div class="input-wrapper">
          <span class="input-icon">📧</span>
          <el-input 
            v-model="registerForm.email" 
            placeholder="请输入邮箱"
            size="large"
            class="custom-input"
          />
        </div>
      </el-form-item>
      
      <el-form-item prop="password">
        <div class="input-wrapper">
          <span class="input-icon">🔒</span>
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            show-password
            class="custom-input"
          />
        </div>
      </el-form-item>
      
      <el-form-item prop="confirmPassword">
        <div class="input-wrapper">
          <span class="input-icon">🔐</span>
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请确认密码"
            size="large"
            show-password
            class="custom-input"
          />
        </div>
      </el-form-item>
      
      <el-form-item class="form-actions">
        <el-button 
          type="primary" 
          class="submit-btn" 
          @click="handleRegister" 
          :loading="loading"
          size="large"
        >
          <span v-if="!loading" class="btn-content">
            <span>创建账号</span>
            <span class="btn-icon">✨</span>
          </span>
          <span v-else>注册中...</span>
        </el-button>
      </el-form-item>
      
      <div class="form-footer">
        <span class="footer-text">已有账号？</span>
        <el-button 
          link 
          type="primary" 
          @click="navigateToLogin"
          class="link-btn"
        >
          立即登录
        </el-button>
      </div>
    </el-form>
    
    <el-alert
      v-if="error"
      type="error"
      :title="error"
      show-icon
      class="error-alert"
      closable
      @close="error = ''"
    />
    
    <el-alert
      v-if="success"
      type="success"
      :title="success"
      show-icon
      class="success-alert"
    />
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../store/modules/auth'

const router = useRouter()
const authStore = useAuthStore()
const registerFormRef = ref(null)
const loading = ref(false)
const error = ref('')
const success = ref('')

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  try {
    await registerFormRef.value.validate()
    loading.value = true
    error.value = ''
    success.value = ''
    
    await authStore.register(registerForm.username, registerForm.email, registerForm.password)
    success.value = '注册成功，即将跳转到登录页'
    setTimeout(() => {
      router.push('/auth/login')
    }, 1500)
  } catch (err) {
    console.error('注册失败:', err)
    error.value = err.response?.data?.detail || '注册失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

const navigateToLogin = () => {
  router.push('/auth/login')
}
</script>

<style scoped>
.register-form {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.form-title {
  text-align: center;
  font-size: 24px;
  font-weight: 700;
  color: #2D3436;
  margin-bottom: 8px;
}

.form-subtitle {
  text-align: center;
  font-size: 14px;
  color: #636E72;
  margin-bottom: 28px;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* ===== 输入框样式 ===== */
.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 16px;
  font-size: 18px;
  z-index: 1;
  pointer-events: none;
}

.custom-input :deep(.el-input__wrapper) {
  padding-left: 44px !important;
  border-radius: 16px !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
  border: 2px solid transparent !important;
  transition: all 0.3s ease !important;
  background: rgba(255, 255, 255, 0.8) !important;
}

.custom-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
  background: white !important;
}

.custom-input :deep(.el-input__wrapper.is-focus) {
  border-color: #FFB1B1 !important;
  box-shadow: 0 0 0 4px rgba(255, 107, 107, 0.1), 0 4px 12px rgba(0, 0, 0, 0.08) !important;
  background: white !important;
}

.custom-input :deep(.el-input__inner) {
  height: 48px;
  font-size: 15px;
}

.custom-input :deep(.el-input__inner::placeholder) {
  color: #B2BEC3;
}

/* ===== 按钮样式 ===== */
.form-actions {
  margin-top: 8px;
  margin-bottom: 0;
}

.submit-btn {
  width: 100%;
  height: 52px;
  border-radius: 16px !important;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%) !important;
  border: none !important;
  box-shadow: 0 4px 16px rgba(255, 107, 107, 0.35) !important;
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55) !important;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(255, 107, 107, 0.45) !important;
}

.submit-btn:active {
  transform: scale(0.98);
}

.btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-icon {
  font-size: 18px;
  transition: transform 0.3s ease;
}

.submit-btn:hover .btn-icon {
  transform: rotate(20deg) scale(1.2);
}

/* ===== 底部链接 ===== */
.form-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.footer-text {
  font-size: 14px;
  color: #636E72;
}

.link-btn {
  font-size: 14px;
  font-weight: 600;
  color: #FF6B6B !important;
  padding: 4px 8px !important;
  border-radius: 8px !important;
  transition: all 0.2s ease !important;
}

.link-btn:hover {
  background: rgba(255, 107, 107, 0.1) !important;
}

/* ===== 提示样式 ===== */
.error-alert {
  margin-top: 16px;
  border-radius: 12px !important;
  animation: shake 0.5s ease-in-out;
}

.success-alert {
  margin-top: 16px;
  border-radius: 12px !important;
  animation: fadeIn 0.3s ease-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
  20%, 40%, 60%, 80% { transform: translateX(5px); }
}

/* ===== 响应式设计 ===== */
@media (max-width: 480px) {
  .form-title {
    font-size: 22px;
  }
  
  .form-subtitle {
    font-size: 13px;
  }
  
  .custom-input :deep(.el-input__inner) {
    height: 44px;
  }
  
  .submit-btn {
    height: 48px;
    font-size: 15px;
  }
}
</style>
