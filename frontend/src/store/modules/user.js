import { defineStore } from 'pinia'
import api from '../../api'

export const useUserStore = defineStore('user', {
  state: () => ({
    plans: [],
    checkins: [],
    todayCheckin: null,
    groups: { created: [], joined: [] },
    loading: false,
    error: null
  }),
  
  actions: {
    async fetchPlans() {
      this.loading = true
      this.error = null
      try {
        const response = await api.plans.getPlans()
        this.plans = response.data.data.items
        return response
      } catch (error) {
        this.error = error.response?.data?.message || '获取计划失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async createPlan(planData) {
      this.loading = true
      this.error = null
      try {
        const response = await api.plans.createPlan(planData)
        await this.fetchPlans()
        return response
      } catch (error) {
        this.error = error.response?.data?.message || '创建计划失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async fetchTodayCheckin() {
      this.loading = true
      this.error = null
      try {
        const response = await api.checkins.getTodayCheckins()
        // 当返回的数据为空或没有有效的打卡信息时，设置为null
        this.todayCheckin = response.data.data && response.data.data.total_hours > 0 ? response.data.data : null
        return response
      } catch (error) {
        // 发生错误时，确保todayCheckin为null（未打卡状态）
        this.todayCheckin = null
        this.error = error.response?.data?.message || '获取今日打卡失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async createCheckin(checkinData) {
      this.loading = true
      this.error = null
      try {
        const response = await api.checkins.createCheckin(checkinData)
        await this.fetchTodayCheckin()
        return response
      } catch (error) {
        this.error = error.response?.data?.message || '创建打卡失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async fetchGroups() {
      this.loading = true
      this.error = null
      try {
        const response = await api.groups.getGroups()
        this.groups = response.data.data
        return response
      } catch (error) {
        this.error = error.response?.data?.message || '获取群组失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async deletePlan(planId) {
      this.loading = true
      this.error = null
      try {
        const response = await api.plans.deletePlan(planId)
        await this.fetchPlans()
        return response
      } catch (error) {
        this.error = error.response?.data?.message || '删除计划失败'
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})
