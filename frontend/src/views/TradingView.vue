<template>
  <div class="content-section">
    <h2 class="section-title">市场交易</h2>
    <!-- 机组报价详情 -->
    <div v-if="g13Company" class="card">
      <!-- 调整后的顶端栏：左侧机组 + 中部日期 + 右侧按钮 -->
      <div class="card-header-row">
        <!-- 左侧：机组标签 -->
        <div class="tab-bar" style="margin-bottom: 0;">
          <button v-for="u in g13Company.units" :key="u.id"
                  :class="['tab-btn', { active: tradingUnit === u.id }]"
                  @click="tradingUnit = u.id">机组{{ u.id.replace('Thermal_','G') }}</button>
        </div>

        <!-- 新增：中部日期标签卡 -->
        <div class="date-tab-bar">
          <button 
            v-for="day in dateTabs" 
            :key="day.key"
            :class="['tab-btn', { active: currentDay === day.key }]"
            @click="handleDayChange(day.key)"
          >
            {{ day.label }}
          </button>
        </div>

        <!-- 右侧：功能按钮 -->
        <div>
          <button class="btn primary sm" @click="tradingSelected = null">提交报价</button>
          <button class="btn outline sm" style="margin-left: 8px;" @click="tradingSelected = null">取消</button>
          <button class="btn primary sm" style="margin-left: 8px;" @click="refreshData">刷新数据</button>
        </div>
      </div>

      <div class="trading-grid">
        <div class="trading-left">
          <h4>电能量市场申报</h4>
          <button class="btn outline sm" style="margin-bottom: 12px;" @click="tradingMode='bid'">选择策略报价</button>
          <button class="btn outline sm" style="margin-left: 8px;" @click="tradingMode='clear'">市场出清</button>
          <div class="data-table-wrap">
            <table class="data-table">
              <thead><tr><th>分段</th><th>起始出力(MW)</th><th>终止出力(MW)</th><th>分段报价(元/MWh)</th></tr></thead>
              <tbody>
                <tr v-for="(s, index) in bidSegments" :key="s.seg">
                  <td>{{ s.seg }}</td>
                  <td><input type="number" v-model.number="customBidSegments[index].start" min="0" step="1" class="input-sm"/></td>
                  <td><input type="number" v-model.number="customBidSegments[index].end" min="0" step="1" class="input-sm"/></td>
                  <td><input type="number" v-model.number="customBidSegments[index].price" min="0" step="0.1" class="input-sm"/></td>
                </tr>
                <tr v-if="bidSegments.length === 0">
                  <td colspan="4" style="text-align: center; color: #999;">暂无报价数据</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="trading-right">
          <h4>报价曲线</h4>
          <p class="chart-unit">电价(元/MWh)</p>
          <div class="svg-chart-wrap" style="height: 200px;">
            <svg viewBox="0 0 960 180" class="svg-chart">
              <line x1="40" y1="10" x2="40" y2="140" stroke="#e0e0e0" stroke-width="1"/>
              <line x1="40" y1="140" x2="920" y2="140" stroke="#e0e0e0" stroke-width="1"/>
              <text v-for="(v, i) in bidYLabels" :key="'by'+i" :x="36" :y="140 - (i / 5) * 130 + 4" text-anchor="end" font-size="9" fill="#999">{{ v }}</text>
              <line v-for="(v, i) in bidYLabels.slice(1)" :key="'bg'+i" x1="40" :y1="140 - ((i+1) / 5) * 130" x2="920" :y2="140 - ((i+1) / 5) * 130" stroke="#f0f0f0" stroke-width="0.5"/>
              <polyline :points="bidCurvePoints" fill="none" stroke="#1890ff" stroke-width="2"/>
              <text v-for="(v, i) in bidXLabels" :key="'bx'+i" :x="40 + (i / 9) * 880" y="155" text-anchor="middle" font-size="9" fill="#999">{{ v }}</text>
              <text x="480" y="172" text-anchor="middle" font-size="9" fill="#666">出力(MW)</text>
            </svg>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="card">
      <h3 class="card-title">加载中...</h3>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { marketApi } from "../api/market";

