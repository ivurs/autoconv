<template>
  <div class="job-content">
    <!-- ✅ 顶部全屏加载工单信息 -->
    <div v-if="loading" class="overlay">
      <i class="el-icon-loading"></i>
      <p>正在加载工单详情，请稍候...</p>
    </div>

    <el-row v-else :gutter="30">
      <!-- ==================== 左侧 PDF ==================== -->
      <el-col :span="11">
        <el-card>
          <div class="pdf-header" ref="pdfHeader">
            <h2 class="center-title">工单关联文件</h2>
          </div>

          <!-- PDF 加载提示 -->
          <div v-if="!pdfUrl" class="loading-text">
            <i class="el-icon-loading"></i> 正在加载PDF文件...
          </div>

          <!-- PDF 渲染区域 -->
          <div v-else class="pdf-container">
            <canvas ref="pdfCanvasRef" :style="{ width: '70%', height: '970px' }"></canvas>
          </div>

          <!-- PDF 分页控件 -->
          <div class="pagination-container">
            <el-pagination
              v-if="totalPages > 1"
              :current-page="currentPage"
              :page-size="1"
              :total="totalPages"
              layout="prev, pager, next"
              @current-change="handlePdfPageChange"
            />
          </div>
        </el-card>
      </el-col>

      <!-- ==================== 右侧信息与结果 ==================== -->
      <el-col :span="12">
        <el-collapse v-model="activeNames">
          <!-- 文件信息 -->
          <el-collapse-item title="文件预审信息" name="1">
            <el-descriptions class="margin-top" :column="1" :size="size" border>
              <el-descriptions-item label="工单名">{{ jobInfo.jobName }}</el-descriptions-item>
              <el-descriptions-item label="工单种类">{{ jobTypeName }}</el-descriptions-item>
              <el-descriptions-item label="工单简介">{{ jobInfo.jobIntro }}</el-descriptions-item>
              <el-descriptions-item label="客户预算">{{ jobInfo.clientBudget }} 元</el-descriptions-item>
              <el-descriptions-item label="发布日期">
                {{ dayjs(jobInfo.issueDate).format('YYYY年MM月DD日 HH:mm:ss') }}
              </el-descriptions-item>
              <el-descriptions-item label="文件名">{{ jobInfo.fileName }}</el-descriptions-item>
            </el-descriptions>
          </el-collapse-item>

          <!-- 合同预审结果 -->
          <el-collapse-item title="合同预审结果" name="2">
            <!-- ✅ 优化后的加载显示 -->
            <div v-if="loadingTable" class="loading-text">
              <i class="el-icon-loading"></i> 正在加载合同预审结果，请稍候...
            </div>

            <!-- ✅ 没有数据 -->
            <el-empty v-else-if="tableData.length === 0" description="暂无预审结果" />

            <!-- ✅ 有数据才显示表格 -->
            <el-table
              v-else
              :data="paginatedData"
              border
              style="width: 100%"
              empty-text="暂无预审结果"
            >
              <el-table-column prop="paragraph" label="段落">
                <template #default="scope">
                  <span class="clickable-text" @click="locatePdfPage(scope.row.pageNum)">
                    {{
                      scope.row.paragraph.length > 20 && !scope.row.expanded
                        ? scope.row.paragraph.slice(0, 20) + '...'
                        : scope.row.paragraph
                    }}
                  </span>
                  <el-button
                    v-if="scope.row.paragraph.length > 20"
                    type="text"
                    @click="toggleExpand(scope.row, 'expanded')"
                  >
                    {{ scope.row.expanded ? '收起' : '展开' }}
                  </el-button>
                </template>
              </el-table-column>

              <el-table-column prop="paragraphClean" label="段落清理后">
                <template #default="scope">
                  <span>
                    {{
                      scope.row.paragraphClean.length > 20 && !scope.row.expandedClean
                        ? scope.row.paragraphClean.slice(0, 20) + '...'
                        : scope.row.paragraphClean
                    }}
                  </span>
                  <el-button
                    v-if="scope.row.paragraphClean.length > 20"
                    type="text"
                    @click="toggleExpand(scope.row, 'expandedClean')"
                  >
                    {{ scope.row.expandedClean ? '收起' : '展开' }}
                  </el-button>
                </template>
              </el-table-column>

              <el-table-column prop="modelPredictDetails" label="模型预测详情">
                <template #default="scope">
                  <span>
                    {{
                      scope.row.modelPredictDetails.length > 20 && !scope.row.expandedDetails
                        ? scope.row.modelPredictDetails.slice(0, 20) + '...'
                        : scope.row.modelPredictDetails
                    }}
                  </span>
                  <el-button
                    v-if="scope.row.modelPredictDetails.length > 20"
                    type="text"
                    @click="toggleExpand(scope.row, 'expandedDetails')"
                  >
                    {{ scope.row.expandedDetails ? '收起' : '展开' }}
                  </el-button>
                </template>
              </el-table-column>

              <el-table-column prop="modelPredictLabels" label="模型预测标签">
                <template #default="scope">
                  <span>
                    {{
                      scope.row.modelPredictLabels.length > 20 && !scope.row.expandedLabels
                        ? scope.row.modelPredictLabels.slice(0, 20) + '...'
                        : scope.row.modelPredictLabels
                    }}
                  </span>
                  <el-button
                    v-if="scope.row.modelPredictLabels.length > 20"
                    type="text"
                    @click="toggleExpand(scope.row, 'expandedLabels')"
                  >
                    {{ scope.row.expandedLabels ? '收起' : '展开' }}
                  </el-button>
                </template>
              </el-table-column>
            </el-table>

            <el-pagination
              v-if="!loadingTable && tableData.length > 0"
              @current-change="handleTablePageChange"
              :current-page="tableCurrentPage"
              :page-size="5"
              layout="prev, pager, next"
              :total="tableData.length"
            />
          </el-collapse-item>
        </el-collapse>

        <div class="button-group">
          <el-button type="primary" @click="submitForm">确认</el-button>
          <el-button @click="changePage('/JobManage')">取消</el-button>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import dayjs from 'dayjs';
