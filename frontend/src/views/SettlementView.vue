<template>
  <div class="content-section">
    <div class="tab-bar">
      <button :class="['tab-btn', { active: settlementTab === 'overview' }]" @click="settlementTab = 'overview'">市场总览</button>
      <button :class="['tab-btn', { active: settlementTab === 'analysis' }]" @click="settlementTab = 'analysis'">详情分析</button>
    </div>

    <!-- 市场总览 -->
    <div v-if="settlementTab === 'overview'">
      <div class="card">
        <div class="card-header-row">
          <h3 class="card-title">电能量市场结果</h3>
          <span class="score-badge">评分：80</span>
        </div>
        <div class="kv-list">
          <div class="kv-row"><span class="kv-label">总装机容量(100MW)</span><span class="kv-value">{{ overviewData.energy_market.total_capacity }}</span></div>
          <div class="kv-row"><span class="kv-label">发电企业数目</span><span class="kv-value">{{ overviewData.energy_market.plant_count }}</span></div>
          <div class="kv-row"><span class="kv-label">成交总出力(100MW)</span><span class="kv-value">{{ overviewData.energy_market.total_output }}</span></div>
          <div class="kv-row"><span class="kv-label">成交均价(元/MWh)</span><span class="kv-value">{{ overviewData.energy_market.avg_price }}</span></div>
          <div class="kv-row"><span class="kv-label">供需比</span><span class="kv-value">{{ overviewData.energy_market.supply_demand_ratio }}</span></div>
          <div class="kv-row"><span class="kv-label">总交易额(万元)</span><span class="kv-value">{{ overviewData.energy_market.total_revenue }}</span></div>
          <div class="kv-row"><span class="kv-label">阻塞情况</span><span class="kv-value">{{ overviewData.energy_market.congestion || '' }}</span></div>
          <div class="kv-row"><span class="kv-label">阻塞盈余(万元)</span><span class="kv-value">{{ overviewData.energy_market.congestion_surplus }}</span></div>
          <div class="kv-row"><span class="kv-label">申报机组数目</span><span class="kv-value">{{ overviewData.energy_market.quote_unit_count }}</span></div>
          <div class="kv-row"><span class="kv-label">中标机组数目</span><span class="kv-value">{{ overviewData.energy_market.bid_units }}</span></div>
          <div class="kv-row"><span class="kv-label">申报出力(MW)</span><span class="kv-value">{{ overviewData.energy_market.quote_quantity }}</span></div>
          <div class="kv-row"><span class="kv-label">申报均价(元/MWh)</span><span class="kv-value">{{ overviewData.energy_market.avg_quote_price }}</span></div>
          <div class="kv-row"><span class="kv-label">最高节点电价(元/MWh)</span><span class="kv-value">{{ overviewData.energy_market.max_node_price }}</span></div>
          <div class="kv-row"><span class="kv-label">最低节点电价(元/MWh)</span><span class="kv-value">{{ overviewData.energy_market.min_node_price }}</span></div>
          <div class="kv-row"><span class="kv-label">传输网损(100MW)</span><span class="kv-value">{{ overviewData.energy_market.transmission_loss }}</span></div>
          <div class="kv-row"><span class="kv-label">总发电量(MWh)</span><span class="kv-value">{{ overviewData.energy_market.total_generation }}</span></div>
          <div class="kv-row"><span class="kv-label">总用电量(MWh)</span><span class="kv-value">{{ overviewData.energy_market.total_consumption }}</span></div>
          <div class="kv-row"><span class="kv-label">新能源总弃电量(MWh)</span><span class="kv-value">{{ overviewData.energy_market.re_curtailment }}</span></div>
          <div class="kv-row"><span class="kv-label">最大新能源弃电比例</span><span class="kv-value">{{ overviewData.energy_market.max_re_curtailment_ratio }}</span></div>
          <div class="kv-row"><span class="kv-label">总切负荷量(100MW)</span><span class="kv-value">{{ overviewData.energy_market.total_load_shedding }}</span></div>
          <div class="kv-row"><span class="kv-label">最大失负荷容量比例</span><span class="kv-value">{{ overviewData.energy_market.max_load_loss_ratio }}</span></div>
        </div>
      </div>

      <!-- 饼状图：机组数量 & 装机容量 -->
      <div class="card" style="margin-top: 20px;">
        <div class="pie-chart-row">
          <div class="pie-chart-item">
            <h4 class="pie-title">机组数量分布</h4>
            <svg viewBox="0 0 180 180" class="pie-svg">
              <path v-for="(arc, i) in countArcs" :key="'c'+i" :d="arc.path" :fill="arc.color" stroke="#fff" stroke-width="1.5"/>
              <text v-for="(arc, i) in countArcs" :key="'cl'+i" :x="arc.lx" :y="arc.ly" text-anchor="middle" dominant-baseline="central" font-size="11" fill="#fff" font-weight="600">{{ arc.pct }}%</text>
            </svg>
            <div class="pie-legend">
              <span v-for="(arc, i) in countArcs" :key="'clg'+i" class="legend-item">
                <span class="legend-color" :style="{ background: arc.color }"></span>{{ arc.name }} {{ arc.value }}
              </span>
            </div>
          </div>
          <div class="pie-chart-item">
            <h4 class="pie-title">装机容量分布(100MW)</h4>
            <svg viewBox="0 0 180 180" class="pie-svg">
              <path v-for="(arc, i) in capacityArcs" :key="'p'+i" :d="arc.path" :fill="arc.color" stroke="#fff" stroke-width="1.5"/>
              <text v-for="(arc, i) in capacityArcs" :key="'pl'+i" :x="arc.lx" :y="arc.ly" text-anchor="middle" dominant-baseline="central" font-size="11" fill="#fff" font-weight="600">{{ arc.pct }}%</text>
            </svg>
            <div class="pie-legend">
              <span v-for="(arc, i) in capacityArcs" :key="'plg'+i" class="legend-item">
                <span class="legend-color" :style="{ background: arc.color }"></span>{{ arc.name }} {{ arc.value }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 电力电量平衡表单图 -->
      <div class="card" style="margin-top: 20px;">
        <h3 class="card-title">电力电量平衡表单</h3>
        <div class="svg-chart-wrap" style="height: 260px;">
          <svg viewBox="0 0 700 260" class="svg-chart">
            <line x1="50" y1="10" x2="50" y2="230" stroke="#e0e0e0" stroke-width="1"/>
            <line x1="50" y1="230" x2="690" y2="230" stroke="#e0e0e0" stroke-width="1"/>
            <text x="10" y="130" font-size="10" fill="#666" transform="rotate(-90,10,130)">功率(100MW)</text>
            <text v-for="(v, i) in balanceYLabels" :key="i" :x="46" :y="230 - (i/3)*210 + 4" text-anchor="end" font-size="10" fill="#999">{{ v }}</text>
            <polygon :points="balanceAreaPoints" fill="rgba(255,72,72,0.8)" stroke="none"/>
            <polygon :points="windAreaPoints" fill="rgba(76,175,80,0.8)" stroke="none"/>
            <polygon :points="solarAreaPoints" fill="rgba(255,215,0,0.8)" stroke="none"/>
            <polygon :points="hydroAreaPoints" fill="rgba(24,144,255,0.8)" stroke="none"/>
            <polyline :points="loadLinePoints" fill="none" stroke="#333" stroke-width="2"/>
            <text x="370" y="255" text-anchor="middle" font-size="10" fill="#666">时段/15min</text>
          </svg>
        </div>
        <div class="legend-row">
          <span class="legend-item"><span class="legend-color" style="background:rgba(255,72,72,0.8)"></span>火电功率</span>
          <span class="legend-item"><span class="legend-color" style="background:rgba(76,175,80,0.8)"></span>风电功率</span>
          <span class="legend-item"><span class="legend-color" style="background:rgba(255,215,0,0.8)"></span>光伏功率</span>
          <span class="legend-item"><span class="legend-color" style="background:rgba(24,144,255,0.8)"></span>水电功率</span>
          <span class="legend-item"><span class="legend-color" style="background:#333"></span>总负荷功率</span>
        </div>
      </div>

      <!-- 出清电价图表 -->
      <div class="card" style="margin-top: 20px;">
        <h3 class="card-title">电能量市场出清电价</h3>
        <p class="chart-unit">电价(元/MWh)</p>
        <div class="svg-chart-wrap">
          <svg viewBox="0 0 700 220" class="svg-chart">
            <line x1="50" y1="10" x2="50" y2="200" stroke="#e0e0e0" stroke-width="1"/>
            <line x1="50" y1="200" x2="690" y2="200" stroke="#e0e0e0" stroke-width="1"/>
            <text v-for="(v, i) in [0, 100, 200, 300]" :key="i" :x="45" :y="200 - i * 60 + 4" text-anchor="end" font-size="11" fill="#999">{{ v }}</text>
            <polyline :points="clearingChartPoints" fill="none" stroke="#1890ff" stroke-width="2"/>
            <text v-for="i in 7" :key="'cl'+i" :x="50 + (i-1) * 91.4 + 45" y="218" text-anchor="middle" font-size="11" fill="#666">时段{{ (i-1)*14+1 }}</text>
          </svg>
        </div>
      </div>
    </div>

    <!-- 详情分析 -->
    <div v-if="settlementTab === 'analysis'">
      <div class="card">
        <h3 class="card-title">电能量市场中标结果</h3>
        <div class="data-table-wrap">
          <table class="data-table">
            <thead><tr><th>火电厂编号</th><th>火电厂名称</th><th>运行成本(万元)</th><th>开机成本(万元)</th><th>关机成本(万元)</th><th>总中标出力(MW)</th><th>中标电量均价(元/MWh)</th><th>总中标收益(万元)</th><th>净收益(万元)</th></tr></thead>
            <tbody>
              <tr v-for="r in settlementRows" :key="r.id">
                <td>{{ r.id }}</td><td>{{ r.name }}</td><td>{{ r.opCost }}</td><td>{{ r.startCost }}</td><td>{{ r.stopCost }}</td><td>{{ r.output }}</td><td>{{ r.avgPrice }}</td><td>{{ r.revenue }}</td><td>{{ r.netIncome }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 自主报价结果 -->
      <div class="card" style="margin-top: 20px;">
        <div>
          <h4>电能量市场中标结果</h4>
          <p class="note">中标出力单位为MW，中标均价单位为元/MWh</p>
          <div class="data-table-wrap">
            <table class="data-table">
              <thead><tr><th>机组编号</th><th>类型</th><th v-for="i in Math.min(historyEnergyDetail[0]?.values?.length || 0, 6)" :key="i">时段{{ i }}</th></tr></thead>
              <tbody>
                <tr v-for="row in historyEnergyDetail.slice(0, 8)" :key="row.row_index">
                  <td>Thermal_{{ row.row_index + 1 }}</td>
                  <td>中标出力</td>
                  <td v-for="(v, i) in row.values.slice(0, 6)" :key="i">{{ typeof v === 'number' ? v.toFixed(2) : v }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { marketApi } from "../api/market";

const settlementTab = ref("overview");
const overviewData = ref<any>({ energy_market: {} });
const settlementRows = ref<any[]>([]);
const historyEnergyDetail = ref<any[]>([]);
const balanceChart = ref<any>({ thermal: [], wind: [], solar: [], hydro: [], load: [], periods: 96 });
const energyPriceData = ref<number[]>([]);

async function fetchSettlementData() {
  try {
    const [ov, dt] = await Promise.all([
      marketApi.getSettlementOverview(),
      marketApi.getSettlementDetail(),
    ]);
    overviewData.value = ov.data;
    settlementRows.value = dt.data.energy_rows || [];
  } catch (e) { 
    console.error("获取结算数据失败", e); 
  }
}

async function fetchHistoryDetail() {
  try {
    const res = await marketApi.getOutResults({ sheet: "thermal_tg_opera_power" });
    historyEnergyDetail.value = res.data.items || [];
  } catch (e) { 
    console.error("获取历史详情失败", e); 
  }
}

async function fetchBalanceChart() {
  try {
    const { data } = await marketApi.getBalanceChart();
    balanceChart.value = data;
  } catch (e) { 
    console.error("获取平衡图表失败", e); 
  }
}

async function fetchEnergyPriceChart() {
  try {
    const { data } = await marketApi.getOutResults({ sheet: "energy_price", row_index: 0 });
    const items = data.items || [];
    energyPriceData.value = items.length > 0 ? items[0].values : [];
  } catch (e) { 
    console.error("获取出清电价失败", e); 
  }
}

// 饼状图数据
const pieColors = ["rgba(76,175,80,0.8)", "rgba(255,215,0,0.8)", "rgba(24,144,255,0.8)", "rgba(255,72,72,0.8)", "rgba(114,46,209,0.8)"];
const pieTypes = ["风电", "光伏", "水电", "火电", "电化学储能", "抽蓄电站"];

const countPieData = computed(() => {
  const em = overviewData.value.energy_market;
  if (!em) return [];
  const raw = [
    { name: "风电", value: em.wind_count || 0 },
    { name: "光伏", value: em.solar_count || 0 },
    { name: "水电", value: em.hydro_count || 0 },
    { name: "火电", value: em.thermal_count || 0 },
    { name: "电化学储能", value: em.storage_count || 0 },
    { name: "抽蓄电站", value: em.pumped_storage_count || 0 },
  ];
  return raw.filter(d => d.value > 0);
});

const capacityPieData = computed(() => {
  const em = overviewData.value.energy_market;
  if (!em) return [];
  const raw = [
    { name: "风电", value: em.wind_capacity || 0 },
    { name: "光伏", value: em.solar_capacity || 0 },
    { name: "水电", value: em.hydro_capacity || 0 },
    { name: "火电", value: em.thermal_capacity || 0 },
    { name: "电化学储能", value: 0 },
    { name: "抽蓄电站", value: 0 },
  ];
  return raw.filter(d => d.value > 0);
});

function pieArcs(data: { name: string; value: number }[]) {
  const total = data.reduce((s, d) => s + d.value, 0);
  if (total === 0) return [];
  const cx = 90, cy = 90, r = 80;
  let startAngle = -Math.PI / 2;
  return data.map((d, i) => {
    const angle = (d.value / total) * Math.PI * 2;
    const endAngle = startAngle + angle;
    const x1 = cx + r * Math.cos(startAngle);
    const y1 = cy + r * Math.sin(startAngle);
    const x2 = cx + r * Math.cos(endAngle);
    const y2 = cy + r * Math.sin(endAngle);
    const large = angle > Math.PI ? 1 : 0;
    const path = data.length === 1
      ? `M ${cx} ${cy - r} A ${r} ${r} 0 1 1 ${cx - 0.01} ${cy - r} Z`
      : `M ${cx} ${cy} L ${x1} ${y1} A ${r} ${r} 0 ${large} 1 ${x2} ${y2} Z`;
    const midAngle = startAngle + angle / 2;
    const labelR = r * 0.6;
    const lx = cx + labelR * Math.cos(midAngle);
    const ly = cy + labelR * Math.sin(midAngle);
    const pct = Math.round(d.value / total * 100);
    startAngle = endAngle;
    const colorIdx = pieTypes.indexOf(d.name);
    return { path, color: pieColors[colorIdx >= 0 ? colorIdx : i], name: d.name, value: d.value, pct, lx, ly };
  });
}

const countArcs = computed(() => pieArcs(countPieData.value));
const capacityArcs = computed(() => pieArcs(capacityPieData.value));

// 平衡图表计算
const balanceMaxY = computed(() => {
  const all = [
    ...balanceChart.value.thermal,
    ...balanceChart.value.load,
    ...(balanceChart.value.thermal.map((v: number, i: number) => v + (balanceChart.value.wind[i] || 0) + (balanceChart.value.solar[i] || 0) + (balanceChart.value.hydro[i] || 0))),
  ];
  return Math.max(...all, 1);
});

const toBalanceY = (v: number) => {
  const max = balanceMaxY.value;
  return 230 - (v / max) * 210;
};

const balanceAreaPoints = computed(() => {
  const data = balanceChart.value.thermal;
  if (!data.length) return "";
  const n = data.length;
  const step = 640 / (n - 1);
  const top = data.map((v: number, i: number) => `${(50 + i * step).toFixed(1)},${toBalanceY(v).toFixed(1)}`);
  const bottom = `${(50 + (n - 1) * step).toFixed(1)},${toBalanceY(0)} 50,${toBalanceY(0)}`;
  return top.join(" ") + " " + bottom;
});

const windAreaPoints = computed(() => {
  const thermal = balanceChart.value.thermal;
  const wind = balanceChart.value.wind;
  if (!thermal.length || !wind.length) return "";
  const n = thermal.length;
  const step = 640 / (n - 1);
  const top = wind.map((_: number, i: number) => `${(50 + i * step).toFixed(1)},${toBalanceY(thermal[i]).toFixed(1)}`);
  const topWind = wind.map((v: number, i: number) => `${(50 + i * step).toFixed(1)},${toBalanceY(thermal[i] + v).toFixed(1)}`);
  return topWind.join(" ") + " " + [...top].reverse().join(" ");
});

const solarAreaPoints = computed(() => {
  const thermal = balanceChart.value.thermal;
  const wind = balanceChart.value.wind;
  const solar = balanceChart.value.solar;
  if (!thermal.length || !wind.length || !solar.length) return "";
  const n = thermal.length;
  const step = 640 / (n - 1);
  const top = wind.map((_: number, i: number) => `${(50 + i * step).toFixed(1)},${toBalanceY(thermal[i] + wind[i]).toFixed(1)}`);
  const topSolar = solar.map((v: number, i: number) => `${(50 + i * step).toFixed(1)},${toBalanceY(thermal[i] + wind[i] + v).toFixed(1)}`);
  return topSolar.join(" ") + " " + [...top].reverse().join(" ");
});

const hydroAreaPoints = computed(() => {
  const thermal = balanceChart.value.thermal;
  const wind = balanceChart.value.wind;
  const solar = balanceChart.value.solar;
  const hydro = balanceChart.value.hydro;
  if (!thermal.length || !wind.length || !solar.length || !hydro.length) return "";
  const n = thermal.length;
  const step = 640 / (n - 1);
  const top = wind.map((_: number, i: number) => `${(50 + i * step).toFixed(1)},${toBalanceY(thermal[i] + wind[i] + solar[i]).toFixed(1)}`);
  const topHydro = hydro.map((v: number, i: number) => `${(50 + i * step).toFixed(1)},${toBalanceY(thermal[i] + wind[i] + solar[i] + v).toFixed(1)}`);
  return topHydro.join(" ") + " " + [...top].reverse().join(" ");
});

const loadLinePoints = computed(() => {
  const data = balanceChart.value.load;
  if (!data.length) return "";
  const n = data.length;
  const step = 640 / (n - 1);
  return data.map((v: number, i: number) => `${(50 + i * step).toFixed(1)},${toBalanceY(v).toFixed(1)}`).join(" ");
});

const balanceYLabels = computed(() => {
  const max = balanceMaxY.value;
  return [0, Math.round(max / 3), Math.round(max * 2 / 3), Math.round(max)];
});

const clearingChartPoints = computed(() => {
  const vals = energyPriceData.value;
  if (!vals.length) return "";
  const maxVal = Math.max(...vals, 1);
  const step = 640 / Math.max(vals.length - 1, 1);
  return vals.map((v, i) => `${(50 + i * step).toFixed(1)},${(200 - (v / maxVal) * 180).toFixed(1)}`).join(" ");
});

onMounted(() => {
  fetchSettlementData();
  fetchHistoryDetail();
  fetchBalanceChart();
  fetchEnergyPriceChart();
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
.card-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.score-badge {
  font-size: 18px;
  font-weight: 700;
  color: #333;
}
.kv-list {
  display: flex;
  flex-direction: column;
}
.kv-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 13px;
  border-bottom: 1px solid #f5f5f5;
}
.kv-label {
  color: #555;
}
.kv-value {
  color: #333;
  font-weight: 500;
  text-align: right;
  min-width: 140px;
}
.pie-chart-row {
  display: flex;
  gap: 40px;
  justify-content: center;
  margin: 16px 0;
}
.pie-chart-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.pie-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px;
}
.pie-svg {
  width: 180px;
  height: 180px;
}
.pie-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 16px;
  justify-content: center;
  margin-top: 8px;
  font-size: 12px;
  color: #555;
}
.legend-row {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-top: 8px;
  font-size: 12px;
  color: #555;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
}
.legend-color {
  display: inline-block;
  width: 14px;
  height: 10px;
  border-radius: 2px;
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
.note {
  font-size: 12px;
  color: #999;
  margin: 0 0 8px;
}
</style>
