<template>
  <MainLayout>
    <div class="page-header">
      <h1 class="page-title">评分管理</h1>
    </div>

    <section class="panel">
      <div class="panel-header">
        <h3 class="panel-title">模型排名</h3>
      </div>
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th class="filterable" @click="toggleFilter('dataset')">
                <div class="header-content">
                  <span class="filter-text">数据集</span>
                  <div class="filter-dropdown" v-if="activeFilter === 'dataset'">
                    <div class="filter-menu">
                      <div class="filter-options">
                        <label v-for="option in datasetOptions" :key="option">
                          <input 
                            type="checkbox" 
                            :checked="filters.dataset.includes(option)"
                            @click.stop="toggleFilterOption('dataset', option)"
                          />
                          {{ option }}
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              </th>
              <th class="filterable" @click="toggleFilter('type')">
                <div class="header-content">
                  <span class="filter-text">类型</span>
                  <div class="filter-dropdown" v-if="activeFilter === 'type'">
                    <div class="filter-menu">
                      <div class="filter-options">
                        <label v-for="option in typeOptions" :key="option">
                          <input 
                            type="checkbox" 
                            :checked="filters.type.includes(option)"
                            @click.stop="toggleFilterOption('type', option)"
                          />
                          {{ option }}
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              </th>
              <th class="filterable" @click="toggleFilter('model')">
                <div class="header-content">
                  <span class="filter-text">模型名称</span>
                  <div class="filter-dropdown" v-if="activeFilter === 'model'">
                    <div class="filter-menu">
                      <div class="filter-options">
                        <label v-for="option in modelOptions" :key="option">
                          <input 
                            type="checkbox" 
                            :checked="filters.model.includes(option)"
                            @click.stop="toggleFilterOption('model', option)"
                          />
                          {{ option }}
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              </th>
              <th class="filterable" @click="toggleFilter('period')">
                <div class="header-content">
                  <span class="filter-text">预测时间段</span>
                  <div class="filter-dropdown" v-if="activeFilter === 'period'">
                    <div class="filter-menu">
                      <div class="filter-options">
                        <label v-for="option in periodOptions" :key="option">
                          <input 
                            type="checkbox" 
                            :checked="filters.period.includes(option)"
                            @click.stop="toggleFilterOption('period', option)"
                          />
                          {{ option }}
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              </th>
              <th class="filterable" @click="toggleFilter('load')">
                <div class="header-content">
                  <span class="filter-text">负荷</span>
                  <div class="filter-dropdown" v-if="activeFilter === 'load'">
                    <div class="filter-menu">
                      <div class="filter-options">
                        <label v-for="option in loadOptions" :key="option">
                          <input 
                            type="checkbox" 
                            :checked="filters.load.includes(option)"
                            @click.stop="toggleFilterOption('load', option)"
                          />
                          {{ option }}
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              </th>
              <th class="filterable" @click="toggleFilter('wind')">
                <div class="header-content">
                  <span class="filter-text">风速</span>
                  <div class="filter-dropdown" v-if="activeFilter === 'wind'">
                    <div class="filter-menu">
                      <div class="filter-options">
                        <label v-for="option in windOptions" :key="option">
                          <input 
                            type="checkbox" 
                            :checked="filters.wind.includes(option)"
                            @click.stop="toggleFilterOption('wind', option)"
                          />
                          {{ option }}
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              </th>
              <th class="filterable" @click="toggleFilter('weather_type')">
                <div class="header-content">
                  <span class="filter-text">天气</span>
                  <div class="filter-dropdown" v-if="activeFilter === 'weather_type'">
                    <div class="filter-menu">
                      <div class="filter-options">
                        <label v-for="option in weatherOptions" :key="option">
                          <input 
                            type="checkbox" 
                            :checked="filters.weather_type.includes(option)"
                            @click.stop="toggleFilterOption('weather_type', option)"
                          />
                          {{ option }}
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              </th>
              <th>MAE</th>
              <th>RMSE</th>
              <th>R2</th>
              <th>IMAPE</th>
              <th>分数</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredRankings" :key="item.id">
              <td>{{ item.dataset }}</td>
              <td>{{ item.type }}</td>
              <td><a class="link">{{ item.model }}</a></td>
              <td>{{ item.period }}</td>
              <td>{{ item.load }}</td>
              <td>{{ item.wind }}</td>
              <td>{{ item.weather_type }}</td>
              <td>{{ item.mae }}</td>
              <td>{{ item.rmse }}</td>
              <td>{{ item.r2 }}</td>
              <td>{{ item.imape }}</td>
              <td>{{ item.score }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import MainLayout from "../layouts/MainLayout.vue";

const rankings = ref([
  {
    id: 1,
    dataset: "广东电价数据",
    type: "周前确定",
    model: "mamba周前",
    period: "2024.5.1-2024.5.7",
    load: "中负荷",
    wind: "微风",
    weather_type: "多云",
    mae: "20.03",
    rmse: "40.64",
    r2: "0.81",
    imape: "0.08",
    score: "92",
  },
  {
    id: 2,
    dataset: "广东电价数据",
    type: "周前概率",
    model: "tcn周前",
    period: "2024.5.1-2024.5.7",
    load: "中负荷",
    wind: "微风",
    weather_type: "多云",
    mae: "22.15",
    rmse: "43.28",
    r2: "0.78",
    imape: "0.09",
    score: "88",
  },
]);

const activeFilter = ref<string | null>(null);

const filters = ref({
  dataset: [] as string[],
  type: [] as string[],
  model: [] as string[],
  period: [] as string[],
  load: [] as string[],
  wind: [] as string[],
  weather_type: [] as string[],
});

// 获取所有唯一的选项
const datasetOptions = computed(() => [...new Set(rankings.value.map(r => r.dataset))]);
const typeOptions = computed(() => [...new Set(rankings.value.map(r => r.type))]);
const modelOptions = computed(() => [...new Set(rankings.value.map(r => r.model))]);
const periodOptions = computed(() => [...new Set(rankings.value.map(r => r.period))]);
const loadOptions = computed(() => [...new Set(rankings.value.map(r => r.load))]);
const windOptions = computed(() => [...new Set(rankings.value.map(r => r.wind))]);
const weatherOptions = computed(() => [...new Set(rankings.value.map(r => r.weather_type))]);

// 筛选后的数据
const filteredRankings = computed(() => {
  return rankings.value.filter(item => {
    const datasetMatch = filters.value.dataset.length === 0 || filters.value.dataset.includes(item.dataset);
    const typeMatch = filters.value.type.length === 0 || filters.value.type.includes(item.type);
    const modelMatch = filters.value.model.length === 0 || filters.value.model.includes(item.model);
    const periodMatch = filters.value.period.length === 0 || filters.value.period.includes(item.period);
    const loadMatch = filters.value.load.length === 0 || filters.value.load.includes(item.load);
    const windMatch = filters.value.wind.length === 0 || filters.value.wind.includes(item.wind);
    const weatherMatch = filters.value.weather_type.length === 0 || filters.value.weather_type.includes(item.weather_type);

    return datasetMatch && typeMatch && modelMatch && periodMatch && loadMatch && windMatch && weatherMatch;
  });
});

const toggleFilter = (field: string) => {
  activeFilter.value = activeFilter.value === field ? null : field;
};

const toggleFilterOption = (field: string, option: string) => {
  const filterArray = filters.value[field as keyof typeof filters.value];
  const index = filterArray.indexOf(option);
  
  if (index > -1) {
    filterArray.splice(index, 1);
  } else {
    filterArray.push(option);
  }
};
</script>

<style scoped>
.panel-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
}
.panel-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
  margin: 0;
}

.filterable {
  position: relative;
  cursor: pointer;
  user-select: none;
  text-align: center;
}

.filterable:hover {
  background-color: #f5f5f5;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 0;
  position: relative;
}

.filter-text {
  cursor: pointer;
}

.filter-dropdown {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
}

.filter-menu {
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  min-width: 150px;
  margin-top: 4px;
}

.filter-options {
  padding: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.filter-options label {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  cursor: pointer;
  font-size: 13px;
  border-radius: 3px;
  transition: background-color 0.2s;
}

.filter-options label:hover {
  background-color: #f5f5f5;
}

.filter-options input[type="checkbox"] {
  cursor: pointer;
}
</style>
