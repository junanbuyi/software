<template>
  <div class="content-section">
    <h2 class="section-title">企业信息</h2>
    <!-- G13企业详情 -->
    <div v-if="g13Company" class="card">
      <h3 class="card-title">企业名称：{{ g13Company.name }} 企业类型：火电公司</h3>
      <h4 style="margin: 16px 0 12px; font-size: 15px;">机组信息</h4>
      <div class="unit-grid">
        <div v-for="u in g13Company.units" :key="u.id" class="unit-card">
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
    <div v-else-if="error" class="card">
      <h3 class="card-title" style="color: #ff4d4f;">错误</h3>
      <p>{{ error }}</p>
      <div v-if="companiesList.length > 0">
        <h4 style="margin: 16px 0 12px; font-size: 14px;">可用企业列表:</h4>
        <ul style="margin: 0; padding-left: 20px;">
          <li v-for="c in companiesList" :key="c.id">{{ c.id }} - {{ c.name }}</li>
        </ul>
      </div>
    </div>
    <div v-else class="card">
      <h3 class="card-title">加载中...</h3>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { marketApi } from "../api/market";

const g13Company = ref<any>(null);
const error = ref<string | null>(null);
const companiesList = ref<any[]>([]);

async function fetchG13Company() {
  try {
    error.value = null;
    const { data } = await marketApi.getCompanies();
    const companies = data.items || [];
    companiesList.value = companies;
    console.log("所有企业:", companies);
    // 查找G13企业（通过名称）
    g13Company.value = companies.find((c: any) => c.name === "G13") || null;
    if (!g13Company.value) {
      console.log("未找到G13企业，企业列表:", companies.map((c: any) => ({ id: c.id, name: c.name })));
    } else {
      console.log("找到G13企业:", g13Company.value);
    }
  } catch (e) { 
    console.error("获取企业信息失败", e); 
    error.value = "获取企业信息失败，请检查网络连接";
  }
}

onMounted(() => {
  fetchG13Company();
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