// 新增：日期标签配置
const dateTabs = [
  { key: 1, label: "第一天" },
  { key: 2, label: "第二天" },
  { key: 3, label: "第三天" },
  { key: 4, label: "第四天" },
  { key: 5, label: "第五天" },
  { key: 6, label: "第六天" },
  { key: 7, label: "第七天" }
];
// 新增：当前选中日期（默认第一天）
const currentDay = ref<number>(1);

const g13Company = ref<any>(null);
const tradingUnit = ref("Thermal_1");
const tradingMode = ref("bid");
const dayAheadQuotes = ref<any[]>([]);
const tradingSelected = ref<any>(null);
const customBidSegments = ref<any[]>([]);

// 新增：日期切换处理方法
const handleDayChange = (dayKey: number) => {
  currentDay.value = dayKey;
  // 这里先保留联动逻辑框架，后端接口实现后可补充：
  // 1. 调用接口时传递 currentDay.value 和 tradingUnit.value
  // 2. 重新初始化报价数据
  initCustomBidSegments();
};

async function fetchG13Company() {
  try {
    const { data } = await marketApi.getCompanies();
    const companies = data.items || [];
    // 查找G13企业（通过名称）
    g13Company.value = companies.find((c: any) => c.name === "G13") || null;
    if (g13Company.value && g13Company.value.units.length > 0) {
      // 设置默认机组
      tradingUnit.value = g13Company.value.units[0].id;
    }
  } catch (e) { 
    console.error("获取企业信息失败", e); 
  }
}

async function fetchTradingData() {
  try {
    const da = await marketApi.getDayAheadQuotes();
    dayAheadQuotes.value = da.data.items || [];
    // 初始化自定义报价数据
    initCustomBidSegments();
  } catch (e) { 
    console.error("获取交易数据失败", e); 
  }
}

async function refreshData() {
  await fetchG13Company();
  // 重置表单数据为0
  resetFormData();
}

function resetFormData() {
  // 将所有表单数值清0
  customBidSegments.value = customBidSegments.value.map((seg: any) => ({
    ...seg,
    start: 0,
    end: 0,
    price: 0
  }));
}

function initCustomBidSegments() {
  const filtered = dayAheadQuotes.value.filter(
    (q: any) => q.unit_id === tradingUnit.value && q.quote_time === 1
    // 后端实现后可添加日期筛选条件：
    // && q.quote_day === currentDay.value
  );
  let cumQty = 0;
  const segments = filtered.map((q: any, i: number) => {
    const start = cumQty;
    cumQty += q.quote_quantity;
    return { seg: i + 1, start, end: cumQty, price: q.quote_price };
  });
  customBidSegments.value = segments;
}

const bidSegments = computed(() => {
  return customBidSegments.value;
});

// 监听交易单位变化，重新初始化数据（保留日期）
watch(tradingUnit, () => {
  initCustomBidSegments();
});

// 新增：监听日期变化时打印日志（后端实现后可替换为真实逻辑）
watch(currentDay, () => {
  console.log(`切换到${currentDay.value}天，当前机组：${tradingUnit.value}`);
});

const bidCurveMaxOutput = computed(() => {
  const segs = bidSegments.value;
  return segs.length ? segs[segs.length - 1].end : 600;
});

const bidPriceRange = computed(() => {
  const segs = bidSegments.value;
  if (!segs.length) return { min: 0, max: 400 };
  const prices = segs.map((s: any) => s.price);
  const minP = Math.min(...prices);
  const maxP = Math.max(...prices);
  const range = maxP - minP;
  const padding = Math.max(range * 0.1, 5);
  const yMin = Math.max(0, Math.floor((minP - padding) / 5) * 5);
  const yMax = Math.ceil((maxP + padding) / 5) * 5;
  return { min: yMin, max: yMax };
});

