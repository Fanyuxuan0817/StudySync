import { defineStore } from 'pinia'
import api from '../../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    isAuthenticated: !!localStorage.getItem('token'),
    user: null,
    loading: false,
    error: null
  }),
  
  actions: {
    async login(username, password) {
      this.loading = true
      this.error = null
      try {
        console.log('调用API登录...')
        const response = await api.auth.login({ username, password })
        console.log('API登录响应:', response)
        
        const { access_token } = response.data.data
        console.log('获取到的token:', access_token)
        
        localStorage.setItem('token', access_token)
        console.log('token已存储到localStorage')
        
        this.token = access_token
        this.isAuthenticated = true
        console.log('认证状态已更新')
        
        // 尝试获取用户信息，但即使失败也不中断登录流程
        try {
          console.log('尝试获取用户信息...')
          await this.fetchUserInfo()
          console.log('获取用户信息成功')
        } catch (err) {
          console.warn('获取用户信息失败，但登录成功:', err)
        }
        return response
      } catch (error) {
        console.error('登录失败:', error)
        this.error = error.response?.data?.detail || '登录失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async register(username, email, password) {
      this.loading = true
      this.error = null
      try {
        const response = await api.auth.register({ username, email, password })
        return response
      } catch (error) {
        this.error = error.response?.data?.detail || '注册失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async fetchUserInfo() {
      try {
        const response = await api.users.getMe()
        this.user = response.data.data
        return response
      } catch (error) {
        this.error = error.response?.data?.detail || '获取用户信息失败'
        throw error
      }
    },
    
    logout() {
      localStorage.removeItem('token')
      this.token = null
      this.isAuthenticated = false
      this.user = null
    }
  }
})
