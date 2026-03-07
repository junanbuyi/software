<template>
  <div class="content-section">
    <div class="header-tabs">
      <div class="tab-bar">
        <button 
          v-for="t in disclosureTabs" 
          :key="t.key"
          :class="['tab-btn', { active: disclosureTab === t.key }]"
          @click="disclosureTab = t.key"
        >
          {{ t.label }}
        </button>
      </div>
      
      <div class="date-tab-bar">
        <button 
          v-for="day in dateTabs" 
          :key="day.key"
          :class="['date-tab-btn', { active: currentDay === day.key }]"
          @click="currentDay = day.key"
        >
          {{ day.label }}
        </button>
      </div>
    </div>

    <div class="card">
      <!-- 修复1：getCurrentDayLabel 是计算属性，不需要调用 -->
      <h3 class="card-title">{{ currentDisclosure.title }}（{{ getCurrentDayLabel }}）</h3>
      <div class="svg-chart-wrap">
        <svg viewBox="0 0 700 220" class="svg-chart">
          <line x1="50" y1="20" x2="50" y2="200" stroke="#e0e0e0" stroke-width="1"/>
          <line x1="50" y1="200" x2="690" y2="200" stroke="#e0e0e0" stroke-width="1"/>
          <text x="50" y="16" font-size="10" fill="#666" text-anchor="middle" font-weight="500">{{ currentDisclosure.unit }}</text>
          <text v-for="(v, i) in disclosureYLabels" :key="i" :x="45" :y="200 - i * (175/3) + 4" text-anchor="end" font-size="11" fill="#999">{{ v }}</text>
          <polyline :points="disclosureChartPoints" fill="none" :stroke="disclosureTab === 'wind' ? 'rgba(76,175,80,1)' : (disclosureTab === 'solar' ? 'rgba(255,215,0,1)' : '#1890ff')" stroke-width="2"/>
          <text v-for="(lbl, i) in periodLabels" :key="'d'+i" :x="50 + i * (640 / (periodLabels.length - 1))" y="218" text-anchor="middle" font-size="10" fill="#666">{{ lbl }}</text>
        </svg>
      </div>
      <div class="data-table-wrap" style="margin-top: 16px; overflow-x: auto;">
        <table class="data-table">
          <thead><tr><th>名称</th><th v-for="i in Math.min(disclosureData.length, 96)" :key="i">t{{ i }}</th></tr></thead>
          <tbody>
            <tr><td>{{ currentDisclosure.rowName }}</td><td v-for="(v, i) in disclosureData.slice(0, 96)" :key="i">{{ typeof v === 'number' ? v.toFixed(2) : v }}</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { marketApi } from "../api/market";

// 1. 定义数据类型接口
interface ItemData {
  values: number[];
}

// 2. 扩展接口参数类型（修复day参数报错）
interface GetOutResultsParams {
  sheet: string;
  row_index?: number;
  day?: number; // 新增day参数类型
}

// 3. 功能标签配置
const disclosureTabs = [
  { key: "price", label: "电价预测" },
  { key: "load", label: "负荷预测" },
  { key: "wind", label: "风电功率预测" },
  { key: "solar", label: "光伏功率预测" },
];

// 4. 日期标签配置
const dateTabs = [
  { key: 1, label: "第一天" },
  { key: 2, label: "第二天" },
  { key: 3, label: "第三天" },
  { key: 4, label: "第四天" },
  { key: 5, label: "第五天" },
  { key: 6, label: "第六天" },
  { key: 7, label: "第七天" },
];

// 5. 响应式变量
const disclosureTab = ref<string>("price");
const currentDay = ref<number>(1);
const disclosureData = ref<number[]>([]);

// 6. 功能配置映射
const disclosureSheetMap: Record<string, string> = {
  price: "energy_price", 
  load: "load_load_bid_power",
  wind: "wind_wt_opera_power", 
  solar: "solar_pv_opera_power",
};

const disclosureConfig: Record<string, { title: string; unit: string; rowName: string }> = {
  price: { title: "电价预测", unit: "电价(元/MWh)", rowName: "出清电价" },
  load: { title: "负荷预测", unit: "负荷(MW)", rowName: "总负荷功率" },
  wind: { title: "风电功率预测", unit: "风电功率(MW)", rowName: "风电消纳功率" },
  solar: { title: "光伏功率预测", unit: "光伏功率(MW)", rowName: "光伏功率" },
};

// 7. 计算属性
const currentDisclosure = computed(() => disclosureConfig[disclosureTab.value]);
// 修复2：计算属性直接取值，不是函数调用
const getCurrentDayLabel = computed(() => {
  const dayItem = dateTabs.find(item => item.key === currentDay.value);
  return dayItem?.label || "第一天";
});

// 8. 核心：数据请求函数
async function fetchDisclosureData() {
  try {
    const sheet = disclosureSheetMap[disclosureTab.value];
    // 修复3：指定参数类型，解决day属性报错
    const params: GetOutResultsParams = { 
      sheet, 
      day: currentDay.value 
    };
    // 如果接口暂时不支持day参数，可先注释day，后续联调再打开
    // const params: GetOutResultsParams = { sheet };
    
    // 修复4：调用接口时传入类型化的参数
    const { data } = await marketApi.getOutResults(params);
    
    const items: ItemData[] = data.items || [];
    if (items.length > 0) {
      if (disclosureTab.value === 'price') {
        disclosureData.value = items[0].values;
      } else {
        const periods = items[0].values.length;
        const totalValues = new Array(periods).fill(0);
        
        items.forEach((item: ItemData) => {
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
    console.error("数据请求失败：", e);
    disclosureData.value = []; 
  }
}

// 9. 监听事件
watch(disclosureTab, fetchDisclosureData);
watch(currentDay, fetchDisclosureData);

// 10. 图表相关计算属性
const disclosureChartPoints = computed(() => {
  const vals = disclosureData.value;
  if (!vals.length) return "";
  const maxVal = Math.max(...vals, 1);
  const step = 640 / Math.max(vals.length - 1, 1);
  return vals.map((v, i) => `${(50 + i * step).toFixed(1)},${(200 - (v / maxVal) * 175).toFixed(1)}`).join(" ");
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

// 11. 初始化
onMounted(() => {
  fetchDisclosureData();
});
</script>

<style scoped>
.content-section {
  max-width: 1100px;
}

.header-tabs {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.tab-bar {
  display: flex;
  gap: 0;
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

.date-tab-bar {
  display: flex;
  gap: 0;
}
.date-tab-btn {
  padding: 8px 16px;
  border: 1px solid #d9d9d9;
  border-radius: 0;
  background: #fff;
  cursor: pointer;
  font-size: 14px;
  color: #333;
  transition: all 0.2s;
}
.date-tab-btn.active {
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
