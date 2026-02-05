import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器，自动添加token
apiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器，处理错误
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/auth/login'
    }
    return Promise.reject(error)
  }
)

// API模块
const api = {
  auth: {
    login: (data) => apiClient.post('/auth/login', data),
    register: (data) => apiClient.post('/auth/register', data)
  },
  users: {
    getMe: () => apiClient.get('/users/me'),
    createApiKey: () => apiClient.post('/users/api_key')
  },
  plans: {
    createPlan: (data) => apiClient.post('/plans', data),
    getPlans: (params) => apiClient.get('/plans', { params }),
    updatePlan: (id, data) => apiClient.put(`/plans/${id}`, data),
    deletePlan: (id) => apiClient.delete(`/plans/${id}`)
  },
  checkins: {
    createCheckin: (data) => apiClient.post('/checkins', data),
    getCheckins: (params) => apiClient.get('/checkins', { params }),
    getTodayCheckins: () => apiClient.get('/checkins/today'),
    getCheckinStats: (params) => apiClient.get('/checkins/stats', { params }),
    updateCheckin: (id, data) => apiClient.put(`/checkins/${id}`, data),
    deleteCheckin: (id) => apiClient.delete(`/checkins/${id}`)
  },
  groups: {
    createGroup: (data) => apiClient.post('/groups', data),
    getGroups: () => apiClient.get('/groups'),
    joinGroup: (id) => apiClient.post(`/groups/${id}/join`),
    leaveGroup: (id) => apiClient.post(`/groups/${id}/leave`),
    getGroupMembers: (id, params) => apiClient.get(`/groups/${id}/members`, { params }),
    removeMember: (groupId, userId) => apiClient.delete(`/groups/${groupId}/members/${userId}`),
    getGroupCheckins: (id, params) => apiClient.get(`/groups/${id}/checkins`, { params }),
    getGroupStats: (id) => apiClient.get(`/groups/${id}/stats`)
  },
  chatRooms: {
    // 群聊相关API
    createChatRoom: (data) => apiClient.post('/chat-rooms', data),
    searchChatRooms: (params) => apiClient.get('/chat-rooms/search', { params }),
    searchByChatId: (chatId) => apiClient.get('/chat-rooms/search-by-id', { params: { chat_id: chatId } }),
    getChatRoomMembers: (id) => apiClient.get(`/chat-rooms/${id}/members`),
    createJoinRequest: (chatRoomId, data) => apiClient.post(`/chat-rooms/${chatRoomId}/join-request`, data),
    getJoinRequests: (chatRoomId, params) => apiClient.get(`/chat-rooms/${chatRoomId}/join-requests`, { params }),
    reviewJoinRequest: (chatRoomId, requestId, data) => apiClient.post(`/chat-rooms/${chatRoomId}/join-requests/${requestId}/review`, data)
  },
  ai: {
    getWeeklyReport: (params) => apiClient.get('/ai/weekly_report', { params }),
    generateReport: (data) => apiClient.post('/ai/generate_report', data)
  }
}

export default api
