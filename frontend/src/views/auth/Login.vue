<template>
  <div class="login-form">
    <h2 class="form-title">登录</h2>
    <el-form
      :model="loginForm"
      :rules="loginRules"
      ref="loginFormRef"
      label-width="80px"
      class="demo-ruleForm"
    >
      <el-form-item label="用户名" prop="username">
        <el-input v-model="loginForm.username" placeholder="请输入用户名" />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input
          v-model="loginForm.password"
          type="password"
          placeholder="请输入密码"
          show-password
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" class="login-btn" @click="handleLogin" :loading="loading">
          登录
        </el-button>
        <el-button @click="navigateToRegister">
          去注册
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
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../store/modules/auth'

const router = useRouter()
const authStore = useAuthStore()
const loginFormRef = ref(null)
const loading = ref(false)
const error = ref('')

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 个字符', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    await loginFormRef.value.validate()
    loading.value = true
    error.value = ''
    console.log('开始登录...')
    
    const response = await authStore.login(loginForm.username, loginForm.password)
    console.log('登录成功，响应:', response)
    console.log('localStorage中的token:', localStorage.getItem('token'))
    console.log('准备跳转到/home...')
    
    router.push('/home')
    console.log('跳转命令已执行')
  } catch (err) {
    console.error('登录失败:', err)
    error.value = err.response?.data?.detail || '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}

const navigateToRegister = () => {
  router.push('/auth/register')
}
</script>

<style scoped>
.form-title {
  text-align: center;
  margin-bottom: 20px;
  color: #333;
}

.login-btn {
  width: 100%;
  margin-bottom: 10px;
}

.error-alert {
  margin-top: 15px;
}
</style>
