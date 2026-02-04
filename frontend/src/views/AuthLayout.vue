<template>
  <div class="auth-layout">
    <div class="auth-container">
      <div class="auth-header">
        <h1>StudySync</h1>
        <p>学习同步助手</p>
      </div>
      <div class="auth-content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-layout {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.auth-container {
  width: 100%;
  max-width: 400px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.auth-header {
  text-align: center;
  padding: 30px 0;
  background: #f5f7fa;
  border-bottom: 1px solid #eaeef2;
}

.auth-header h1 {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.auth-header p {
  font-size: 14px;
  color: #666;
}

.auth-content {
  padding: 30px;
}
</style>
