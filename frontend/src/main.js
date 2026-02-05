import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './styles/theme.css'
import './styles/animations.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia) // 先初始化 Pinia
app.use(router) // 再使用路由
app.use(ElementPlus)

app.mount('#app')
