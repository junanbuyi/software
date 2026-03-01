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
              :class="['nav-item', { active: activeNav === item.key }]"
              @click="activeNav = item.key">
            <span class="nav-icon">{{ item.icon }}</span>
            <span>{{ item.label }}</span>
          </li>
        </ul>
      </aside>

      <!-- 右侧内容区 -->
      <main class="market-content">

        <!-- ========== 企业信息 ========== -->
        <div v-if="activeNav === 'company'" class="content-section">
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

        <!-- ========== 成交历史 ========== -->
        <div v-if="activeNav === 'history'" class="content-section">
          <div class="tab-bar">
            <button :class="['tab-btn', { active: historyTab === 'overview' }]" @click="historyTab = 'overview'">历史总览</button>
            <button :class="['tab-btn', { active: historyTab === 'detail' }]" @click="historyTab = 'detail'">历史详情</button>
          </div>
          <!-- 历史总览 -->
          <div v-if="historyTab === 'overview'" class="card">
            <div class="data-table-wrap">
              <table class="data-table">
                <thead><tr><th>名称</th><th v-for="i in Math.min(clearingHistory[0]?.values?.length || 0, 10)" :key="i">时段{{ i }}</th></tr></thead>
                <tbody>
                  <tr v-for="h in clearingHistory" :key="h.metric_name">
                    <td>{{ h.metric_name }}</td>
                    <td v-for="(v, i) in h.values.slice(0, 10)" :key="i">{{ typeof v === 'number' ? v.toFixed(4) : v }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <!-- 历史详情 -->
          <div v-if="historyTab === 'detail'" class="card">
            <div>
              <h4>现货市场申报</h4>
              <p class="note">报价单位为元/MWh，报量单位MW，报价和报量下数字表示第几段报价</p>
              <div class="data-table-wrap">
                <table class="data-table">
                  <thead><tr><th>编号</th><th>机组编号</th><th>报价</th><th>报量</th></tr></thead>
                  <tbody>
                    <tr v-for="(b, i) in selfBidRows" :key="i">
                      <td>{{ b.no }}</td><td>{{ b.unit }}</td><td>{{ b.price }}</td><td>{{ b.quantity }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <h3 class="card-title" style="margin-top: 24px;">电能量市场中标结果</h3>
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

        <!-- ========== 信息披露 ========== -->
        <div v-if="activeNav === 'disclosure'" class="content-section">
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
                <polyline :points="disclosureChartPoints" fill="none" stroke="#1890ff" stroke-width="2"/>
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

        <!-- ========== 市场交易 ========== -->
        <div v-if="activeNav === 'trading'" class="content-section">
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

        <!-- ========== 结算报告 ========== -->
        <div v-if="activeNav === 'settlement'" class="content-section">
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
                  <!-- 火电功率区域 (主体) -->
                  <polygon :points="balanceAreaPoints" fill="rgba(255,180,140,0.6)" stroke="none"/>
                  <!-- 风电功率区域 (顶部) -->
                  <polygon :points="windAreaPoints" fill="rgba(76,175,80,0.6)" stroke="none"/>
                  <!-- 负荷曲线 -->
                  <polyline :points="loadLinePoints" fill="none" stroke="#333" stroke-width="2"/>
                  <text x="370" y="255" text-anchor="middle" font-size="10" fill="#666">时段/15min</text>
                </svg>
              </div>
              <div class="legend-row">
                <span class="legend-item"><span class="legend-color" style="background:rgba(255,180,140,0.8)"></span>火电功率</span>
                <span class="legend-item"><span class="legend-color" style="background:rgba(76,175,80,0.8)"></span>风电消纳功率</span>
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
                <h4>现货市场申报</h4>
                <p class="note">报价单位为元/MWh，报量单位MW，报价和报量下数字表示第几段报价</p>
                <div class="data-table-wrap">
                  <table class="data-table">
                    <thead><tr><th>编号</th><th>机组编号</th><th>报价</th><th>报量</th></tr></thead>
                    <tbody>
                      <tr v-for="(b, i) in selfBidRows" :key="i">
                        <td>{{ b.no }}</td><td>{{ b.unit }}</td><td>{{ b.price }}</td><td>{{ b.quantity }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

              </div>
            </div>
          </div>
        </div>

      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { marketApi } from "../api/market";

const router = useRouter();
const goBack = () => router.push("/home");

const activeNav = ref("company");
const navItems = [
  { key: "company", label: "企业信息", icon: "\u2261" },
  { key: "history", label: "成交历史", icon: "\u2615" },
  { key: "disclosure", label: "信息披露", icon: "\ud83d\udcca" },
  { key: "trading", label: "市场交易", icon: "\u2699" },
  { key: "settlement", label: "结算报告", icon: "\ud83d\udcb0" },
];

// ---- 企业信息 ----
const companies = ref<any[]>([]);
const selectedCompany = ref<any>(null);

async function fetchCompanies() {
  try {
    const { data } = await marketApi.getCompanies();
    companies.value = data.items || [];
  } catch (e) { console.error("获取企业信息失败", e); }
}

// ---- 成交历史 ----
const historyTab = ref("overview");
const clearingHistory = ref<any[]>([]);
const historyEnergyDetail = ref<any[]>([]);

async function fetchClearingHistory() {
  try {
    const { data } = await marketApi.getClearingHistory({ start: 0, limit: 96 });
    clearingHistory.value = data.items || [];
  } catch (e) { console.error("获取成交历史失败", e); }
}

async function fetchHistoryDetail() {
  try {
    const res = await marketApi.getOutResults({ sheet: "thermal_tg_opera_power" });
    historyEnergyDetail.value = res.data.items || [];
  } catch (e) { console.error("获取历史详情失败", e); }
}

// ---- 信息披露 ----
const disclosureTabs = [
  { key: "price", label: "电价预测" },
  { key: "load", label: "负荷预测" },
  { key: "wind", label: "风电功率预测" },
  { key: "solar", label: "光伏功率预测" },
];
const disclosureTab = ref("price");
const disclosureSheetMap: Record<string, string> = {
  price: "energy_price", load: "load_load_bid_power",
  wind: "wind_wt_opera_power", solar: "solar_pv_opera_power",
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
    const { data } = await marketApi.getOutResults({ sheet, row_index: 0 });
    const items = data.items || [];
    disclosureData.value = items.length > 0 ? items[0].values : [];
  } catch (e) { disclosureData.value = []; }
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
  // 96个时段 = 一天24小时，每15分钟一个时段
  // 显示 0:00, 4:00, 8:00, 12:00, 16:00, 20:00, 24:00 共7个标签
  return ["0:00", "4:00", "8:00", "12:00", "16:00", "20:00", "24:00"];
});

const disclosureYLabels = computed(() => {
  const vals = disclosureData.value;
  if (!vals.length) return [0, 100, 200, 300];
  const maxVal = Math.max(...vals, 1);
  const step = maxVal / 3;
  return [0, Math.round(step), Math.round(step * 2), Math.round(maxVal)];
});

// ---- 市场交易 ----
const tradingSelected = ref<any>(null);
const tradingUnit = ref("Thermal_1");
const tradingMode = ref("bid");
const dayAheadQuotes = ref<any[]>([]);

async function fetchTradingData() {
  try {
    const da = await marketApi.getDayAheadQuotes();
    dayAheadQuotes.value = da.data.items || [];
  } catch (e) { console.error("获取交易数据失败", e); }
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

// ---- 结算报告 ----
const settlementTab = ref("overview");
const settlementSub = ref("self");
const overviewData = ref<any>({ energy_market: {} });
const settlementRows = ref<any[]>([]);

async function fetchSettlementData() {
  try {
    const [ov, dt] = await Promise.all([
      marketApi.getSettlementOverview(),
      marketApi.getSettlementDetail(),
    ]);
    overviewData.value = ov.data;
    settlementRows.value = dt.data.energy_rows || [];
  } catch (e) { console.error("获取结算数据失败", e); }
}

const selfBidRows = computed(() => {
  return dayAheadQuotes.value
    .filter((q: any) => q.unit_id === "Thermal_1")
    .map((q: any) => ({ no: q.quote_id, unit: q.unit_id, price: q.quote_price, quantity: q.quote_quantity }));
});

// ---- 电力电量平衡表单 ----
const balanceChart = ref<any>({ thermal: [], wind: [], solar: [], load: [], periods: 96 });

async function fetchBalanceChart() {
  try {
    const { data } = await marketApi.getBalanceChart();
    balanceChart.value = data;
  } catch (e) { console.error("获取平衡图表失败", e); }
}

const balanceMaxY = computed(() => {
  const all = [
    ...balanceChart.value.thermal,
    ...balanceChart.value.load,
    ...(balanceChart.value.thermal.map((v: number, i: number) => v + (balanceChart.value.wind[i] || 0))),
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

// ---- 饼状图数据 ----
const pieColors = ["#1890ff", "#52c41a", "#13c2c2", "#fa541c", "#722ed1", "#faad14"];
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

// ---- 出清电价图表 ----
const energyPriceData = ref<number[]>([]);

async function fetchEnergyPriceChart() {
  try {
    const { data } = await marketApi.getOutResults({ sheet: "energy_price", row_index: 0 });
    const items = data.items || [];
    energyPriceData.value = items.length > 0 ? items[0].values : [];
  } catch (e) { console.error("获取出清电价失败", e); }
}

const clearingChartPoints = computed(() => {
  const vals = energyPriceData.value;
  if (!vals.length) return "";
  const maxVal = Math.max(...vals, 1);
  const step = 640 / Math.max(vals.length - 1, 1);
  return vals.map((v, i) => `${(50 + i * step).toFixed(1)},${(200 - (v / maxVal) * 180).toFixed(1)}`).join(" ");
});

// ---- 初始化 ----
onMounted(async () => {
  await fetchCompanies();
  fetchClearingHistory();
  fetchHistoryDetail();
  fetchDisclosureData();
  fetchTradingData();
  fetchSettlementData();
  fetchBalanceChart();
  fetchEnergyPriceChart();
});
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

/* ---- 左侧导航 ---- */
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

/* ---- 右侧内容 ---- */
.market-content {
  padding: 20px 24px;
  background: #f5f7fa;
  overflow-y: auto;
}
.content-section {
  max-width: 1100px;
}
.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 16px;
}

/* ---- 卡片 ---- */
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

/* ---- Tab 栏 ---- */
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

/* ---- 简单列表表格 ---- */
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

/* ---- 数据表格 ---- */
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

/* ---- 机组详情网格 ---- */
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

/* ---- 键值列表 ---- */
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
.kv-row.highlight .kv-label {
  color: #ff4d4f;
}
.kv-row.highlight .kv-value {
  color: #ff4d4f;
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

/* ---- 图表 ---- */
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
.note {
  font-size: 12px;
  color: #999;
  margin: 0 0 8px;
}

/* ---- 市场交易网格 ---- */
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

/* ---- 按钮 ---- */
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

/* ---- 子导航 ---- */
.sub-nav {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  border-bottom: 1px solid #e8e8e8;
  padding-bottom: 8px;
}
.sub-nav span {
  font-size: 13px;
  color: #666;
  cursor: pointer;
  padding: 4px 8px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  transition: all 0.2s;
}
.sub-nav span.active {
  color: #1890ff;
  border-color: #1890ff;
  background: #e6f7ff;
}

/* ---- 评分徽章 ---- */
.score-badge {
  font-size: 18px;
  font-weight: 700;
  color: #333;
}

/* ---- 饼状图 ---- */
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

/* ---- 图例 ---- */
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
</style>
