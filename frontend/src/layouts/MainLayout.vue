<template>
  <div class="app">
    <!-- 左侧侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-brand">
        <div class="sidebar-brand-text">电价预测平台</div>
      </div>

      <nav class="sidebar-menu">
        <div class="sidebar-section">功能模块</div>
        <RouterLink class="sidebar-item" to="/home" :class="{ active: $route.path === '/home' }">
          <span class="sidebar-item-icon">☰</span>
          <span>首页</span>
        </RouterLink>
        <RouterLink class="sidebar-item" to="/datasets" :class="{ active: $route.path === '/datasets' }">
          <span class="sidebar-item-icon">📊</span>
          <span>数据管理</span>
        </RouterLink>
        <RouterLink class="sidebar-item" to="/models" :class="{ active: $route.path === '/models' }">
          <span class="sidebar-item-icon">⚙</span>
          <span>模型管理</span>
        </RouterLink>
        <RouterLink class="sidebar-item" to="/predictions" :class="{ active: $route.path.startsWith('/predictions') }">
          <span class="sidebar-item-icon">📈</span>
          <span>预测</span>
        </RouterLink>
        <RouterLink class="sidebar-item" to="/ranking" :class="{ active: $route.path === '/ranking' }">
          <span class="sidebar-item-icon">👤</span>
          <span>评分管理</span>
        </RouterLink>

        <div class="sidebar-section">系统</div>
        <RouterLink class="sidebar-item" to="/account" :class="{ active: $route.path === '/account' }">
          <span class="sidebar-item-icon">⚙️</span>
          <span>账号设置</span>
        </RouterLink>
        <a class="sidebar-item" href="#" @click.prevent="handleLogout">
          <span class="sidebar-item-icon">🚪</span>
          <span>退出登录</span>
        </a>
      </nav>
    </aside>

    <!-- 右侧主内容区 -->
    <div class="main-wrapper">
      <main class="content">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink, useRouter } from "vue-router";

const router = useRouter();

const handleLogout = () => {
  localStorage.removeItem("access_token");
  router.push("/login");
};
</script>
