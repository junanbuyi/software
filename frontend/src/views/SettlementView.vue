<template>
  <div class="content-section">
    <!-- 调整后的顶部栏：左侧Tab + 右侧日期标签 -->
    <div class="top-operation-bar">
      <div class="tab-bar">
        <button :class="['tab-btn', { active: settlementTab === 'overview' }]" @click="handleTabChange('overview')">市场总览</button>
        <button :class="['tab-btn', { active: settlementTab === 'analysis' }]" @click="handleTabChange('analysis')">详情分析</button>
      </div>
      
      <!-- 新增：右上角日期标签栏 -->
      <div class="date-tab-bar">
        <button 
          v-for="day in dateTabs" 
          :key="day.key"
          :class="['date-tab-btn', { active: currentDay === day.key }]"
          @click="handleDayChange(day.key)"
        >
          {{ day.label }}
        </button>
      </div>
    </div>

    <!-- 市场总览 -->
    <div v-if="settlementTab === 'overview'">
      <div class="card">
        <div class="card-header-row">
          <!-- 标题随日期变化 -->
          <h3 class="card-title">{{ currentDayLabel }} 电能量市场结果</h3>
          <span class="score-badge">评分：80</span>
        </div>
        <div class="market-results">
          <!-- 第一行：电价相关 -->
          <div class="result-row row-1">
            <div class="result-item">
              <div class="result-value">{{ overviewData.energy_market.avg_price || 0 }}</div>
              <div class="result-label">成交均价(元/MWh)</div>
            </div>
            <div class="result-item">
              <div class="result-value">{{ overviewData.energy_market.max_node_price || 0 }}</div>
              <div class="result-label">最高节点电价(元/MWh)</div>
            </div>
            <div class="result-item">
              <div class="result-value">{{ overviewData.energy_market.min_node_price || 0 }}</div>
              <div class="result-label">最低节点电价(元/MWh)</div>
            </div>
            <div class="result-item">
              <div class="result-value">{{ overviewData.energy_market.avg_quote_price || 0 }}</div>
              <div class="result-label">申报均价(元/MWh)</div>
            </div>
            <div class="result-item">
              <div class="result-value">{{ overviewData.energy_market.supply_demand_ratio || 0 }}</div>
              <div class="result-label">供需比</div>
            </div>
          </div>
          <!-- 第二行：电量相关 -->
          <div class="result-row row-2">
            <div class="result-item">
              <div class="result-value">{{ overviewData.energy_market.total_generation || 0 }}</div>
              <div class="result-label">总发电量(MWh)</div>
            </div>
            <div class="result-item">
              <div class="result-value">{{ overviewData.energy_market.total_consumption || 0 }}</div>
              <div class="result-label">总用电量(MWh)</div>
            </div>
            <div class="result-item">
              <div class="result-value">{{ overviewData.energy_market.re_curtailment || 0 }}</div>
              <div class="result-label">新能源总弃电量(MWh)</div>
            </div>
            <div class="result-item">
              <div class="result-value">{{ overviewData.energy_market.quote_quantity || 0 }}</div>
              <div class="result-label">申报出力(MW)</div>
            </div>
            <div class="result-item">
              <div class="result-value">{{ overviewData.energy_market.total_output || 0 }}</div>
              <div class="result-label">成交总出力(100MW)</div>
            </div>
          </div>
          <!-- 第三行：其他指标 -->
          <div class="result-row row-3">
            <div class="result-item">
              <div class="result-value">{{ overviewData.energy_market.total_capacity || 0 }}</div>
              <div class="result-label">总装机容量(100MW)</div>
            </div>
            <div class="result-item">
              <div class="result-value">{{ overviewData.energy_market.plant_count || 0 }}</div>
              <div class="result-label">发电企业数目</div>
            </div>
            <div class="result-item">
              <div class="result-value">{{ overviewData.energy_market.quote_unit_count || 0 }}</div>
              <div class="result-label">申报机组数目</div>
            </div>
            <div class="result-item">
              <div class="result-value">{{ overviewData.energy_market.bid_units || 0 }}</div>
              <div class="result-label">中标机组数目</div>
            </div>
            <div class="result-item">
              <div class="result-value">{{ overviewData.energy_market.total_revenue || 0 }}</div>
              <div class="result-label">总交易额(万元)</div>
            </div>
          </div>
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
        <h3 class="card-title">电力电量平衡结果</h3>
        <div class="svg-chart-wrap" style="height: 260px;">
          <svg viewBox="0 0 700 260" class="svg-chart">
            <line x1="50" y1="10" x2="50" y2="230" stroke="#e0e0e0" stroke-width="1"/>
            <line x1="50" y1="230" x2="690" y2="230" stroke="#e0e0e0" stroke-width="1"/>
            <text x="50" y="10" font-size="10" fill="#666" text-anchor="middle">功率(MW)</text>
            <text v-for="(v, i) in balanceYLabels" :key="i" :x="46" :y="230 - (i/3)*210 + 4" text-anchor="end" font-size="10" fill="#999">{{ v }}</text>
            <polygon :points="balanceAreaPoints" fill="rgba(255,72,72,0.8)" stroke="none"/>
            <polygon :points="windAreaPoints" fill="rgba(76,175,80,0.8)" stroke="none"/>
            <polygon :points="solarAreaPoints" fill="rgba(255,215,0.8)" stroke="none"/>
            <polygon :points="hydroAreaPoints" fill="rgba(24,144,255,0.8)" stroke="none"/>
            <polyline :points="loadLinePoints" fill="none" stroke="#333" stroke-width="2"/>
            
            <!-- X轴刻度和标签（适配96时段） -->
            <template v-for="i in maxPeriods" :key="'x-balance-'+i">
              <text v-if="i % 8 === 0" :x="50 + (i - 0.5) * 6.67" y="250" text-anchor="middle" font-size="9" fill="#666">{{ i }}</text>
              <line :x1="50 + i * 6.67" :y1="230" :x2="50 + i * 6.67" :y2="235" stroke="#e0e0e0" stroke-width="1"/>
            </template>
          </svg>
        </div>
        <div class="legend-row">
          <span class="legend-item"><span class="legend-color" style="background:rgba(255,72,72,0.8)"></span>火电功率</span>
          <span class="legend-item"><span class="legend-color" style="background:rgba(76,175,80,0.8)"></span>风电功率</span>
          <span class="legend-item"><span class="legend-color" style="background:rgba(255,215,0.8)"></span>光伏功率</span>
          <span class="legend-item"><span class="legend-color" style="background:rgba(24,144,255,0.8)"></span>水电功率</span>
          <span class="legend-item"><span class="legend-color" style="background:#333"></span>总负荷功率</span>
        </div>
      </div>

      <!-- 出清电价图表 -->
      <div class="card" style="margin-top: 20px;">
        <h3 class="card-title">电能量市场出清电价</h3>
        <div class="svg-chart-wrap">
          <svg viewBox="0 0 700 220" class="svg-chart">
            <line x1="50" y1="10" x2="50" y2="200" stroke="#e0e0e0" stroke-width="1"/>
            <line x1="50" y1="200" x2="690" y2="200" stroke="#e0e0e0" stroke-width="1"/>
            <text x="50" y="10" font-size="10" fill="#666" text-anchor="middle">电价(元/MWh)</text>
            <text v-for="(v, i) in [0, 100, 200, 300]" :key="i" :x="45" :y="200 - i * 60 + 4" text-anchor="end" font-size="11" fill="#999">{{ v }}</text>
            <polyline :points="clearingChartPoints" fill="none" stroke="#1890ff" stroke-width="2"/>
            
            <!-- X轴刻度和标签（适配96时段） -->
            <template v-for="i in maxPeriods" :key="'x-clearing-'+i">
              <text v-if="i % 8 === 0" :x="50 + (i - 0.5) * 6.67" y="218" text-anchor="middle" font-size="9" fill="#666">{{ i }}</text>
              <line :x1="50 + i * 6.67" :y1="200" :x2="50 + i * 6.67" :y2="205" stroke="#e0e0e0" stroke-width="1"/>
            </template>
          </svg>
        </div>
      </div>
    </div>

    <!-- 详情分析 -->
    <div v-if="settlementTab === 'analysis'">
      <div class="card">
        <!-- 标题随日期变化 -->
        <h3 class="card-title">{{ currentDayLabel }} 公司中标结果</h3>
        <!-- G13企业中标结果 -->
        <div v-if="g13SettlementData" class="g13-settlement-results">
          <div class="result-row row-4">
            <div class="result-item">
              <div class="result-label">火电厂名称</div>
              <div class="result-value">{{ g13SettlementData.name || 'G13' }}</div>
            </div>
            <div class="result-item">
              <div class="result-label">运行成本(万元)</div>
              <div class="result-value">{{ g13SettlementData.opCost || 0 }}</div>
            </div>
            <div class="result-item">
              <div class="result-label">开机成本(万元)</div>
              <div class="result-value">{{ g13SettlementData.startCost || 0 }}</div>
            </div>
            <div class="result-item">
              <div class="result-label">关机成本(万元)</div>
              <div class="result-value">{{ g13SettlementData.stopCost || 0 }}</div>
            </div>
          </div>
          <div class="result-row row-4">
            <div class="result-item">
              <div class="result-label">总中标出力(MW)</div>
              <div class="result-value">{{ g13SettlementData.output || 0 }}</div>
            </div>
            <div class="result-item">
              <div class="result-label">中标电量均价(元/MWh)</div>
              <div class="result-value">{{ g13SettlementData.avgPrice || 0 }}</div>
            </div>
            <div class="result-item">
              <div class="result-label">总中标收益(万元)</div>
              <div class="result-value">{{ g13SettlementData.revenue || 0 }}</div>
            </div>
            <div class="result-item">
              <div class="result-label">净收益(万元)</div>
              <div class="result-value">{{ g13SettlementData.netIncome || 0 }}</div>
            </div>
          </div>
        </div>
        <div v-else class="no-data">
          <p>暂无G13企业的中标结果数据</p>
        </div>
      </div>

      <!-- 自主报价结果 -->
      <div class="card" style="margin-top: 20px; overflow: visible;">
        
        <div><!--
          <h4>{{ currentDayLabel }} 机组中标结果</h4>
          <p class="note">中标出力单位为MW，中标均价单位为元/MWh</p>
          <div class="data-table-wrap">
            <table class="data-table">
              <thead>
                <tr>
                  <th>机组编号</th>
                  <th>类型</th>
                  <th v-for="i in Math.min(historyEnergyDetail[0]?.values?.length || 0, 6)" :key="i">时段{{ i }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in historyEnergyDetail.slice(0, 8)" :key="row.row_index">
                  <td>Thermal_{{ Number(row.row_index) + 1 }}</td>
                  <td>中标出力</td>
                  <td v-for="(v, i) in row.values.slice(0, 6)" :key="i">{{ typeof v === 'number' ? v.toFixed(2) : v }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        -->
          
          
          <!-- 新增：机组中标出力柱状图 -->
          <div class="bar-chart-container" style="margin-top: 20px; overflow: visible;">
            <!-- 标题+下拉选择框 -->
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
              <h5 style="font-size: 13px; color: #333; margin: 0;">各时段机组中标结果</h5>
              <!-- 机组选择下拉框 - 修复disabled绑定 -->
              <select 
                v-model="selectedUnitIndex" 
                style="padding: 4px 8px; border: 1px solid #d9d9d9; border-radius: 4px; font-size: 12px; color: #333;"
                :disabled="!historyEnergyDetail.length"  <!-- 修复：使用v-bind绑定布尔值 -->
              >
                <option 
                  v-for="(row, idx) in historyEnergyDetail.slice(0, 8)" 
                  :key="`unit-option-${idx}`"
                  :value="idx"
                >
                  Thermal_{{ Number(row.row_index) + 1 }}
                </option>
              </select>
            </div>


            <div class="svg-chart-wrap" style="height: 300px; overflow: visible;">
              <svg :viewBox="`0 0 ${Math.max(800, 60 + maxPeriods * 8 + 60)} 300`" class="svg-chart bar-chart" style="width: 100%; min-width: 800px;">
                <!-- 坐标轴 -->
                <line x1="60" y1="20" x2="60" y2="270" stroke="#e0e0e0" stroke-width="1"/>
                <line x1="60" y1="270" :x2="60 + maxPeriods * 8 + 20" y2="270" stroke="#e0e0e0" stroke-width="1"/>
                <!-- 右侧Y轴 - 中标均价 -->
                <line :x1="60 + maxPeriods * 8 + 20" y1="20" :x2="60 + maxPeriods * 8 + 20" y2="270" stroke="#e0e0e0" stroke-width="1"/>
                
                <!-- Y轴刻度和标签 -->
                <!-- 出力(MW) 标签放在坐标轴上方 -->
                <text x="60" y="10" font-size="10" fill="#666" text-anchor="middle">出力(MW)</text>
                <template v-for="(v, i) in barYLabels" :key="'y-'+i">
                  <text :x="55" :y="270 - (i / (barYLabels.length - 1)) * 240 + 4" text-anchor="end" font-size="10" fill="#999">{{ v }}</text>
                  <line :x1="58" :y1="270 - (i / (barYLabels.length - 1)) * 240" :x2="60 + maxPeriods * 8 + 20" :y2="270 - (i / (barYLabels.length - 1)) * 240" stroke="#f0f0f0" stroke-width="1"/>
                </template>
                
                <!-- 右侧Y轴 - 中标均价刻度和标签 -->
                <!-- 中标均价(元/MWh) 标签放在坐标轴上方 -->
                <text :x="60 + maxPeriods * 8 + 20" y="10" font-size="10" fill="#666" text-anchor="middle">中标均价(元/MWh)</text>
                <template v-for="(v, i) in priceYLabels" :key="'y-price-'+i">
                  <text :x="60 + maxPeriods * 8 + 25" :y="270 - (i / (priceYLabels.length - 1)) * 240 + 4" text-anchor="start" font-size="10" fill="#999">{{ v }}</text>
                </template>
                
                <!-- X轴刻度和标签（适配96时段） -->
                <template v-for="i in maxPeriods" :key="'x-'+i">
                  <text v-if="i % 8 === 0" :x="60 + (i - 0.5) * 8" y="285" text-anchor="middle" font-size="9" fill="#666">{{ i }}</text>
                  <line :x1="60 + i * 8" :y1="270" :x2="60 + i * 8" :y2="275" stroke="#e0e0e0" stroke-width="1"/>
                </template>
                
                <!-- 选中机组的柱状图 -->
                <template v-if="selectedUnitData">
                  <rect 
                    v-for="(value, periodIdx) in selectedUnitData.values" 
                    :key="'bar-'+selectedUnitIndex+'-'+periodIdx"
                    :x="60 + periodIdx * 8 + 1"
                    :y="getBarY(value)" 
                    width="6"
                    :height="getBarHeight(value)" 
                    fill="#1890ff"
                    opacity="0.8"
                  >
                    <title>
                      机组{{ Number(selectedUnitData.row_index) + 1 }} 时段{{ Number(periodIdx) + 1 }}: 
                      {{ typeof value === 'number' ? value.toFixed(2) : '0.00' }} MW
                    </title>
                  </rect>
                </template>
                
                <!-- 中标均价曲线 -->
                <polyline 
                  v-if="priceLinePath" 
                  :points="priceLinePath" 
                  fill="none" 
                  stroke="#faad14" 
                  stroke-width="2"
                >
                  <title>中标均价(元/MWh)</title>
                </polyline>
                
                <!-- 图例（居中显示：中标出力、中标均价） -->
                <g :transform="`translate(${60 + (maxPeriods * 8) / 2 - 100}, 10)`">
                  <template v-if="selectedUnitData">
                    <!-- 中标出力图例 -->
                    <rect 
                      x="0" y="0" width="12" height="8" 
                      fill="#1890ff" opacity="0.8"
                    />
                    <text x="16" y="8" font-size="10" fill="#666">中标出力</text>
                    
                    <!-- 中标均价图例 -->
                    <line x1="80" y1="4" x2="100" y2="4" stroke="#faad14" stroke-width="2"/>
                    <text x="105" y="8" font-size="10" fill="#666">中标均价</text>
                  </template>
                </g>
              </svg>
            </div>
          </div>
          
          <!-- 新增：中标收益柱状图 -->
          <div class="bar-chart-container" style="margin-top: 30px;">
            <!-- 标题 -->
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
              <h5 style="font-size: 13px; color: #333; margin: 0;">各时段机组中标收益</h5>
            </div>

            <div class="svg-chart-wrap" style="height: 300px; overflow: visible;">
              <svg :viewBox="`0 0 ${Math.max(800, 60 + maxPeriods * 8 + 60)} 300`" class="svg-chart bar-chart" style="width: 100%; min-width: 800px;">
                <!-- 坐标轴 -->
                <line x1="60" y1="20" x2="60" y2="270" stroke="#e0e0e0" stroke-width="1"/>
                <line x1="60" y1="270" :x2="60 + maxPeriods * 8 + 20" y2="270" stroke="#e0e0e0" stroke-width="1"/>
                
                <!-- Y轴刻度和标签 -->
                <!-- 中标收益(元) 标签放在坐标轴上方 -->
                <text x="60" y="10" font-size="10" fill="#666" text-anchor="middle">中标收益(元)</text>
                <template v-for="(v, i) in revenueYLabels" :key="'y-revenue-'+i">
                  <text :x="55" :y="270 - (i / (revenueYLabels.length - 1)) * 240 + 4" text-anchor="end" font-size="10" fill="#999">{{ v }}</text>
                  <line :x1="58" :y1="270 - (i / (revenueYLabels.length - 1)) * 240" :x2="60 + maxPeriods * 8 + 20" :y2="270 - (i / (revenueYLabels.length - 1)) * 240" stroke="#f0f0f0" stroke-width="1"/>
                </template>
                
                <!-- X轴刻度和标签（适配96时段） -->
                <template v-for="i in maxPeriods" :key="'x-revenue-'+i">
                  <text v-if="i % 8 === 0" :x="60 + (i - 0.5) * 8" y="285" text-anchor="middle" font-size="9" fill="#666">{{ i }}</text>
                  <line :x1="60 + i * 8" :y1="270" :x2="60 + i * 8" :y2="275" stroke="#e0e0e0" stroke-width="1"/>
                </template>
                
                <!-- 中标收益柱状图 -->
                <template v-if="revenueData.length > 0">
                  <rect 
                    v-for="(value, periodIdx) in revenueData" 
                    :key="'revenue-bar-'+periodIdx"
                    :x="60 + periodIdx * 8 + 1"
                    :y="getRevenueY(value)" 
                    width="6"
                    :height="getRevenueBarHeight(value)" 
                    fill="#52c41a"
                    opacity="0.8"
                  >
                    <title>
                      时段{{ Number(periodIdx) + 1 }}: {{ typeof value === 'number' ? value.toFixed(2) : '0.00' }} 元
                    </title>
                  </rect>
                </template>
                
                <!-- 图例（居中显示：中标收益） -->
                <g :transform="`translate(${60 + (maxPeriods * 8) / 2 - 40}, 10)`">
                  <template v-if="selectedUnitData">
                    <rect 
                      x="0" y="0" width="12" height="8" 
                      fill="#52c41a" opacity="0.8"
                    />
                    <text x="16" y="8" font-size="10" fill="#666">中标收益</text>
                  </template>
                </g>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { marketApi } from "../api/market";

// 定义类型接口 - 解决any类型问题
interface HistoryEnergyItem {
  row_index: number | string;
  values: (number | string)[];
}

interface DateTab {
  key: number;
  label: string;
}

interface BalanceChartData {
  thermal: number[];
  wind: number[];
  solar: number[];
  hydro: number[];
  load: number[];
  periods: number;
}

// 柱状图颜色配置
const barColors = [
  "#1890ff", "#722ed1", "#f5222d", "#fa8c16", 
  "#52c41a", "#13c2c2", "#eb2f96", "#fadb14"
];

// 选中机组索引（响应式）
const selectedUnitIndex = ref<number>(0);

// 最大时段数（基于选中机组）
const maxPeriods = computed<number>(() => {
  return selectedUnitData.value?.values?.length || 96;
});

// 最大出力值（基于选中机组）
const maxOutput = computed<number>(() => {
  if (!selectedUnitData.value) return 1;
  let max = 1;
  selectedUnitData.value.values.forEach((v: any) => {
    const numVal = Number(v);
    if (!isNaN(numVal) && numVal > max) max = numVal;
  });
  return max;
});

// Y轴刻度标签
const barYLabels = computed<number[]>(() => {
  const max = maxOutput.value;
  return [0, Math.round(max / 4), Math.round(max / 2), Math.round(max * 3 / 4), Math.round(max)];
});

// 获取选中机组数据
const selectedUnitData = computed((): HistoryEnergyItem | null => {
  if (historyEnergyDetail.value.length === 0) return null;
  return historyEnergyDetail.value.slice(0, 8)[selectedUnitIndex.value] || null;
});

// 获取柱状图Y坐标
const getBarY = (value: any): number => {
  const val = Number(value) || 0;
  const maxVal = Number(maxOutput.value) || 1;
  // 最小高度1px，避免完全不可见
  return 270 - Math.max((val / maxVal) * 240, 1);
};

// 获取柱状图高度
const getBarHeight = (value: any): number => {
  const val = Number(value) || 0;
  const maxVal = Number(maxOutput.value) || 1;
  // 最小高度1px
  return Math.max((val / maxVal) * 240, 1);
};

// 中标均价（电能量市场出清电价）相关计算
const maxPrice = computed<number>(() => {
  if (!energyPriceData.value.length) return 1000;
  let max = 1000;
  energyPriceData.value.forEach((v: any) => {
    const numVal = Number(v);
    if (!isNaN(numVal) && numVal > max) max = numVal;
  });
  return Math.ceil(max / 100) * 100;
});

// 中标均价Y轴刻度标签
const priceYLabels = computed<number[]>(() => {
  const max = maxPrice.value;
  return [0, Math.round(max / 4), Math.round(max / 2), Math.round(max * 3 / 4), max];
});

// 获取中标均价Y坐标
const getPriceY = (value: any): number => {
  const val = Number(value) || 0;
  const maxVal = Number(maxPrice.value) || 1000;
  // 最小高度1px
  return 270 - Math.max((val / maxVal) * 240, 1);
};

// 中标均价曲线路径
const priceLinePath = computed<string>(() => {
  if (!energyPriceData.value.length) return "";
  const points = energyPriceData.value.map((value, idx) => {
    const x = 60 + idx * 8 + 3; // 居中在柱子上
    const y = getPriceY(value);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });
  return points.join(" ");
});

// 中标收益相关计算
const revenueData = computed<number[]>(() => {
  const output = selectedUnitData.value;
  const prices = energyPriceData.value;
  if (!output || !output.values || !prices.length) return [];
  return output.values.map((v: any, i: number) => {
    const outputVal = Number(v) || 0;
    const priceVal = Number(prices[i]) || 0;
    return outputVal * priceVal;
  });
});

const maxRevenue = computed<number>(() => {
  // 固定最大值为2000
  return 2000;
});

// 中标收益Y轴刻度标签
const revenueYLabels = computed<number[]>(() => {
  const max = maxRevenue.value;
  return [0, Math.round(max / 4), Math.round(max / 2), Math.round(max * 3 / 4), max];
});

// 获取中标收益Y坐标
const getRevenueY = (value: number): number => {
  const val = Number(value) || 0;
  const maxVal = Number(maxRevenue.value) || 100000;
  // 最小高度1px
  return 270 - Math.max((val / maxVal) * 240, 1);
};

// 获取中标收益柱状图高度
const getRevenueBarHeight = (value: number): number => {
  const val = Number(value) || 0;
  const maxVal = Number(maxRevenue.value) || 100000;
  // 最小高度1px
  return Math.max((val / maxVal) * 240, 1);
};

// 日期标签配置
const dateTabs: DateTab[] = [
  { key: 1, label: "第一天" },
  { key: 2, label: "第二天" },
  { key: 3, label: "第三天" },
  { key: 4, label: "第四天" },
  { key: 5, label: "第五天" },
  { key: 6, label: "第六天" },
  { key: 7, label: "第七天" }
];

// 核心状态
const settlementTab = ref<string>("overview");
const currentDay = ref<number>(1);
const overviewData = ref<any>({ energy_market: {} });
const settlementRows = ref<any[]>([]);
const g13SettlementData = ref<any>(null);
const historyEnergyDetail = ref<HistoryEnergyItem[]>([]); // 修复：指定具体类型
const balanceChart = ref<BalanceChartData>({ thermal: [], wind: [], solar: [], hydro: [], load: [], periods: 96 });
const energyPriceData = ref<number[]>([]);

// 当前日期标签文本
const currentDayLabel = computed(() => {
  const dayItem = dateTabs.find(item => item.key === currentDay.value);
  return dayItem?.label || "第一天";
});

// Tab切换处理
const handleTabChange = (tabKey: string) => {
  settlementTab.value = tabKey;
  refreshAllData();
};

// 日期切换处理
const handleDayChange = (dayKey: number) => {
  currentDay.value = dayKey;
  refreshAllData();
};

// 数据刷新统一入口
const refreshAllData = () => {
  console.log(`刷新数据：${currentDayLabel.value} - ${settlementTab.value === 'overview' ? '市场总览' : '详情分析'}`);
  fetchSettlementData();
  fetchHistoryDetail();
  fetchBalanceChart();
  fetchEnergyPriceChart();
};

// 获取结算数据
async function fetchSettlementData() {
  try {
    const [ov, dt] = await Promise.all([
      marketApi.getSettlementOverview(),
      marketApi.getSettlementDetail(),
    ]);
    overviewData.value = ov.data;
    settlementRows.value = dt.data.energy_rows || [];
    g13SettlementData.value = settlementRows.value.find((row: any) => row.name === "G13") || null;
  } catch (e) { 
    console.error("获取结算数据失败", e); 
  }
}

// 获取历史详情数据（添加兜底测试数据）
async function fetchHistoryDetail() {
  try {
    const res = await marketApi.getOutResults({ sheet: "thermal_tg_opera_power" });
    const rawItems = res.data?.items || [];
    // 过滤有效数据 - 修复：指定item类型
    historyEnergyDetail.value = rawItems.filter((item: HistoryEnergyItem) => 
      Array.isArray(item?.values) && item.values.length > 0
    );
    // 兜底：无数据时生成测试数据（8个机组，96时段）
    if (historyEnergyDetail.value.length === 0) {
      historyEnergyDetail.value = Array.from({ length: 8 }, (_, idx) => ({
        row_index: idx,
        values: Array.from({ length: 96 }, () => Math.floor(Math.random() * 200) + 50)
      }));
    }
  } catch (e) { 
    console.error("获取历史详情失败", e);
    // 报错时生成测试数据
    historyEnergyDetail.value = Array.from({ length: 8 }, (_, idx) => ({
      row_index: idx,
      values: Array.from({ length: 96 }, () => Math.floor(Math.random() * 200) + 50)
    }));
  }
}

// 获取平衡图表数据
async function fetchBalanceChart() {
  try {
    const { data } = await marketApi.getBalanceChart();
    balanceChart.value = data;
  } catch (e) { 
    console.error("获取平衡图表失败", e); 
  }
}

// 获取出清电价数据
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
const pieColors = ["rgba(76,175,80,0.8)", "rgba(255,215,0.8)", "rgba(24,144,255,0.8)", "rgba(255,72,72,0.8)", "rgba(114,46,209,0.8)"];
const pieTypes = ["风电", "光伏", "水电", "火电", "电化学储能", "抽蓄电站"];

// 机组数量分布数据
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

// 装机容量分布数据
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

// 生成饼状图路径
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

// 机组数量饼图
const countArcs = computed(() => pieArcs(countPieData.value));
// 装机容量饼图
const capacityArcs = computed(() => pieArcs(capacityPieData.value));

// 平衡图表最大Y值
const balanceMaxY = computed(() => {
  const all = [
    ...balanceChart.value.thermal,
    ...balanceChart.value.load,
    ...(balanceChart.value.thermal.map((v: number, i: number) => v + (balanceChart.value.wind[i] || 0) + (balanceChart.value.solar[i] || 0) + (balanceChart.value.hydro[i] || 0))),
  ];
  return Math.max(...all, 1);
});

// 平衡图表Y坐标转换
const toBalanceY = (v: number) => {
  const max = balanceMaxY.value;
  return 230 - (v / max) * 210;
};

// 火电区域坐标
const balanceAreaPoints = computed(() => {
  const data = balanceChart.value.thermal;
  if (!data.length) return "";
  const n = data.length;
  const step = 640 / (n - 1);
  const top = data.map((v: number, i: number) => `${(50 + i * step).toFixed(1)},${toBalanceY(v).toFixed(1)}`);
  const bottom = `${(50 + (n - 1) * step).toFixed(1)},${toBalanceY(0)} 50,${toBalanceY(0)}`;
  return top.join(" ") + " " + bottom;
});

// 风电区域坐标
const windAreaPoints = computed(() => {
  const thermal = balanceChart.value.thermal;
  const wind = balanceChart.value.wind;
  if (!thermal.length || !wind.length) return "";
  const n = thermal.length;
  const step = 640 / (n - 1);
  const top = wind.map((_: number, i: number) => `${(50 + i * step).toFixed(1)},${toBalanceY(thermal[i] + wind[i]).toFixed(1)}`);
  const bottom = thermal.map((v: number, i: number) => `${(50 + i * step).toFixed(1)},${toBalanceY(v).toFixed(1)}`).reverse();
  return top.join(" ") + " " + bottom.join(" ");
});

// 光伏区域坐标
const solarAreaPoints = computed(() => {
  const thermal = balanceChart.value.thermal;
  const wind = balanceChart.value.wind;
  const solar = balanceChart.value.solar;
  if (!thermal.length || !wind.length || !solar.length) return "";
  const n = thermal.length;
  const step = 640 / (n - 1);
  const top = solar.map((_: number, i: number) => `${(50 + i * step).toFixed(1)},${toBalanceY(thermal[i] + wind[i] + solar[i]).toFixed(1)}`);
  const bottom = wind.map((_: number, i: number) => `${(50 + i * step).toFixed(1)},${toBalanceY(thermal[i] + wind[i]).toFixed(1)}`).reverse();
  return top.join(" ") + " " + bottom.join(" ");
});

// 水电区域坐标
const hydroAreaPoints = computed(() => {
  const thermal = balanceChart.value.thermal;
  const wind = balanceChart.value.wind;
  const solar = balanceChart.value.solar;
  const hydro = balanceChart.value.hydro;
  if (!thermal.length || !wind.length || !solar.length || !hydro.length) return "";
  const n = thermal.length;
  const step = 640 / (n - 1);
  const top = hydro.map((_: number, i: number) => `${(50 + i * step).toFixed(1)},${toBalanceY(thermal[i] + wind[i] + solar[i] + hydro[i]).toFixed(1)}`);
  const bottom = solar.map((_: number, i: number) => `${(50 + i * step).toFixed(1)},${toBalanceY(thermal[i] + wind[i] + solar[i]).toFixed(1)}`).reverse();
  return top.join(" ") + " " + bottom.join(" ");
});

// 负荷线坐标
const loadLinePoints = computed(() => {
  const data = balanceChart.value.load;
  if (!data.length) return "";
  const n = data.length;
  const step = 640 / (n - 1);
  return data.map((v: number, i: number) => `${(50 + i * step).toFixed(1)},${toBalanceY(v).toFixed(1)}`).join(" ");
});

// 平衡图表Y轴标签
const balanceYLabels = computed(() => {
  const max = balanceMaxY.value;
  return [0, Math.round(max / 3), Math.round(max * 2 / 3), Math.round(max)];
});

// 出清电价图表坐标
const clearingChartPoints = computed(() => {
  const vals = energyPriceData.value;
  if (!vals.length) return "";
  const maxVal = Math.max(...vals, 1);
  const step = 640 / Math.max(vals.length - 1, 1);
  return vals.map((v, i) => `${(50 + i * step).toFixed(1)},${(200 - (v / maxVal) * 180).toFixed(1)}`).join(" ");
});

// 初始化数据
onMounted(() => {
  fetchSettlementData();
  fetchHistoryDetail();
  fetchBalanceChart();
  fetchEnergyPriceChart();
});
</script>

<style scoped>
.content-section {
  max-width: 1300px;
  margin: 0 auto;
  padding: 16px;
}

/* 顶部操作栏 */
.top-operation-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.tab-bar {
  display: flex;
  gap: 0;
  height: 36px;
}

.tab-btn {
  padding: 8px 20px;
  border: 1px solid #d9d9d9;
  background: #fff;
  cursor: pointer;
  font-size: 14px;
  color: #333;
  transition: all 0.2s;
  height: 100%;
  box-sizing: border-box;
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

/* 日期标签栏 */
.date-tab-bar {
  display: flex;
  gap: 0;
  height: 36px;
}

.date-tab-btn {
  padding: 8px 16px;
  border: 1px solid #d9d9d9;
  border-radius: 0;
  background: #fff;
  cursor: pointer;
  font-size: 12px;
  color: #333;
  transition: all 0.2s;
  height: 100%;
  box-sizing: border-box;
}

.date-tab-btn + .date-tab-btn {
  border-left: none;
}

.date-tab-btn.active {
  background: #1890ff;
  color: #fff;
  border-color: #1890ff;
}

/* 卡片样式 */
.card {
  background: #fff;
  border-radius: 8px;
  padding: 20px 24px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  margin-bottom: 20px;
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

/* 结果行样式 */
.result-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 16px;
  padding: 16px;
  border-radius: 8px;
}

.result-row.row-1 {
  background: #f0f8ff;
  border: 1px solid #e6f7ff;
}

.result-row.row-2 {
  background: #f6ffed;
  border: 1px solid #d9f7be;
}

.result-row.row-3 {
  background: #fffbe6;
  border: 1px solid #ffe58f;
}

.result-row.row-4 {
  background: #f0f8ff;
  border: 1px solid #e6f7ff;
}

.result-item {
  flex: 1;
  min-width: 140px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 6px;
  text-align: center;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.result-value {
  font-size: 18px;
  font-weight: 600;
  color: #1890ff;
  margin-bottom: 8px;
}

.result-label {
  font-size: 12px;
  color: #666;
  line-height: 1.4;
}

/* 饼状图样式 */
.pie-chart-row {
  display: flex;
  gap: 40px;
  justify-content: center;
  margin: 16px 0;
  flex-wrap: wrap;
}

.pie-chart-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 200px;
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

/* 图例样式 */
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

/* 图表容器 */
.svg-chart-wrap {
  width: 100%;
  height: 220px;
  position: relative;
  overflow: auto;
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

/* 表格样式 */
.data-table-wrap {
  overflow-x: auto;
  margin: 16px 0;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  min-width: 600px;
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
  border-bottom: 1px solid #f0f8ff;
  color: #555;
  white-space: nowrap;
}

/* 无数据样式 */
.no-data {
  padding: 40px 0;
  text-align: center;
  color: #999;
  font-size: 14px;
}

/* 柱状图样式 */
.bar-chart-container {
  margin-top: 20px;
}

.bar-chart {
  min-width: 4000px;
  height: 100%;
}

.note {
  font-size: 12px;
  color: #999;
  margin: 0 0 8px;
}

/* 适配96时段柱状图容器 */
.bar-chart-container .svg-chart-wrap {
  height: 300px !important;
}
</style>