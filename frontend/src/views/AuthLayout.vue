<template>
  <div class="auth-layout">
    <!-- 装饰背景元素 -->
    <div class="bg-decoration">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>
      <div class="floating-shapes">
        <span class="shape">📚</span>
        <span class="shape">✏️</span>
        <span class="shape">🎯</span>
        <span class="shape">💡</span>
        <span class="shape">🌟</span>
      </div>
    </div>
    
    <div class="auth-container">
      <div class="auth-header">
        <div class="logo-wrapper">
          <div class="logo-bg">
            <span class="logo-icon">📚</span>
          </div>
        </div>
        <h1 class="brand-title">StudySync</h1>
        <p class="brand-subtitle">让学习变得更有趣</p>
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
  background: linear-gradient(135deg, #FFE5E5 0%, #FFF4E6 25%, #FFF8F5 50%, #F0F9FF 75%, #E5F3FF 100%);
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
  position: relative;
  overflow: hidden;
  padding: 20px;
}

@keyframes gradientShift {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

/* ===== 装饰背景元素 ===== */
.bg-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.5;
}

.blob-1 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
  top: -100px;
  right: -100px;
  animation: float 8s ease-in-out infinite;
}

.blob-2 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #FFD93D 0%, #FFB347 100%);
  bottom: -50px;
  left: -50px;
  animation: float 10s ease-in-out infinite reverse;
}

.blob-3 {
  width: 250px;
  height: 250px;
  background: linear-gradient(135deg, #6BCB77 0%, #4D96FF 100%);
  top: 50%;
  left: 20%;
  animation: float 12s ease-in-out infinite;
  animation-delay: -4s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg) scale(1);
  }
  33% {
    transform: translateY(-30px) rotate(5deg) scale(1.05);
  }
  66% {
    transform: translateY(15px) rotate(-3deg) scale(0.95);
  }
}

/* 浮动形状 */
.floating-shapes {
  position: absolute;
  inset: 0;
}

.shape {
  position: absolute;
  font-size: 32px;
  opacity: 0.15;
  animation: shapeFloat 6s ease-in-out infinite;
}

.shape:nth-child(1) {
  top: 15%;
  left: 10%;
  animation-delay: 0s;
}

.shape:nth-child(2) {
  top: 25%;
  right: 15%;
  animation-delay: 1s;
}

.shape:nth-child(3) {
  bottom: 30%;
  left: 15%;
  animation-delay: 2s;
}

.shape:nth-child(4) {
  bottom: 20%;
  right: 10%;
  animation-delay: 3s;
}

.shape:nth-child(5) {
  top: 60%;
  right: 20%;
  animation-delay: 4s;
}

@keyframes shapeFloat {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(10deg);
  }
}

/* ===== 认证容器 ===== */
.auth-container {
  width: 100%;
  max-width: 440px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 32px;
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.08),
    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
  overflow: hidden;
  position: relative;
  z-index: 1;
  backdrop-filter: blur(20px);
  animation: slideUp 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(40px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* ===== 头部区域 ===== */
.auth-header {
  text-align: center;
  padding: 40px 32px 24px;
  background: linear-gradient(180deg, rgba(255, 107, 107, 0.03) 0%, transparent 100%);
}

.logo-wrapper {
  margin-bottom: 20px;
}

.logo-bg {
  width: 80px;
  height: 80px;
  margin: 0 auto;
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 
    0 8px 24px rgba(255, 107, 107, 0.3),
    0 0 0 4px rgba(255, 255, 255, 0.5) inset;
  animation: logoPulse 3s ease-in-out infinite;
}

@keyframes logoPulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 8px 24px rgba(255, 107, 107, 0.3), 0 0 0 4px rgba(255, 255, 255, 0.5) inset;
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 12px 32px rgba(255, 107, 107, 0.4), 0 0 0 4px rgba(255, 255, 255, 0.5) inset;
  }
}

.logo-icon {
  font-size: 40px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.brand-title {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 50%, #FFB347 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
  letter-spacing: -0.5px;
}

.brand-subtitle {
  font-size: 15px;
  color: #636E72;
  font-weight: 400;
}

/* ===== 内容区域 ===== */
.auth-content {
  padding: 0 32px 40px;
}

/* ===== 响应式设计 ===== */
@media (max-width: 480px) {
  .auth-layout {
    padding: 16px;
    background: linear-gradient(135deg, #FFE5E5 0%, #FFF4E6 50%, #F0F9FF 100%);
  }
  
  .auth-container {
    border-radius: 24px;
  }
  
  .auth-header {
    padding: 32px 24px 20px;
  }
  
  .logo-bg {
    width: 64px;
    height: 64px;
    border-radius: 20px;
  }
  
  .logo-icon {
    font-size: 32px;
  }
  
  .brand-title {
    font-size: 24px;
  }
  
  .brand-subtitle {
    font-size: 14px;
  }
  
  .auth-content {
    padding: 0 24px 32px;
  }
  
  .blob {
    filter: blur(40px);
    opacity: 0.3;
  }
  
  .blob-1 {
    width: 250px;
    height: 250px;
  }
  
  .blob-2 {
    width: 200px;
    height: 200px;
  }
  
  .blob-3 {
    width: 180px;
    height: 180px;
  }
}
</style>
