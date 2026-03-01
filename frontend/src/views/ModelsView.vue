<template>
  <MainLayout>
    <div class="page-header">
      <h1 class="page-title">模型管理</h1>
      <button class="btn primary" @click="showUploadModal = true">上传模型文件</button>
    </div>

    <section class="panel">
      <div class="panel-header">
        <h3 class="panel-title">模型列表</h3>
      </div>
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>模型名称</th>
              <th>描述</th>
              <th>数据集</th>
              <th>类型</th>
              <th>数据集校核状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="model in staticModels" :key="model.id">
              <td>{{ model.name }}</td>
              <td>{{ model.description }}</td>
              <td>{{ model.dataset }}</td>
              <td>{{ model.type }}</td>
              <td>
                <span :class="['status-tag', getStatusClass(model.verify_status)]">
                  {{ model.verify_status || '未校核' }}
                </span>
              </td>
              <td>
                <a class="link" href="#" @click.prevent="openVerifyModal(model)">数据集校核</a>
                <a class="link" href="#">训练模型</a>
                <a class="link" href="#">上传已训练文件</a>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- 上传弹窗 -->
    <div v-if="showUploadModal" class="modal-overlay" @click.self="showUploadModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>上传模型文件</h3>
          <button class="modal-close" @click="showUploadModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>模型名称 <span class="required">*</span></label>
            <input class="input" placeholder="请输入模型名称" />
          </div>
          <div class="form-group">
            <label>描述</label>
            <textarea class="input" rows="2" placeholder="请输入描述"></textarea>
          </div>
          <div class="form-group">
            <label>模型文件 <span class="required">*</span></label>
            <input type="file" accept=".py,.pkl,.h5" />
          </div>
          <div class="form-group">
            <label>选择数据集 <span class="required">*</span></label>
            <select class="input">
              <option value="">请选择数据集</option>
              <option>陕西电价数据</option>
              <option>广东电价数据</option>
            </select>
          </div>
          <div class="form-group">
            <label>预测类型 <span class="required">*</span></label>
            <select class="input">
              <option value="day_ahead">周前确定</option>
              <option value="week_ahead">周前概率</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn" @click="showUploadModal = false">取消</button>
          <button class="btn primary" @click="showUploadModal = false">上传</button>
        </div>
      </div>
    </div>

    <!-- 数据集校核弹窗 -->
    <div v-if="showVerifyModal" class="modal-overlay" @click.self="showVerifyModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>数据集校核 - {{ currentModel?.name }}</h3>
          <button class="modal-close" @click="showVerifyModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>数据集名称 <span class="required">*</span></label>
            <input class="input" v-model="verifyForm.name" placeholder="请输入数据集名称" />
          </div>
          <div class="form-group">
            <label>描述</label>
            <textarea class="input" rows="2" v-model="verifyForm.description" placeholder="请输入描述"></textarea>
          </div>
          <div class="form-group">
            <label>数据集文件 <span class="required">*</span></label>
            <input type="file" accept=".xlsx,.xls,.csv" @change="handleVerifyFileSelect" />
            <p class="form-hint">支持 Excel (.xlsx, .xls) 或 CSV (.csv) 格式</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn" @click="showVerifyModal = false">取消</button>
          <button class="btn primary" :disabled="verifying" @click="handleUploadAndVerify">
            {{ verifying ? '处理中...' : '上传并校核' }}
          </button>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import MainLayout from "../layouts/MainLayout.vue";
import { uploadDataset, verifyDataset } from "../api/datasets";

type ModelItem = {
  id: number;
  name: string;
  description: string;
  dataset: string;
  type: string;
  verify_status?: string;
};

const showUploadModal = ref(false);
const showVerifyModal = ref(false);
const verifying = ref(false);
const currentModel = ref<ModelItem | null>(null);

const verifyForm = reactive({
  name: "",
  description: "",
  file: null as File | null,
});

const staticModels = ref<ModelItem[]>([
  {
    id: 1,
    name: "LSTM周前确定",
    description: "LSTM周前确定",
    dataset: "陕西电价数据",
    type: "周前确定",
    verify_status: "未校核",
  },
  {
    id: 2,
    name: "TCN周前概率",
    description: "TCN周前概率",
    dataset: "广东电价数据",
    type: "周前概率",
    verify_status: "未校核",
  },
]);

const openVerifyModal = (model: ModelItem) => {
  currentModel.value = model;
  verifyForm.name = model.dataset || "";
  verifyForm.description = "";
  verifyForm.file = null;
  showVerifyModal.value = true;
};

const handleVerifyFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    verifyForm.file = target.files[0];
  }
};

const handleUploadAndVerify = async () => {
  if (!verifyForm.name || !verifyForm.file) {
    alert("请填写数据集名称并选择文件");
    return;
  }
  
  verifying.value = true;
  try {
    // 1. 上传数据集
    const formData = new FormData();
    formData.append("name", verifyForm.name);
    formData.append("file", verifyForm.file);
    if (verifyForm.description) {
      formData.append("description", verifyForm.description);
    }
    const uploadedDataset = await uploadDataset(formData);
    
    // 2. 校核数据集
    const verifiedDataset = await verifyDataset(uploadedDataset.id);
    
    // 3. 更新模型的校核状态
    if (currentModel.value) {
      const model = staticModels.value.find(m => m.id === currentModel.value!.id);
      if (model) {
        model.verify_status = verifiedDataset.verify_status;
      }
    }
    
    showVerifyModal.value = false;
    alert(`校核完成: ${verifiedDataset.verify_status}`);
  } catch (err: any) {
    const detail = err?.response?.data?.detail || err?.message || "未知错误";
    alert("校核失败: " + detail);
    console.error("校核错误详情:", err?.response?.data, err);
  } finally {
    verifying.value = false;
  }
};

const getStatusClass = (status?: string) => {
  if (status === "校核通过") return "verified";
  if (status === "校核失败") return "failed";
  return "unverified";
};
</script>

<style scoped>
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
}
.panel-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
}
.table td a.link {
  margin-right: 12px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal {
  background: var(--card);
  border-radius: 12px;
  width: 520px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
}
.modal-header h3 {
  margin: 0;
  font-size: 16px;
}
.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--muted);
}
.modal-body {
  padding: 20px;
}
.modal-footer {
  padding: 16px 20px;
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
.form-group {
  margin-bottom: 16px;
}
.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 13px;
  font-weight: 500;
}
.form-group .required {
  color: var(--red);
}
.form-hint {
  margin-top: 6px;
  font-size: 12px;
  color: var(--muted);
}
.form-row {
  display: flex;
  gap: 16px;
}
.form-row .form-group {
  flex: 1;
}

.status-tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}
.status-tag.verified {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}
.status-tag.failed {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}
.status-tag.unverified {
  background: rgba(156, 163, 175, 0.15);
  color: #9ca3af;
}
</style>
