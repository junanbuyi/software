<template>
  <MainLayout>
    <div class="page-header">
      <h1 class="page-title">预测管理</h1>
      <button class="btn primary" @click="showCreateModal = true">新建方案</button>
    </div>

    <!-- 方案列表 -->
    <section class="panel">
      <div class="panel-header">
        <h3 class="panel-title">方案列表</h3>
      </div>
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>模型名称</th>
              <th>数据集名称</th>
              <th>类型</th>
              <th>预测时间段</th>
              <th>描述</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="plan in plans" :key="plan.id">
              <td>{{ plan.name }}</td>
              <td>{{ plan.dataset }}</td>
              <td>{{ plan.type }}</td>
              <td>{{ getPeriod(plan) }}</td>
              <td>{{ plan.description }}</td>
              <td>
                <router-link class="link" :to="`/predictions/${plan.id}`">查看</router-link>
                <a class="link danger" href="#" @click.prevent="handleDelete(plan)">删除</a>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- 新建方案弹窗 -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>新建预测方案</h3>
          <button class="modal-close" @click="showCreateModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>模型名称 <span class="required">*</span></label>
            <input class="input" placeholder="请输入模型名称" />
          </div>
          <div class="form-group">
            <label>选择数据集 <span class="required">*</span></label>
            <select class="input">
              <option value="">请选择数据集</option>
              <option>广东电价数据</option>
              <option>陕西电价数据</option>
            </select>
          </div>
          <div class="form-group">
            <label>预测类型 <span class="required">*</span></label>
            <select class="input">
              <option>周前确定</option>
              <option>周前概率</option>
            </select>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>开始日期</label>
              <input class="input" type="date" />
            </div>
            <div class="form-group">
              <label>结束日期</label>
              <input class="input" type="date" />
            </div>
          </div>
          <div class="form-group">
            <label>描述</label>
            <textarea class="input" rows="2" placeholder="请输入描述"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn" @click="showCreateModal = false">取消</button>
          <button class="btn primary" @click="showCreateModal = false">创建</button>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import MainLayout from "../layouts/MainLayout.vue";

const showCreateModal = ref(false);

const STORAGE_KEY = "predict_selected_date";

const selectedDate = ref<string>(localStorage.getItem(STORAGE_KEY) || "");

const periodText = computed(() => {
  const saved = localStorage.getItem("prediction_period");
  if (saved) {
    try {
      const { start, end } = JSON.parse(saved);
      return `${start.replace(/-/g, ".")}-${end.replace(/-/g, ".")}`;
    } catch {}
  }
  return "2024.06.25-2024.07.01";
});

const plans = ref([
  {
    id: 1,
    name: "Mamba周前确定",
    dataset: "广东电价数据",
    type: "周前确定",
    description: "广东mamba周前",
  },
  {
    id: 2,
    name: "tcn周前概率",
    dataset: "广东电价数据",
    type: "周前概率",
    description: "广东tcn周前概率预测",
  },
]);

const getPeriod = (_plan: any) => {
  return periodText.value;
};

const handleDelete = (plan: any) => {
  if (confirm(`确定删除方案 "${plan.name}" 吗？`)) {
    plans.value = plans.value.filter((p) => p.id !== plan.id);
  }
};
</script>

<style scoped>
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
}
.panel-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
}
.table td a.link {
  margin-right: 12px;
}
.form-row {
  display: flex;
  gap: 16px;
}
.form-group {
  flex: 1;
  margin-bottom: 16px;
}
.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 13px;
  font-weight: 500;
}
.form-group .required {
  color: var(--red);
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal {
  background: var(--card);
  border-radius: 4px;
  width: 520px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
}
.modal-header h3 {
  margin: 0;
  font-size: 16px;
}
.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--muted);
}
.modal-body {
  padding: 20px;
}
.modal-footer {
  padding: 16px 20px;
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
