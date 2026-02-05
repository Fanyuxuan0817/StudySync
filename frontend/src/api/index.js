import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 30000 // 30秒超时，给AI分析足够的处理时间
})

// 请求拦截器，自动添加token
apiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    // 调试日志
    console.log(`[API请求] ${config.method?.toUpperCase()} ${config.url}`, config.params || config.data)
    return config
  },
  error => {
    console.error('[API请求错误]', error)
    return Promise.reject(error)
  }
)

// 响应拦截器，处理错误
apiClient.interceptors.response.use(
  response => {
    // 调试日志
    console.log(`[API响应] ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data)
    return response
  },
  error => {
    console.error(`[API响应错误] ${error.config?.method?.toUpperCase()} ${error.config?.url}`, error.response?.data || error.message)
    
    // 处理超时错误
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      console.error('[API超时错误] 请求超时，请检查网络连接或稍后重试')
      // 可以在这里添加全局错误提示
    }
    
    // 处理401错误
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
    getGroup: (id) => apiClient.get(`/groups/${id}`),
    updateGroup: (id, data) => apiClient.put(`/groups/${id}`, data),
    deleteGroup: (id) => apiClient.delete(`/groups/${id}`),
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
    getChatRooms: () => apiClient.get('/chat-rooms/my-rooms'),
    getChatRoom: (id) => apiClient.get(`/chat-rooms/${id}`),
    searchChatRooms: (params) => apiClient.get('/chat-rooms/search', { params }),
    searchByChatId: (chatId) => apiClient.get('/chat-rooms/search-by-id', { params: { chat_id: chatId } }),
    getChatRoomMembers: (id) => apiClient.get(`/chat-rooms/${id}/members`),
    createJoinRequest: (chatRoomId, data) => apiClient.post(`/chat-rooms/${chatRoomId}/join-request`, data),
    getJoinRequests: (chatRoomId, params) => apiClient.get(`/chat-rooms/${chatRoomId}/join-requests`, { params }),
    reviewJoinRequest: (chatRoomId, requestId, data) => apiClient.post(`/chat-rooms/${chatRoomId}/join-requests/${requestId}/review`, data),
    updateChatRoom: (id, data) => apiClient.put(`/chat-rooms/${id}`, data),
    deleteChatRoom: (id) => apiClient.delete(`/chat-rooms/${id}`),
    leaveChatRoom: (id) => apiClient.post(`/chat-rooms/${id}/leave`),
    getPendingApprovals: () => apiClient.get('/chat-rooms/join-requests/pending'),
    // 消息相关API
    getMessages: (chatRoomId, params) => apiClient.get(`/chat-rooms/${chatRoomId}/messages`, { params }),
    sendMessage: (chatRoomId, content, messageType = 'text') => apiClient.post(`/chat-rooms/${chatRoomId}/messages`, null, {
      params: { content, message_type: messageType }
    }),
    deleteMessage: (chatRoomId, messageId) => apiClient.delete(`/chat-rooms/${chatRoomId}/messages/${messageId}`),
    searchMessages: (chatRoomId, params) => apiClient.get(`/chat-rooms/${chatRoomId}/messages/search`, { params }),
    getRecentMessages: (chatRoomId, params) => apiClient.get(`/chat-rooms/${chatRoomId}/messages/recent`, { params })
  },
  ai: {
    getWeeklyReport: (params) => apiClient.get('/ai/weekly_report', { params }),
    generateReport: (data) => apiClient.post('/ai/generate_report', data),
    getLearningCoach: (data) => apiClient.post('/ai/learning_coach', data),
    getCheckinAnalysis: (data) => apiClient.post('/ai/checkin_analysis', data)
  }
}

export default api
