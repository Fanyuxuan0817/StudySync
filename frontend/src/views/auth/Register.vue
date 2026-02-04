<template>
  <div class="register-form">
    <h2 class="form-title">注册</h2>
    <el-form
      :model="registerForm"
      :rules="registerRules"
      ref="registerFormRef"
      label-width="80px"
      class="demo-ruleForm"
    >
      <el-form-item label="用户名" prop="username">
        <el-input v-model="registerForm.username" placeholder="请输入用户名" />
      </el-form-item>
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="registerForm.email" placeholder="请输入邮箱" />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input
          v-model="registerForm.password"
          type="password"
          placeholder="请输入密码"
          show-password
        />
      </el-form-item>
      <el-form-item label="确认密码" prop="confirmPassword">
        <el-input
          v-model="registerForm.confirmPassword"
          type="password"
          placeholder="请确认密码"
          show-password
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" class="register-btn" @click="handleRegister" :loading="loading">
          注册
        </el-button>
        <el-button @click="navigateToLogin">
          去登录
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
    success.value = '注册成功，请登录'
    setTimeout(() => {
      router.push('/auth/login')
    }, 1500)
  } catch (err) {
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
.form-title {
  text-align: center;
  margin-bottom: 20px;
  color: #333;
}

.register-btn {
  width: 100%;
  margin-bottom: 10px;
}

.error-alert,
.success-alert {
  margin-top: 15px;
}
</style>
