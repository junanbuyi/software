<template>
  <div class="content-section">
    <h2 class="section-title">企业信息</h2>
    <div class="card">
      <h3 class="card-title">企业列表</h3>
      <div class="simple-table">
        <div class="table-header">
          <span class="col col-id">火电厂编号</span>
          <span class="col col-name">火电厂名称</span>
        </div>
        <div v-for="c in companies" :key="c.id" class="table-row clickable" @click="selectedCompany = c">
          <span class="col col-id">{{ c.id }}</span>
          <span class="col col-name">{{ c.name }}</span>
        </div>
      </div>
    </div>
    <!-- 机组详情 -->
    <div v-if="selectedCompany" class="card" style="margin-top: 20px;">
      <h3 class="card-title">企业名称：{{ selectedCompany.name }} 企业类型：火电公司</h3>
      <h4 style="margin: 16px 0 12px; font-size: 15px;">机组信息</h4>
      <div class="unit-grid">
        <div v-for="u in selectedCompany.units" :key="u.id" class="unit-card">
          <div class="unit-row"><span class="label">火电机组编号</span><span>{{ u.id }}</span></div>
          <div class="unit-row"><span class="label">所在母线编号</span><span>{{ u.bus }}</span></div>
          <div class="unit-row"><span class="label">装机容量(100MW)</span><span>{{ u.capacity }}</span></div>
          <div class="unit-row"><span class="label">初始开机状态</span><span>{{ u.initState }}</span></div>
          <div class="unit-row"><span class="label">初始状态已持续时间(h)</span><span>{{ u.initDuration }}</span></div>
          <div class="unit-row"><span class="label">最小技术出力(100MW)</span><span>{{ u.minOutput }}</span></div>
          <div class="unit-row"><span class="label">上爬坡速率(100MW/h)</span><span>{{ u.rampUp }}</span></div>
          <div class="unit-row"><span class="label">下爬坡速率(100MW/h)</span><span>{{ u.rampDown }}</span></div>
          <div class="unit-row"><span class="label">最短开机时间(h)</span><span>{{ u.minOnTime }}</span></div>
          <div class="unit-row"><span class="label">最短关机时间(h)</span><span>{{ u.minOffTime }}</span></div>
          <div class="unit-row"><span class="label">启动成本(万元/次)</span><span>{{ u.startCost }}</span></div>
          <div class="unit-row"><span class="label">关停成本(万元/次)</span><span>{{ u.stopCost }}</span></div>
          <div class="unit-row"><span class="label">燃料</span><span>{{ u.fuel }}</span></div>
          <div class="unit-row"><span class="label">运行成本曲线系数A</span><span>{{ u.costA }}</span></div>
          <div class="unit-row"><span class="label">运行成本曲线系数B</span><span>{{ u.costB }}</span></div>
          <div class="unit-row"><span class="label">运行成本曲线系数C</span><span>{{ u.costC }}</span></div>
          <div class="unit-row"><span class="label">调频响应时间(min)</span><span>{{ u.freqResp }}</span></div>
          <div class="unit-row"><span class="label">调频调节误差(%)</span><span>{{ u.freqErr }}</span></div>
          <div class="unit-row"><span class="label">调节速度(MW/min)</span><span>{{ u.regSpeed }}</span></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { marketApi } from "../api/market";

const companies = ref<any[]>([]);
const selectedCompany = ref<any>(null);

async function fetchCompanies() {
  try {
    const { data } = await marketApi.getCompanies();
    companies.value = data.items || [];
  } catch (e) { 
    console.error("获取企业信息失败", e); 
  }
}

onMounted(() => {
  fetchCompanies();
});
</script>

<style scoped>
.content-section {
  max-width: 1100px;
}
.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 16px;
}
.card {
  background: #fff;
  border-radius: 8px;
  padding: 20px 24px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  margin: 0 0 12px;
}
.simple-table {
  font-size: 13px;
}
.table-header {
  display: flex;
  padding: 10px 16px;
  font-weight: 600;
  color: #666;
  border-bottom: 2px solid #e8e8e8;
}
.table-row {
  display: flex;
  padding: 10px 16px;
  border-bottom: 1px solid #f0f0f0;
}
.table-row.clickable {
  cursor: pointer;
}
.table-row.clickable:hover {
  background: #f5f7fa;
}
.col-id { width: 200px; }
.col-name { flex: 1; }
.unit-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
}
.unit-card {
  background: #fafafa;
  border-radius: 6px;
  padding: 16px;
}
.unit-row {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  font-size: 13px;
  border-bottom: 1px solid #f0f0f0;
}
.unit-row .label {
  color: #666;
}
</style>
