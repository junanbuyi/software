<template>
  <div class="content-section">
    <div class="tab-bar">
      <button v-for="t in disclosureTabs" :key="t.key"
              :class="['tab-btn', { active: disclosureTab === t.key }]"
              @click="disclosureTab = t.key">{{ t.label }}</button>
    </div>
    <div class="card">
      <h3 class="card-title">{{ currentDisclosure.title }}</h3>
      <p class="chart-unit">{{ currentDisclosure.unit }}</p>
      <div class="svg-chart-wrap">
        <svg viewBox="0 0 700 220" class="svg-chart">
          <line x1="50" y1="10" x2="50" y2="200" stroke="#e0e0e0" stroke-width="1"/>
          <line x1="50" y1="200" x2="690" y2="200" stroke="#e0e0e0" stroke-width="1"/>
          <text v-for="(v, i) in disclosureYLabels" :key="i" :x="45" :y="200 - i * (190/3) + 4" text-anchor="end" font-size="11" fill="#999">{{ v }}</text>
          <polyline :points="disclosureChartPoints" fill="none" :stroke="disclosureTab === 'wind' ? 'rgba(76,175,80,1)' : (disclosureTab === 'solar' ? 'rgba(255,215,0,1)' : '#1890ff')" stroke-width="2"/>
          <text v-for="(lbl, i) in periodLabels" :key="'d'+i" :x="50 + i * (640 / (periodLabels.length - 1))" y="218" text-anchor="middle" font-size="10" fill="#666">{{ lbl }}</text>
        </svg>
      </div>
      <div class="data-table-wrap" style="margin-top: 16px;">
        <table class="data-table">
          <thead><tr><th>名称</th><th v-for="i in Math.min(disclosureData.length, 10)" :key="i">t{{ i }}</th></tr></thead>
          <tbody>
            <tr><td>{{ currentDisclosure.rowName }}</td><td v-for="(v, i) in disclosureData.slice(0, 10)" :key="i">{{ typeof v === 'number' ? v.toFixed(2) : v }}</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { marketApi } from "../api/market";

const disclosureTabs = [
  { key: "price", label: "电价预测" },
  { key: "load", label: "负荷预测" },
  { key: "wind", label: "风电功率预测" },
  { key: "solar", label: "光伏功率预测" },
];

const disclosureTab = ref("price");
const disclosureSheetMap: Record<string, string> = {
  price: "energy_price", 
  load: "load_load_bid_power",
  wind: "wind_wt_opera_power", 
  solar: "solar_pv_opera_power",
};

const disclosureConfig: Record<string, { title: string; unit: string; rowName: string }> = {
  price: { title: "电价预测", unit: "电价(元/MWh)", rowName: "出清电价" },
  load: { title: "负荷预测", unit: "负荷(100MW)", rowName: "总负荷功率" },
  wind: { title: "风电功率预测", unit: "风电功率(100MW)", rowName: "风电消纳功率" },
  solar: { title: "光伏功率预测", unit: "光伏功率(100MW)", rowName: "光伏功率" },
};

const currentDisclosure = computed(() => disclosureConfig[disclosureTab.value]);
const disclosureData = ref<number[]>([]);

async function fetchDisclosureData() {
  try {
    const sheet = disclosureSheetMap[disclosureTab.value];
    const { data } = await marketApi.getOutResults({ sheet });
    const items = data.items || [];
    if (items.length > 0) {
      if (disclosureTab.value === 'price') {
        // 电价数据不需要累加，只取第一个
        disclosureData.value = items[0].values;
      } else {
        // 其他数据（负荷、风电、光伏）需要累加所有机组的数据
        const periods = items[0].values.length;
        const totalValues = new Array(periods).fill(0);
        items.forEach(item => {
          item.values.forEach((value: number, index: number) => {
            totalValues[index] += value;
          });
        });
        disclosureData.value = totalValues;
      }
    } else {
      disclosureData.value = [];
    }
  } catch (e) { 
    disclosureData.value = []; 
  }
}

watch(disclosureTab, fetchDisclosureData);

const disclosureChartPoints = computed(() => {
  const vals = disclosureData.value;
  if (!vals.length) return "";
  const maxVal = Math.max(...vals, 1);
  const step = 640 / Math.max(vals.length - 1, 1);
  return vals.map((v, i) => `${(50 + i * step).toFixed(1)},${(200 - (v / maxVal) * 180).toFixed(1)}`).join(" ");
});

const periodLabels = computed(() => {
  return ["0:00", "4:00", "8:00", "12:00", "16:00", "20:00", "24:00"];
});

const disclosureYLabels = computed(() => {
  const vals = disclosureData.value;
  if (!vals.length) return [0, 100, 200, 300];
  const maxVal = Math.max(...vals, 1);
  const step = maxVal / 3;
  return [0, Math.round(step), Math.round(step * 2), Math.round(maxVal)];
});

onMounted(() => {
  fetchDisclosureData();
});
</script>

<style scoped>
.content-section {
  max-width: 1100px;
}
.tab-bar {
  display: flex;
  gap: 0;
  margin-bottom: 16px;
}
.tab-btn {
  padding: 8px 20px;
  border: 1px solid #d9d9d9;
  background: #fff;
  cursor: pointer;
  font-size: 14px;
  color: #333;
  transition: all 0.2s;
}
.tab-btn:first-child {
  border-radius: 4px 0 0 4px;
}
.tab-btn:last-child {
  border-radius: 0 4px 4px 0;
}
.tab-btn + .tab-btn {
  border-left: none;
}
.tab-btn.active {
  background: #1890ff;
  color: #fff;
  border-color: #1890ff;
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
.svg-chart-wrap {
  width: 100%;
  height: 220px;
  position: relative;
}
.svg-chart {
  width: 100%;
  height: 100%;
}
.chart-unit {
  font-size: 12px;
  color: #1890ff;
  margin: 0 0 4px;
}
.data-table-wrap {
  overflow-x: auto;
}
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
.data-table th {
  padding: 8px 12px;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #e8e8e8;
  white-space: nowrap;
}
.data-table td {
  padding: 8px 12px;
  border-bottom: 1px solid #f0f0f0;
  color: #555;
  white-space: nowrap;
}
</style>
