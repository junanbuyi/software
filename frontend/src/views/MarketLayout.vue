<template>
  <div class="market-page">
    <header class="market-header">
      <h1 class="market-brand">电力市场平台</h1>
      <div class="header-actions">
        <button class="btn outline sm" @click="goBack">返回电价预测平台</button>
      </div>
    </header>
    <div class="market-layout">
      <!-- 左侧功能模块导航 -->
      <aside class="market-sidebar">
        <div class="sidebar-title">功能模块</div>
        <ul class="sidebar-nav">
          <li v-for="item in navItems" :key="item.key"
              :class="['nav-item', { active: isActive(item.path) }]"
              @click="navigateTo(item.path)">
            <span class="nav-icon">{{ item.icon }}</span>
            <span>{{ item.label }}</span>
          </li>
        </ul>
      </aside>

      <!-- 右侧内容区 -->
      <main class="market-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter, useRoute } from "vue-router";

const router = useRouter();
const route = useRoute();

const goBack = () => router.push("/home");

const navItems = [
  { key: "company", label: "企业信息", icon: "≡", path: "/market/company" },
  { key: "disclosure", label: "信息披露", icon: "📊", path: "/market/disclosure" },
  { key: "trading", label: "市场交易", icon: "⚙", path: "/market/trading" },
  { key: "settlement", label: "结算报告", icon: "💰", path: "/market/settlement" },
];

const navigateTo = (path: string) => {
  router.push(path);
};

const isActive = (path: string) => {
  return route.path === path;
};
</script>

<style scoped>
.market-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.market-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 52px;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  flex-shrink: 0;
}
.market-brand {
  font-size: 18px;
  font-weight: 700;
  color: #1890ff;
  margin: 0;
}
.header-actions {
  display: flex;
  gap: 8px;
}
.market-layout {
  display: grid;
  grid-template-columns: 160px 1fr;
  gap: 0;
  flex: 1;
}

/* 左侧导航 */
.market-sidebar {
  background: #fff;
  border-right: 1px solid #e8e8e8;
  padding: 20px 0;
}
.sidebar-title {
  padding: 0 20px 16px;
  font-size: 13px;
  color: #999;
}
.sidebar-nav {
  list-style: none;
  padding: 0;
  margin: 0;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
  border-left: 3px solid transparent;
  transition: all 0.2s;
}
.nav-item:hover {
  background: #f5f7fa;
}
.nav-item.active {
  color: #1890ff;
  border-left-color: #1890ff;
  background: #e6f7ff;
  font-weight: 600;
}
.nav-icon {
  font-size: 16px;
}

/* 右侧内容 */
.market-content {
  padding: 20px 24px;
  background: #f5f7fa;
  overflow-y: auto;
}

/* 按钮 */
.btn {
  padding: 6px 16px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s;
}
.btn.outline {
  background: #fff;
  color: #333;
  border-color: #d9d9d9;
}
.btn.outline:hover {
  border-color: #1890ff;
  color: #1890ff;
}
.btn.sm {
  padding: 4px 12px;
  font-size: 12px;
}
</style>
