<template>
  <MainLayout>
    <div class="page-header">
      <h1 class="page-title">模型管理</h1>
      <div class="header-actions">
        <button class="btn" :disabled="seeding" @click="handleSeedEpfModels">
          {{ seeding ? "初始化中..." : "初始化EPF模型" }}
        </button>
        <button class="btn primary" @click="showUploadModal = true">上传模型文件</button>
      </div>
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
                <a class="link" href="#" @click.prevent="handleTrainModel(model)">训练模型</a>
                <a class="link" href="#" @click.prevent="handleUploadTrainedModel(model)">上传已训练文件</a>
                <a class="link" href="#" @click.prevent="handleDownloadTrainedModel(model)">下载训练文件</a>
                <a class="link danger" href="#" @click.prevent="handleDeleteModel(model)">删除</a>
              </td>
            </tr>
            <tr v-if="staticModels.length === 0">
              <td colspan="6" class="empty-row">暂无模型数据</td>
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
          <input class="input" v-model="uploadForm.name" placeholder="请输入模型名称" />
        </div>
        <div class="form-group">
          <label>描述</label>
          <textarea class="input" rows="2" v-model="uploadForm.description" placeholder="请输入描述"></textarea>
        </div>
        <div class="form-group">
          <label>模型文件 <span class="required">*</span></label>
          <input type="file" accept=".py" @change="handleModelFileSelect" />
        </div>
        <div class="form-group">
          <label>选择数据集 <span class="required">*</span></label>
          <select class="input" v-model.number="uploadForm.dataset_id">
            <option value="">请选择数据集</option>
            <option v-for="ds in datasetOptions" :key="ds.id" :value="ds.id">
              {{ ds.name }}
            </option>
          </select>
        </div>
        <div class="form-group">
          <label>预测类型 <span class="required">*</span></label>
          <select class="input" v-model="uploadForm.prediction_type">
            <option value="week_ahead">周前概率</option>
          </select>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>训练开始日期</label>
            <input class="input" type="date" v-model="uploadForm.train_start_date" />
          </div>
          <div class="form-group">
            <label>训练结束日期</label>
            <input class="input" type="date" v-model="uploadForm.train_end_date" />
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn" @click="showUploadModal = false">取消</button>
        <button class="btn primary" :disabled="uploading" @click="handleUploadModel">
          {{ uploading ? "上传中..." : "上传" }}
        </button>
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
    <input
      ref="trainedFileInput"
      type="file"
      style="display: none"
      accept=".pt,.pth,.pkl,.joblib,.onnx,.zip,.bin,.json,.csv"
      @change="handleTrainedFileSelect"
    />
  </MainLayout>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import MainLayout from "../layouts/MainLayout.vue";
import { fetchDatasets, uploadDataset, verifyDatasetAsync } from "../api/datasets";
import { deleteModel, downloadTrainedModelFile, fetchModels, seedEpfModels, trainModel, uploadModel, uploadTrainedModelFile } from "../api/models";

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
const training = ref(false);
const seeding = ref(false);
const uploading = ref(false);
const trainedFileInput = ref<HTMLInputElement | null>(null);
const pendingUploadModelName = ref<string>("");
const currentModel = ref<ModelItem | null>(null);
const datasetOptions = ref<{ id: number; name: string }[]>([]);

const uploadForm = reactive({
  name: "",
  description: "",
  dataset_id: "" as number | "",
  prediction_type: "week_ahead",
  train_start_date: "2024-01-01",
  train_end_date: "2024-12-31",
  file: null as File | null,
});

const verifyForm = reactive({
  name: "",
  description: "",
  file: null as File | null,
});

const staticModels = ref<ModelItem[]>([]);

const toPlanTypeLabel = (predictionType: string) => {
  const text = (predictionType || "").toLowerCase();
  if (text.includes("week")) return "周前概率";
  if (text.includes("day")) return "日前预测";
  return predictionType || "未知";
};

const loadModels = async () => {
  try {
    const [modelRes, datasetRes] = await Promise.all([
      fetchModels({ page: 1, size: 200 }),
      fetchDatasets({ page: 1, size: 200 }),
    ]);
    const datasetMap = new Map<number, string>(
      datasetRes.items.map((item) => [item.id, item.name]),
    );
    datasetOptions.value = datasetRes.items.map((item) => ({
      id: item.id,
      name: item.name,
    }));
    staticModels.value = modelRes.items.map((item) => ({
      id: item.id,
      name: item.name,
      description: item.description || "-",
      dataset: item.dataset_id ? datasetMap.get(item.dataset_id) || "未绑定" : "未绑定",
      type: toPlanTypeLabel(item.prediction_type),
      verify_status: undefined,
    }));
  } catch (err: any) {
    const detail = err?.response?.data?.detail || err?.message || "未知错误";
    alert("加载模型失败: " + detail);
  }
};

const handleModelFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    uploadForm.file = target.files[0];
  }
};

