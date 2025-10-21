<template>
  <el-card class="job-title">
    <div class="title-container">
      <h2 class="my-title">工单创建</h2>
    </div>
  </el-card>
  <div class="layout-container">
    <el-steps :active="currentStep" finish-status="success" direction="vertical" class="step-container">
      <el-step title="Step 1"/>
      <el-step title="Step 2"/>
    </el-steps>
    <el-row>
      <el-col :span="12" v-loading="isLoading" v-if="currentStep === 0">
        <div class="form-container">
          <el-form
              ref="ruleFormRef"
              style="max-width: 600px"
              :model="ruleForm"
              :rules="rules"
              label-width="auto"
              class="demo-ruleForm"
              :size="formSize"
              status-icon
          >
            <el-form-item label="工单标题" prop="jobName">
              <el-input v-model="ruleForm.job_name"/>
            </el-form-item>
            <el-form-item label="工单种类" prop="jobType">
              <el-select v-model="ruleForm.job_type" placeholder="列表选择分类">
                <el-option label="房地产" :value="1"></el-option>
                <el-option label="婚姻" :value="2"></el-option>
                <el-option label="公司法" :value="3"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="工单简介" prop="intro">
              <el-input v-model="ruleForm.job_intro"/>
            </el-form-item>
            <el-form-item label="上传文件" label-width="100px">
              <el-upload
                  drag
                  class="upload-demo"
                  show-file-list="false"
                  multiple
                  :before-upload="beforeUpload"
              >
                <el-icon class="el-icon--upload">
                  <upload-filled/>
                </el-icon>
                <div class="el-upload__text">
                  Drop file here or <em>click to upload</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">
                    jpg/png files with a size less than 100Mb
                  </div>
                </template>
              </el-upload>
            </el-form-item>
            <el-form-item label="预期时间" prop="expected_time" required>
              <el-date-picker
                  v-model="ruleForm.expected_time"
                  type="datetime"
                  placeholder="选择预期时间"
                  style="width: 100%;"
                  :disabled-date="disabledDate"
              />
            </el-form-item>
            <el-form-item label="预期金额" prop="client_budget">
              <el-input v-model="ruleForm.client_budget"/>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="goNextStep">
                Next
              </el-button>
              <el-button @click="resetForm(ruleFormRef)">Reset</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-col>
      <el-col :span="12" v-if="currentStep === 1">
        <div class="table-container">
          <el-form
              ref="ruleFormRef"
              style="max-width: 600px"
              :model="ruleForm"
              :rules="rules"
              label-width="auto"
              class="demo-ruleForm"
              :size="formSize"
              status-icon
          >
            <el-form-item label="工单标题" prop="jobName">
              <el-input v-model="ruleForm.job_name"/>
            </el-form-item>
            <el-form-item label="工单种类" prop="jobType">
              <el-select v-model="ruleForm.job_type" placeholder="列表选择分类">
                <el-option label="房地产" :value="1"></el-option>
                <el-option label="婚姻" :value="2"></el-option>
                <el-option label="公司法" :value="3"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="工单简介" prop="intro">
              <el-input v-model="ruleForm.job_intro"/>
            </el-form-item>
            <el-form-item label="Progress Analysis">
              <el-progress
                v-if="isLoading"
                :percentage="progress"
                :text-inside="true"
                stroke-width="18"
                status="success"
                style="width: 100%"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="submitForm(ruleFormRef)">
                Create
              </el-button>
              <el-button @click="resetForm(ruleFormRef)">Reset</el-button>
              <el-button @click="goPrevStep">Previous</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts" setup>
import { reactive, ref } from 'vue'
import { ComponentSize, ElMessage, FormInstance, FormRules, UploadUserFile } from 'element-plus'
import { jobCreate, fileUpload } from "@/api/user";
import { UploadFilled } from '@element-plus/icons-vue'
import { useRouter } from "vue-router";

interface RuleForm {
  file_id: number
  job_name: string
  job_type: number
  job_intro: string
  client_budget: string
  expected_time: string; // 新增字段
}

