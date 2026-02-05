<template>
  <div id="app">
    <NavBar v-if="$route.meta.requiresAuth" />
    <main class="main-content">
      <router-view v-if="$route.meta.requiresAuth" />
      <router-view v-else />
    </main>
  </div>
</template>

<script setup>
import NavBar from './components/NavBar.vue'
</script>

<style>
/* ===== 全局重置 ===== */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  background: linear-gradient(135deg, #FAFAF8 0%, #FFF8F5 50%, #FAFAF8 100%);
  background-attachment: fixed;
  color: #2D3436;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  min-height: 100vh;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

/* ===== 滚动条美化 ===== */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.02);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #FFB1B1 0%, #FF8E8E 100%);
  border-radius: 4px;
  transition: all 0.3s ease;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #FF8E8E 0%, #FF6B6B 100%);
}

/* ===== 选中文本样式 ===== */
::selection {
  background: rgba(255, 107, 107, 0.2);
  color: #2D3436;
}

/* ===== 页面过渡动画 ===== */
.page-enter-active,
.page-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* ===== 链接样式 ===== */
a {
  color: #FF6B6B;
  text-decoration: none;
  transition: all 0.3s ease;
}

a:hover {
  color: #E55A5A;
}

/* ===== 响应式布局 ===== */
@media (max-width: 768px) {
  .main-content {
    padding: 16px;
  }
}

/* ===== Element Plus 全局覆盖 ===== */

/* 按钮样式 */
.el-button {
  border-radius: 12px !important;
  font-weight: 500 !important;
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55) !important;
}

.el-button--primary {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%) !important;
  border: none !important;
  box-shadow: 0 4px 14px rgba(255, 107, 107, 0.35) !important;
}

.el-button--primary:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.45) !important;
}

.el-button--primary:active {
  transform: scale(0.98) !important;
}

.el-button--success {
  background: linear-gradient(135deg, #6BCB77 0%, #5ABF66 100%) !important;
  border: none !important;
  box-shadow: 0 4px 14px rgba(107, 203, 119, 0.35) !important;
}

.el-button--danger {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF5252 100%) !important;
  border: none !important;
}

/* 输入框样式 */
.el-input__wrapper {
  border-radius: 12px !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
  border: 2px solid transparent !important;
  transition: all 0.3s ease !important;
}

.el-input__wrapper:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
}

.el-input__wrapper.is-focus {
  border-color: #FFB1B1 !important;
  box-shadow: 0 0 0 4px rgba(255, 107, 107, 0.1), 0 4px 12px rgba(0, 0, 0, 0.08) !important;
}

/* 卡片样式 */
.el-card {
  border-radius: 20px !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06) !important;
  border: 1px solid rgba(0, 0, 0, 0.04) !important;
  transition: all 0.3s ease !important;
}

.el-card:hover {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
  transform: translateY(-2px);
}

/* 标签样式 */
.el-tag {
  border-radius: 20px !important;
  font-weight: 500 !important;
  padding: 4px 12px !important;
}

.el-tag--success {
  background: rgba(107, 203, 119, 0.15) !important;
  border-color: rgba(107, 203, 119, 0.3) !important;
  color: #4CAF50 !important;
}

.el-tag--warning {
  background: rgba(255, 179, 71, 0.15) !important;
  border-color: rgba(255, 179, 71, 0.3) !important;
  color: #FF9800 !important;
}

.el-tag--danger {
  background: rgba(255, 107, 107, 0.15) !important;
  border-color: rgba(255, 107, 107, 0.3) !important;
  color: #FF6B6B !important;
}

/* 对话框样式 */
.el-dialog {
  border-radius: 24px !important;
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.12) !important;
  overflow: hidden !important;
}

.el-dialog__header {
  padding: 24px 24px 16px !important;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06) !important;
}

.el-dialog__title {
  font-weight: 600 !important;
  font-size: 18px !important;
  color: #2D3436 !important;
}

.el-dialog__body {
  padding: 20px 24px !important;
}

.el-dialog__footer {
  padding: 16px 24px 24px !important;
}

/* 下拉菜单样式 */
.el-dropdown-menu {
  border-radius: 16px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08) !important;
  border: 1px solid rgba(0, 0, 0, 0.04) !important;
  padding: 8px !important;
}