const handleUploadModel = async () => {
  if (uploading.value) return;
  if (!uploadForm.name || !uploadForm.dataset_id || !uploadForm.file) {
    alert("请填写模型名称、选择数据集并选择模型文件");
    return;
  }
  uploading.value = true;
  try {
    const formData = new FormData();
    formData.append("name", uploadForm.name);
    formData.append("description", uploadForm.description || "");
    formData.append("dataset_id", String(uploadForm.dataset_id));
    formData.append("train_start_date", uploadForm.train_start_date);
    formData.append("train_end_date", uploadForm.train_end_date);
    formData.append("prediction_type", uploadForm.prediction_type);
    formData.append("file", uploadForm.file);
    await uploadModel(formData);
    showUploadModal.value = false;
    uploadForm.name = "";
    uploadForm.description = "";
    uploadForm.dataset_id = "";
    uploadForm.file = null;
    await loadModels();
    alert("模型上传成功");
  } catch (err: any) {
    const detail = err?.response?.data?.detail || err?.message || "未知错误";
    alert("模型上传失败: " + detail);
  } finally {
    uploading.value = false;
  }
};

const handleSeedEpfModels = async () => {
  if (seeding.value) return;
  seeding.value = true;
  try {
    const result = await seedEpfModels();
    await loadModels();
    alert(`初始化完成：新增 ${result.created}，已存在 ${result.existing}`);
  } catch (err: any) {
    const detail = err?.response?.data?.detail || err?.message || "未知错误";
    alert("初始化失败: " + detail);
  } finally {
    seeding.value = false;
  }
};

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
    const verifiedDataset = await verifyDatasetAsync(uploadedDataset.id);
    
    // 3. 更新模型的校核状态
    if (currentModel.value) {
      const model = staticModels.value.find(m => m.id === currentModel.value!.id);
      if (model) {
        model.verify_status = verifiedDataset.verify_status;
      }
    }
    
    showVerifyModal.value = false;
    alert(`校核任务已提交: ${verifiedDataset.verify_status || "校核中"}`);
  } catch (err: any) {
    const detail = err?.response?.data?.detail || err?.message || "未知错误";
    alert("校核失败: " + detail);
    console.error("校核错误详情:", err?.response?.data, err);
  } finally {
    verifying.value = false;
  }
};

const handleTrainModel = async (model: ModelItem) => {
  if (training.value) return;
  training.value = true;
  try {
    const result = await trainModel(model.id);
    const selected = (result.selected_model || model.name).toLowerCase();
    staticModels.value.forEach((item) => {
      item.description = item.description.replace(/（已训练）/g, "");
      const normalized = item.name.toLowerCase();
      if (selected.includes("ensemble") && normalized.includes("集成")) {
        item.description = `${item.description}（已训练）`;
      } else if (selected.includes("mamba") && normalized.includes("mamba")) {
        item.description = `${item.description}（已训练）`;
      } else if (selected.includes("tcn") && normalized.includes("tcn")) {
        item.description = `${item.description}（已训练）`;
      } else if (selected.includes("nlinear") && normalized.includes("nlinear")) {
        item.description = `${item.description}（已训练）`;
      }
    });
    alert(
      `训练完成，模型：${result.selected_model || model.name}，综合得分：${(result.selected_score || 0).toFixed(4)}`
    );
    await loadModels();
  } catch (err: any) {
    const detail = err?.response?.data?.detail || err?.message || "未知错误";
    alert("训练失败: " + detail);
  } finally {
    training.value = false;
  }
};

const handleUploadTrainedModel = (model: ModelItem) => {
  pendingUploadModelName.value = model.name;
  trainedFileInput.value?.click();
};

const handleTrainedFileSelect = async (e: Event) => {
  const target = e.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file || !pendingUploadModelName.value) {
    return;
  }

  try {
    await uploadTrainedModelFile(pendingUploadModelName.value, file);
    alert(`已上传训练文件：${file.name}`);
  } catch (err: any) {
    const detail = err?.response?.data?.detail || err?.message || "未知错误";
    alert("上传训练文件失败: " + detail);
  } finally {
    target.value = "";
    pendingUploadModelName.value = "";
  }
};

const handleDownloadTrainedModel = async (model: ModelItem) => {
  try {
    const response = await downloadTrainedModelFile(model.name);
    const blob = new Blob([response.data]);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;

    const disposition = response.headers["content-disposition"] as string | undefined;
    const matched = disposition?.match(/filename="?([^"]+)"?/i);
    link.download = matched?.[1] || `${model.name}_trained_file.bin`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (err: any) {
    const detail = err?.response?.data?.detail || err?.message || "未知错误";
    alert("下载训练文件失败: " + detail);
  }
};

const handleDeleteModel = async (model: ModelItem) => {
  if (!confirm(`确定删除模型 "${model.name}" 吗？`)) return;
  try {
    await deleteModel(model.id);
    staticModels.value = staticModels.value.filter((item) => item.id !== model.id);
    alert("删除成功");
  } catch (err: any) {
    const detail = err?.response?.data?.detail || err?.message || "未知错误";
    alert("删除失败: " + detail);
  }
};

const getStatusClass = (status?: string) => {
  if (status === "校核通过") return "verified";
  if (status === "校核失败") return "failed";
  return "unverified";
};

onMounted(loadModels);
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
.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
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
