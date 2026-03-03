<template>
  <div class="content-section">
    <h2 class="section-title">市场交易</h2>
    <!-- 企业列表 -->
    <div v-if="!tradingSelected" class="card">
      <div class="card-header-row">
        <h3 class="card-title">企业列表</h3>
        <div>
          <button class="btn primary sm" @click="tradingMode = 'bid'">选择边际报价</button>
          <button class="btn primary sm" style="margin-left: 8px;" @click="tradingMode = 'clear'">市场出清</button>
        </div>
      </div>
      <div class="simple-table">
        <div class="table-header">
          <span class="col col-id">#火电厂编号</span>
          <span class="col col-name">火电厂名称</span>
        </div>
        <div v-for="c in companies" :key="c.id" class="table-row clickable" @click="tradingSelected = c">
          <span class="col col-id">{{ c.id }}</span>
          <span class="col col-name">{{ c.name }}</span>
        </div>
      </div>
    </div>
    <!-- 机组报价详情 -->
    <div v-else class="card">
      <div class="card-header-row">
        <div class="tab-bar" style="margin-bottom: 0;">
          <button v-for="u in tradingSelected.units" :key="u.id"
                  :class="['tab-btn', { active: tradingUnit === u.id }]"
                  @click="tradingUnit = u.id">机组{{ u.id.replace('Thermal_','G') }}</button>
        </div>
        <div>
          <button class="btn primary sm" @click="tradingSelected = null">提交</button>
          <button class="btn outline sm" style="margin-left: 8px;" @click="tradingSelected = null">取消</button>
        </div>
      </div>
      <div class="trading-grid">
        <div class="trading-left">
          <h4>电能量市场申报</h4>
          <button class="btn outline sm" style="margin-bottom: 12px;">选择边际报价</button>
          <div class="data-table-wrap">
            <table class="data-table">
              <thead><tr><th>分段</th><th>起始出力(MW)</th><th>终止出力(MW)</th><th>分段报价(元/MWh)</th></tr></thead>
              <tbody>
                <tr v-for="s in bidSegments" :key="s.seg">
                  <td>{{ s.seg }}</td><td>{{ s.start }}</td><td>{{ s.end }}</td><td>{{ s.price }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="trading-right">
          <h4>报价曲线</h4>
          <p class="chart-unit">电价(元/MWh)</p>
          <div class="svg-chart-wrap" style="height: 180px;">
            <svg viewBox="0 0 300 180" class="svg-chart">
              <line x1="40" y1="10" x2="40" y2="140" stroke="#e0e0e0" stroke-width="1"/>
              <line x1="40" y1="140" x2="280" y2="140" stroke="#e0e0e0" stroke-width="1"/>
              <text v-for="(v, i) in bidYLabels" :key="'by'+i" :x="36" :y="140 - (i / 3) * 130 + 4" text-anchor="end" font-size="9" fill="#999">{{ v }}</text>
              <line v-for="(v, i) in bidYLabels.slice(1)" :key="'bg'+i" x1="40" :y1="140 - ((i+1) / 3) * 130" x2="280" :y2="140 - ((i+1) / 3) * 130" stroke="#f0f0f0" stroke-width="0.5"/>
              <polyline :points="bidCurvePoints" fill="none" stroke="#1890ff" stroke-width="2"/>
              <text v-for="(v, i) in bidXLabels" :key="'bx'+i" :x="40 + (i / 4) * 240" y="155" text-anchor="middle" font-size="9" fill="#999">{{ v }}</text>
              <text x="160" y="172" text-anchor="middle" font-size="9" fill="#666">出力(MW)</text>
            </svg>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { marketApi } from "../api/market";

const companies = ref<any[]>([]);
const tradingSelected = ref<any>(null);
const tradingUnit = ref("Thermal_1");
const tradingMode = ref("bid");
const dayAheadQuotes = ref<any[]>([]);

async function fetchCompanies() {
  try {
    const { data } = await marketApi.getCompanies();
    companies.value = data.items || [];
  } catch (e) { 
    console.error("获取企业信息失败", e); 
  }
}

async function fetchTradingData() {
  try {
    const da = await marketApi.getDayAheadQuotes();
    dayAheadQuotes.value = da.data.items || [];
  } catch (e) { 
    console.error("获取交易数据失败", e); 
  }
}

const bidSegments = computed(() => {
  const filtered = dayAheadQuotes.value.filter(
    (q: any) => q.unit_id === tradingUnit.value && q.quote_time === 1
  );
  let cumQty = 0;
  return filtered.map((q: any, i: number) => {
    const start = cumQty;
    cumQty += q.quote_quantity;
    return { seg: i + 1, start, end: cumQty, price: q.quote_price };
  });
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
  const padding = Math.max(range * 0.3, 10);
  const yMin = Math.max(0, Math.floor((minP - padding) / 10) * 10);
  const yMax = Math.ceil((maxP + padding) / 10) * 10;
  return { min: yMin, max: yMax };
});

const bidCurvePoints = computed(() => {
  const segs = bidSegments.value;
  if (!segs.length) return "";
  const maxOut = bidCurveMaxOutput.value;
  const { min: yMin, max: yMax } = bidPriceRange.value;
  const chartL = 40, chartR = 280, chartT = 10, chartB = 140;
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
  const step = max / 4;
  return [0, Math.round(step), Math.round(step * 2), Math.round(step * 3), Math.round(max)];
});

const bidYLabels = computed(() => {
  const { min: yMin, max: yMax } = bidPriceRange.value;
  const step = (yMax - yMin) / 3;
  return [yMin, Math.round(yMin + step), Math.round(yMin + step * 2), yMax];
});

onMounted(() => {
  fetchCompanies();
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
.card-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
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
.trading-grid {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 24px;
  margin-top: 16px;
}
.trading-left h4,
.trading-right h4 {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 8px;
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
