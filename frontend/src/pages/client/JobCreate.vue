<template>
  <!-- 🌟 Full-screen loading overlay -->
  <div v-if="isLoading" class="loading-overlay">
    <div class="loading-box">
      <el-icon class="loading-icon"><Loading /></el-icon>
      <p class="loading-text">AI 正在分析文件，请稍候...</p>
    </div>
  </div>

  <el-card class="job-title">
    <div class="title-container">
      <h2 class="my-title">工单创建</h2>
    </div>
  </el-card>

  <div class="layout-container">
    <el-steps :active="currentStep" finish-status="success" direction="vertical" class="step-container">
      <el-step title="Step 1" />
      <el-step title="Step 2" />
    </el-steps>

    <el-row>
      <!-- Step 1 -->
      <el-col :span="12" v-if="currentStep === 0">
        <div class="form-container">
          <el-form
            ref="ruleFormRef"
            :model="ruleForm"
            :rules="rules"
            label-width="auto"
            class="demo-ruleForm"
            :size="formSize"
            status-icon
          >
            <el-form-item label="工单标题" prop="job_name">
              <el-input v-model="ruleForm.job_name" />
            </el-form-item>

            <el-form-item label="工单种类" prop="job_type">
              <el-select v-model="ruleForm.job_type" placeholder="列表选择分类">
                <el-option label="房地产" :value="1" />
                <el-option label="婚姻" :value="2" />
                <el-option label="公司法" :value="3" />
              </el-select>
            </el-form-item>

            <el-form-item label="工单简介" prop="job_intro">
              <el-input v-model="ruleForm.job_intro" />
            </el-form-item>

            <el-form-item label="上传文件" label-width="100px">
              <el-upload
                drag
                class="upload-demo"
                show-file-list="false"
                multiple
                :auto-upload="false"
                action="#"
                :before-upload="beforeUpload"
              >
                <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                <div class="el-upload__text">
                  拖拽文件到此处或 <em>点击上传</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">支持 PDF / JPG / PNG 文件，小于 100 MB</div>
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
              <el-input v-model="ruleForm.client_budget" disabled />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="goNextStep">Next</el-button>
              <el-button @click="resetForm(ruleFormRef)">Reset</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-col>

      <!-- Step 2 -->
      <el-col :span="12" v-if="currentStep === 1">
        <div class="table-container">
          <el-form
            ref="ruleFormRef"
            :model="ruleForm"
            :rules="rules"
            label-width="auto"
            class="demo-ruleForm"
            :size="formSize"
            status-icon
          >
            <el-form-item label="工单标题" prop="job_name">
              <el-input v-model="ruleForm.job_name" />
            </el-form-item>

            <el-form-item label="工单种类" prop="job_type">
              <el-select v-model="ruleForm.job_type" placeholder="列表选择分类">
                <el-option label="房地产" :value="1" />
                <el-option label="婚姻" :value="2" />
                <el-option label="公司法" :value="3" />
              </el-select>
            </el-form-item>

            <el-form-item label="工单简介" prop="job_intro">
              <el-input v-model="ruleForm.job_intro" />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="submitForm(ruleFormRef)">Create</el-button>
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
import { jobCreate, fileUpload } from '@/api/user'
import { UploadFilled, Loading } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'

interface RuleForm {
  file_id: number
  job_name: string
  job_type: number
  job_intro: string
  client_budget: string
  expected_time: string
}

const router = useRouter()
const formSize = ref<ComponentSize>('default')
const ruleFormRef = ref<FormInstance>()
const isLoading = ref(false)
const ruleForm = ref<RuleForm>({
  file_id: -1,
  job_name: '',
  job_type: 1,
  job_intro: '此工单是关于',
  client_budget: '1500',
  expected_time: '',
})

const uploadedFiles = ref<UploadUserFile[]>([])
const disabledDate = (time: Date) => time.getTime() < Date.now()
const currentStep = ref(0)

const rules = reactive<FormRules<RuleForm>>({
  job_name: [{ required: true, message: '请填写工单名', trigger: 'blur' }],
  job_type: [{ required: true, message: '请选择工单类型', trigger: 'blur' }],
  expected_time: [{ required: true, message: '请选择预期完成时间', trigger: 'blur' }],
})

const goNextStep = () => { if (currentStep.value < 1) currentStep.value++ }
const goPrevStep = () => { if (currentStep.value > 0) currentStep.value-- }

// 上传文件
const beforeUpload = async (file: File) => {
  if (file.size / 1024 / 1024 > 100) {
    ElMessage.error('文件大小不应超过 100 MB')
    return false
  }
  uploadedFiles.value = [{ name: file.name, url: URL.createObjectURL(file) }]
  const formData = new FormData()
  formData.append('file', file)
  try {
    const res = await fileUpload(formData)
    console.log('upload response', res.data)
    // 根据后端返回结构调整
    ruleForm.value.file_id = res.data.data.file_id || res.data.data.data
    ElMessage.success('文件上传成功')
  } catch (error) {
    console.error(error)
    ElMessage.error('文件上传失败')
  }
  return false
}

// 提交表单 + 加载状态
const submitForm = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate(async (valid) => {
    if (!valid) return

    if (!ruleForm.value.expected_time) {
      ElMessage.warning('请选择预期完成时间')
      return
    }
    if (ruleForm.value.file_id <= 0) {
      ElMessage.warning('请先上传文件')
      return
    }

    // 转换时间格式
    ruleForm.value.expected_time = dayjs(ruleForm.value.expected_time).format('YYYY-MM-DD HH:mm:ss')

    // 确保预算为数字
    ruleForm.value.client_budget = parseFloat(ruleForm.value.client_budget).toString()

    isLoading.value = true
    try {
      const res = await jobCreate(ruleForm.value)
      if (res.data.code === 200) {
        ElMessage.success('提交成功！')
        router.push('/jobManage')
      } else {
        ElMessage.error(res.data.msg || '提交失败')
      }
    } catch (error) {
      console.error(error)
      ElMessage.error('请求失败，请稍后再试')
    } finally {
      isLoading.value = false
    }
  })
}

const resetForm = (formEl: FormInstance | undefined) => { if (formEl) formEl.resetFields() }
</script>

<style scoped>
.layout-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 70vh;
  width: 50%;
  margin: 0 auto;
  background-color: #f5f5f5;
  gap: 50px;
}

.job-title {
  width: 66%;
  margin: 0 auto;
  background-color: #fff;
  border-radius: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  padding: 1px;
}

.my-title {
  text-align: center;
  color: #1890ff;
  font-size: 24px;
  font-weight: bold;
}

.step-container {
  margin-bottom: 20px;
  height: 40vh;
  width: 150px;
}

.form-container, .table-container {
  background-color: #fff;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  width: 700px;
}

/* 🌟 Elegant AI loading overlay */
.loading-overlay {
  position: fixed;
  top: 0; left: 0;
  width: 100vw; height: 100vh;
  background: radial-gradient(circle at center, rgba(30,144,255,0.15), rgba(0,0,0,0.8));
  display: flex;
  justify-content: center;
  align-items: center;
  backdrop-filter: blur(6px);
  z-index: 9999;
}

.loading-box {
  text-align: center;
  color: #fff;
  animation: fadeIn 0.5s ease-in-out;
}

.loading-icon {
  font-size: 60px;
  color: #40a9ff;
  animation: spin 1.5s linear infinite;
}

.loading-text {
  font-size: 20px;
  margin-top: 16px;
  color: #e0f7ff;
  letter-spacing: 1px;
}

@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>