const router = useRouter();
const formSize = ref<ComponentSize>('default')
const ruleFormRef = ref<FormInstance>()
const ruleForm = ref<RuleForm>({
  file_id: -1,
  job_name: '',
  job_type: '',
  job_intro: '此工单是关于',
  client_budget: '',
  expected_time: '', // 初始化为空字符串
})

const uploadedFiles = ref<UploadUserFile[]>([])

// 禁用过去的日期
const disabledDate = (time: Date) => {
  return time.getTime() < Date.now();
};

const currentStep = ref(0);  // 控制当前步骤

const rules = reactive<FormRules<RuleForm>>({
  job_name: [{ required: true, message: '请填写工单名', trigger: 'blur' }],
  job_type: [{ required: true, message: '请选择工单类型', trigger: 'blur' }],
  client_budget: [{ required: true, message: '请填写预估金额', trigger: 'blur' }],
  expected_time: [{ required: true, message: '请选择预期完成时间', trigger: 'blur' }],
})

const isLoading = ref(false); // 控制滚轮的显示
const progress = ref(0); // 进度条的进度

const goNextStep = () => {
  if (currentStep.value < 1) {
    currentStep.value++;
  }
};

const goPrevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--;
  }
};

const beforeUpload = async (file: File) => {
  // 校验文件大小不超过100Mb
  if (file.size / 1024 / 1024 > 100) {
    ElMessage.error('头像大小不应超过100Mb！')
    return false
  }

  uploadedFiles.value = [{ name: file.name, url: URL.createObjectURL(file) }]
  const formData = new FormData();
  formData.append('file', file);
  
  // Call fileUpload with progress tracking
  await fileUpload(formData, {
    onUploadProgress: (progressEvent) => {
      if (progressEvent.lengthComputable) {
        progress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total);
      }
    }
  });

  const res = await fileUpload(formData);
  ruleForm.value.file_id = res.data.data.data
  return false
}

const submitForm = async (formEl: FormInstance | undefined) => {
  if (!formEl) return;
  await formEl.validate(async (valid) => {
    if (valid) {
      try {
        isLoading.value = true; 
        progress.value = 0;

        // Call the job creation API and track progress
        const res = await jobCreate(ruleForm.value, {
          onUploadProgress: (progressEvent) => {
            if (progressEvent.lengthComputable) {
              progress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            }
          }
        });

        if (res.data.code === 200) {
          ElMessage.success('提交成功');
          changePage('/jobManage');
        } else {
          ElMessage.error('提交失败');
        }
      } catch (error) {
        console.error('提交表单失败:', error);
        ElMessage.error('提交失败');
      } finally {
        isLoading.value = false;
        progress.value = 0; // Reset progress after submission
      }
    }
  });
};

const changePage = (path: any) => {
  router.push(path);
};

const resetForm = (formEl: FormInstance | undefined) => {
  if (!formEl) return
  formEl.resetFields()
}
</script>

<style scoped>
.layout-container {
  display: flex;
  justify-content: center; /* 水平居中 */
  align-items: center; /* 垂直居中 */
  height: 70vh; /* 占满视口高度 */
  width: 50%; /* 设置宽度为视口宽度的 90% */
  margin: 0 auto; /* 通过自动外边距实现水平居中 */
  background-color: #f5f5f5; /* 可选：设置背景颜色 */
  gap: 50px; /* 设置左右两部分的间距 */
}

/* 标题片卡样式调整 */
.job-title {
  width: 66% !important;
  margin: 0 auto;
  background-color: #fff !important;
  border-radius: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  padding: 1px;
}

/* 标题样式调整 */
.my-title {
  text-align: center;
  color: #1890ff !important;
  margin: 0 auto; /* 水平居中 */
  margin-bottom: 0px !important;
  font-size: 24px;
  font-weight: bold;
}

/* 增加卡片间垂直间距 */
.job-title + .layout-container {
  margin-top: 30px !important;
}

.step-container {
  margin-bottom: 20px;
  height: 40vh; /* 设置高度为原来的一半 */
  width: 150px; /* 可选：调整宽度 */
}

.form-container, .table-container {
  background-color: #fff; /* 可选：设置背景颜色 */
  padding: 20px; /* 内边距 */
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); /* 可选：添加阴影 */
  border-radius: 8px; /* 可选：圆角 */
  width: 700px;
}

.spin-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}
</style>