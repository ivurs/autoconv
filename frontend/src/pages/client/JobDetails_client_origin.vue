<template>
  <div class="job-content">
    <!-- ✅ Fullscreen loading overlay for Stage 1 -->
    <div v-if="loading" class="fullscreen-loader">
      <el-icon><i class="el-icon-loading"></i></el-icon>
      <p>正在加载工单详情，请稍候...</p>
    </div>

    <el-row v-else :gutter="30">
      <el-col :span="11">
        <el-card>
          <div class="pdf-header" ref="pdfHeader">
            <h2 class="center-title">工单关联文件</h2>
          </div>

          <!-- ✅ Stage 2: PDF loading indicator -->
          <div v-if="pdfLoading" class="loading-text">
            <i class="el-icon-loading"></i>
            正在加载PDF文件...
          </div>

          <!-- ✅ PDF Canvas -->
          <div v-else class="pdf-container">
            <canvas ref="pdfCanvasRef" :style="{ width: '70%', height: '970px' }"></canvas>
          </div>

          <!-- Pagination -->
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

      <el-col :span="12">
        <el-collapse v-model="activeNames">
          <el-collapse-item title="文件预审信息" name="1">
            <el-descriptions class="margin-top" :column="1" :size="size" border>
              <el-descriptions-item label="工单名">{{ jobInfo.jobName }}</el-descriptions-item>
              <el-descriptions-item label="工单种类">{{ jobTypeName }}</el-descriptions-item>
              <el-descriptions-item label="工单简介">{{ jobInfo.jobIntro }}</el-descriptions-item>
              <el-descriptions-item label="客户预算">{{ jobInfo.clientBudget }} 元</el-descriptions-item>
              <el-descriptions-item label="发布日期">{{
                  dayjs(jobInfo.issueDate).format('YYYY年MM月DD日 HH:mm:ss')
                }}
              </el-descriptions-item>
              <el-descriptions-item label="文件名">{{ jobInfo.fileName }}</el-descriptions-item>
            </el-descriptions>
          </el-collapse-item>

          <el-collapse-item title="合同预审结果" name="2">
            <el-table :data="paginatedData" border style="width: 100%">
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
pdfjsLib.GlobalWorkerOptions.workerSrc = require('pdfjs-dist/build/pdf.worker.entry');

const jobInfo = ref<any>({});
const loading = ref(true);         // ✅ Stage 1 loading flag
const pdfLoading = ref(true);      // ✅ Stage 2 loading flag
const error = ref(null);
const pdfUrl = ref<string | null>(null);
const pdfCanvasRef = ref<HTMLCanvasElement | null>(null);
const pdfDocRef = ref<any>(null);  // cache PDF doc
const currentPage = ref(1);
const totalPages = ref(0);
const tableCurrentPage = ref(1);
const size = ref('small');
const activeNames = ref(['1', '2']);
const pageSize = 5;

const tableData = ref<any[]>([]);
const route = useRoute();
const router = useRouter();

const jobTypeMapping: Record<number, string> = {
  1: '房地产',
  2: '婚姻',
  3: '公司法'
};
const jobTypeName = computed(() => jobTypeMapping[jobInfo.value.jobType] || '未知类型');

const paginatedData = computed(() => {
  const start = (tableCurrentPage.value - 1) * pageSize;
  return tableData.value.slice(start, start + pageSize);
});

const toggleExpand = (row: any, field: string) => (row[field] = !row[field]);
const handleTablePageChange = (page: number) => (tableCurrentPage.value = page);

const handlePdfPageChange = async (page: number) => {
  currentPage.value = page;
  await renderPage(page);
};

const renderPage = async (pageNum: number) => {
  if (!pdfDocRef.value || !pdfCanvasRef.value) return;
  const page = await pdfDocRef.value.getPage(pageNum);
  const canvas = pdfCanvasRef.value;
  const context = canvas.getContext('2d')!;
  const viewport = page.getViewport({ scale: 1 });
  canvas.height = viewport.height;
  canvas.width = viewport.width;
  await page.render({ canvasContext: context, viewport }).promise;
};

const locatePdfPage = async (pageNum: number) => {
  currentPage.value = pageNum;
  await renderPage(pageNum);
};

// ✅ Base64 → Blob
const base64ToBlob = (code: string) => {
  if (code.startsWith('data:application/pdf;base64,')) {
    code = code.replace('data:application/pdf;base64,', '');
  }
  const raw = window.atob(code);
  const uInt8Array = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; ++i) uInt8Array[i] = raw.charCodeAt(i);
  return new Blob([uInt8Array], { type: 'application/pdf' });
};

// ✅ Stage 1: Fetch meta + table
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
      path: data.path
    };

    tableData.value = data.paragraph.map((_: any, index: number) => ({
      paragraph: data.paragraph[index],
      paragraphClean: data.paragraph_clean[index],
      modelPredictDetails: data.model_predict_details[index],
      modelPredictLabels: data.model_predict_labels[index],
      pageNum: data.page_num[index]
    }));

    // ✅ Stage 2: Load PDF asynchronously (non-blocking)
    setTimeout(() => loadPdfAsync(data.file_content), 0);
  } catch (err: any) {
    error.value = err.message || '获取工单信息失败';
  } finally {
    loading.value = false;
  }
};

// ✅ Stage 2: Async PDF loader
const loadPdfAsync = async (base64: string) => {
  try {
    const blob = base64ToBlob(base64);
    pdfUrl.value = URL.createObjectURL(blob);

    const loadingTask = pdfjsLib.getDocument(pdfUrl.value);
    pdfDocRef.value = await loadingTask.promise;
    totalPages.value = pdfDocRef.value.numPages;

    // ✅ wait for canvas to mount
    await nextTick();
    await renderPage(currentPage.value);
  } catch (err) {
    console.error('加载PDF失败', err);
  } finally {
    pdfLoading.value = false;
  }
};


onMounted(async () => {
  await fetchJobDetails();
});

watch(pdfUrl, async (newUrl) => {
  if (newUrl && pdfDocRef.value) {
    await nextTick();
    await renderPage(currentPage.value);
    pdfLoading.value = false; // ✅ ensure hides spinner after render
  }
});


const submitForm = async () => {
  const postData = {
    job_id: parseInt(Array.isArray(route.params.id) ? route.params.id[0] : route.params.id, 10)
  };
  try {
    const response = await myAxios.post('/job/acceptJob', postData);
    ElMessage.success('提交成功');
    changePage('/newJobListForClient');
  } catch (error) {
    ElMessage.error('提交失败');
  }
};

const changePage = (path: string) => router.push(path);
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
.fullscreen-loader {
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
</style>