const bidCurvePoints = computed(() => {
  const segs = bidSegments.value;
  if (!segs.length) return "";
  const maxOut = bidCurveMaxOutput.value;
  const { min: yMin, max: yMax } = bidPriceRange.value;
  const chartL = 40, chartR = 920, chartT = 10, chartB = 140;
  const w = chartR - chartL, h = chartB - chartT;
  const pts: string[] = [];
  for (const s of segs) {
    const x1 = chartL + (s.start / maxOut) * w;
    const x2 = chartL + (s.end / maxOut) * w;
    const y = chartB - ((s.price - yMin) / (yMax - yMin)) * h;
    pts.push(`${x1.toFixed(1)},${y.toFixed(1)}`);
    pts.push(`${x2.toFixed(1)},${y.toFixed(1)}`);
  }
  return pts.join(" ");
});

const bidXLabels = computed(() => {
  const max = bidCurveMaxOutput.value;
  const step = max / 9;
  return [0, Math.round(step), Math.round(step * 2), Math.round(step * 3), Math.round(step * 4), Math.round(step * 5), Math.round(step * 6), Math.round(step * 7), Math.round(step * 8), Math.round(max)];
});

const bidYLabels = computed(() => {
  const { min: yMin, max: yMax } = bidPriceRange.value;
  const step = (yMax - yMin) / 5;
  return [yMin, Math.round(yMin + step), Math.round(yMin + step * 2), Math.round(yMin + step * 3), Math.round(yMin + step * 4), yMax];
});

onMounted(() => {
  fetchG13Company();
  fetchTradingData();
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
/* 调整顶端栏样式：保证三部分垂直齐平 */
.card-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  gap: 16px; /* 增加元素间间距，避免拥挤 */
}
/* 新增：日期标签容器样式 */
.date-tab-bar {
  display: flex;
  gap: 0; /* 无间隙 */
  flex: 1; /* 占据中间剩余空间 */
  justify-content: center; /* 日期标签居中 */
  height: 36px; /* 与机组标签高度一致 */
}
.tab-bar {
  display: flex;
  gap: 0;
  margin-bottom: 16px;
  height: 36px; /* 统一高度 */
}
.tab-btn {
  padding: 8px 20px;
  border: 1px solid #d9d9d9;
  background: #fff;
  cursor: pointer;
  font-size: 14px;
  color: #333;
  transition: all 0.2s;
  border-radius: 0; /* 去掉所有圆角 */
  height: 100%; /* 高度铺满父容器 */
  box-sizing: border-box;
}
/* 移除原有圆角样式，保证无圆角 */
.tab-btn:first-child {
  border-radius: 0;
}
.tab-btn:last-child {
  border-radius: 0;
}
.tab-btn + .tab-btn {
  border-left: none;
}
.tab-btn.active {
  background: #1890ff;
  color: #fff;
  border-color: #1890ff;
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

.trading-grid {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-top: 16px;
}
.trading-left h4,
.trading-right h4 {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 8px;
}
.trading-right {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  width: 100%;
}

.trading-right h4 {
  width: 100%;
  text-align: center;
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 8px;
}

.trading-right .chart-unit {
  width: 100%;
  text-align: left;
  margin-left: 20px;
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
.input-sm {
  width: 100px;
  padding: 4px 8px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 13px;
  transition: all 0.2s;
}
.input-sm:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}
.svg-chart-wrap {
  width: 100%;
  height: 200px;
  position: relative;
  display: block;
  margin-left: 20px;
}
.svg-chart {
  width: 100%;
  height: 100%;
}
.chart-unit {
  font-size: 12px;
  color: #666;
  margin: 0 0 4px;
}
.btn {
  padding: 6px 16px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s;
}
.btn.primary {
  background: #1890ff;
  color: #fff;
  border-color: #1890ff;
}
.btn.primary:hover {
  background: #40a9ff;
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