.el-dropdown-menu__item {
  border-radius: 12px !important;
  padding: 10px 16px !important;
  transition: all 0.2s ease !important;
}

.el-dropdown-menu__item:hover {
  background: rgba(255, 107, 107, 0.1) !important;
  color: #FF6B6B !important;
}

/* 表格样式 */
.el-table {
  border-radius: 16px !important;
  overflow: hidden !important;
}

.el-table th {
  background: linear-gradient(180deg, #FFF8F5 0%, #FAFAF8 100%) !important;
  font-weight: 600 !important;
  color: #2D3436 !important;
}

.el-table__row {
  transition: background-color 0.2s ease !important;
}

.el-table__row:hover {
  background-color: rgba(255, 107, 107, 0.03) !important;
}

/* 进度条样式 */
.el-progress-bar__outer {
  border-radius: 10px !important;
  background-color: rgba(0, 0, 0, 0.04) !important;
}

.el-progress-bar__inner {
  border-radius: 10px !important;
  background: linear-gradient(90deg, #FF6B6B 0%, #FF8E8E 100%) !important;
}

/* 表单样式 */
.el-form-item__label {
  font-weight: 500 !important;
  color: #636E72 !important;
}

/* 警告提示样式 */
.el-alert {
  border-radius: 12px !important;
  border: none !important;
}

.el-alert--success {
  background: rgba(107, 203, 119, 0.1) !important;
}

.el-alert--warning {
  background: rgba(255, 179, 71, 0.1) !important;
}

.el-alert--error {
  background: rgba(255, 107, 107, 0.1) !important;
}

/* 选择器样式 */
.el-select .el-input__wrapper {
  border-radius: 12px !important;
}

/* 日期选择器样式 */
.el-date-editor.el-input__wrapper {
  border-radius: 12px !important;
}

/* 文本域样式 */
.el-textarea__inner {
  border-radius: 12px !important;
  border: 2px solid rgba(0, 0, 0, 0.06) !important;
  transition: all 0.3s ease !important;
}

.el-textarea__inner:focus {
  border-color: #FFB1B1 !important;
  box-shadow: 0 0 0 4px rgba(255, 107, 107, 0.1) !important;
}

/* 标签页样式 */
.el-tabs__nav-wrap::after {
  height: 1px !important;
  background: rgba(0, 0, 0, 0.06) !important;
}

.el-tabs__item {
  font-weight: 500 !important;
  transition: all 0.2s ease !important;
}

.el-tabs__item.is-active {
  color: #FF6B6B !important;
}

.el-tabs__active-bar {
  background: linear-gradient(90deg, #FF6B6B 0%, #FF8E8E 100%) !important;
  height: 3px !important;
  border-radius: 2px !important;
}

/* 徽章样式 */
.el-badge__content {
  border-radius: 10px !important;
  font-weight: 600 !important;
  box-shadow: 0 2px 8px rgba(255, 107, 107, 0.4) !important;
}

/* 分页样式 */
.el-pagination .el-pager li {
  border-radius: 8px !important;
  transition: all 0.2s ease !important;
}

.el-pagination .el-pager li.active {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%) !important;
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.35) !important;
}

/* 加载动画 */
.el-loading-spinner .circular {
  width: 42px;
  height: 42px;
}

.el-loading-spinner .path {
  stroke: #FF6B6B !important;
  stroke-width: 3;
}

/* 消息提示样式 */
.el-message {
  border-radius: 12px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12) !important;
}

.el-message--success {
  background: rgba(107, 203, 119, 0.95) !important;
  border-color: #6BCB77 !important;
}

.el-message--error {
  background: rgba(255, 107, 107, 0.95) !important;
  border-color: #FF6B6B !important;
}

.el-message--warning {
  background: rgba(255, 179, 71, 0.95) !important;
  border-color: #FFB347 !important;
}

/* 空状态样式 */
.el-empty__image {
  filter: hue-rotate(340deg) saturate(1.5);
}

.el-empty__description {
  color: #636E72 !important;
}

/* 骨架屏样式 */
.el-skeleton__item {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%) !important;
  background-size: 200% 100% !important;
}
</style>