import myAxios from '@/request';
import * as pdfjsLib from 'pdfjs-dist';

// ✅ Worker 设置（推荐现代写法）
import pdfWorker from 'pdfjs-dist/build/pdf.worker?url';
pdfjsLib.GlobalWorkerOptions.workerSrc = pdfWorker;

// ---- 状态变量 ----
const jobInfo = ref({});
const loading = ref(true);
const loadingTable = ref(true);
const error = ref(null);
const pdfUrl = ref<string | null>(null);
const pdfCanvasRef = ref<HTMLCanvasElement | null>(null);
const currentPage = ref(1);
const totalPages = ref(0);
const tableData = ref<any[]>([]);
const tableCurrentPage = ref(1);
const pageSize = 5;
const route = useRoute();
const router = useRouter();
const size = ref('small');
const activeNames = ref(['1', '2']);

const jobTypeMapping: Record<number, string> = { 1: '房地产', 2: '婚姻', 3: '公司法' };
const jobTypeName = computed(() => jobTypeMapping[jobInfo.value.jobType] || '未知类型');

const paginatedData = computed(() => {
  const start = (tableCurrentPage.value - 1) * pageSize;
  return tableData.value.slice(start, start + pageSize);
});

// ---- 渲染 PDF ----
const renderPage = async (pageNum: number) => {
  if (!pdfUrl.value || !pdfCanvasRef.value) return;
  const loadingTask = pdfjsLib.getDocument(pdfUrl.value);
  const pdfDoc = await loadingTask.promise;
  totalPages.value = pdfDoc.numPages;

  const page = await pdfDoc.getPage(pageNum);
  const canvas = pdfCanvasRef.value as HTMLCanvasElement;
  const context = canvas.getContext('2d')!;
  const viewport = page.getViewport({ scale: 1 });
  canvas.height = viewport.height;
  canvas.width = viewport.width;

  await page.render({ canvasContext: context, viewport }).promise;
  console.log(`✅ Page ${pageNum} rendered`);
};

const handlePdfPageChange = (p: number) => {
  currentPage.value = p;
  renderPage(p);
};
const handleTablePageChange = (p: number) => (tableCurrentPage.value = p);

const base64ToBlob = (code: string) => {
  if (code.startsWith('data:application/pdf;base64,')) {
    code = code.replace('data:application/pdf;base64,', '');
  }
  const raw = atob(code);
  const uInt8Array = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; ++i) uInt8Array[i] = raw.charCodeAt(i);
  return new Blob([uInt8Array], { type: 'application/pdf' });
};

// ---- 获取工单详情 ----
const fetchJobDetails = async () => {
  try {
    const id = route.params.id;
    const response = await myAxios.get(`/job/details?id=${id}`);
    const data = response.data.data;

    jobInfo.value = {
      jobId: data.job_id,
      jobName: data.job_name,
      jobType: data.job_type,
      jobIntro: data.job_intro,
      clientBudget: data.client_budget,
      issueDate: dayjs(data.issue_date).format('YYYY-MM-DD HH:mm:ss'),
      fileName: data.file_name,
    };

    tableData.value = data.paragraph.map((_: any, i: number) => ({
      paragraph: data.paragraph[i],
      paragraphClean: data.paragraph_clean[i],
      modelPredictDetails: data.model_predict_details[i],
      modelPredictLabels: data.model_predict_labels[i],
      pageNum: data.page_num[i],
    }));

    const blob = base64ToBlob(data.file_content);
    pdfUrl.value = URL.createObjectURL(blob);
  } catch (e: any) {
    error.value = e.message;
  } finally {
    loading.value = false;
    loadingTable.value = false;
  }
};

// ---- 生命周期 ----
onMounted(async () => {
  await fetchJobDetails();
  await nextTick();
  if (pdfUrl.value) await renderPage(1);
});

const toggleExpand = (row: any, field: string) => (row[field] = !row[field]);
const locatePdfPage = (p: number) => {
  currentPage.value = p;
  renderPage(p);
};
const submitForm = async () => {
  try {
    const id = parseInt(Array.isArray(route.params.id) ? route.params.id[0] : route.params.id, 10);
    await myAxios.post('/job/acceptJob', { job_id: id });
    ElMessage.success('提交成功');
    router.push('/newJobListForClient');
  } catch {
    ElMessage.error('提交失败');
  }
};
</script>

<style scoped>
.center-title {
  text-align: center;
}
.loading-text {
  text-align: center;
  font-size: 16px;
  color: #666;
}
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: white;
  z-index: 9999;
  color: #666;
  font-size: 18px;
}
.pdf-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  background-color: #d6d6d6;
}
.pagination-container {
  text-align: center;
  margin-top: 20px;
}
.button-group {
  position: fixed;
  bottom: 60px;
  right: 80px;
  display: flex;
  gap: 10px;
}
.clickable-text {
  color: #409eff;
  cursor: pointer;
  text-decoration: underline;
}
</style>
