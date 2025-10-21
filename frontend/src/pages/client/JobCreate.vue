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
      <!-- Step 1 -->
      <el-col :span="12" v-if="currentStep === 0">
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
                :before-upload="beforeUpload"
              >
                <el-icon class="el-icon--upload"><upload-filled/></el-icon>
                <div class="el-upload__text">
                  拖拽文件到此处或 <em>点击上传</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">仅支持 PDF / JPG / PNG 文件，小于 100 MB</div>
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
            style="max-width: 600px"
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
import { ComponentSize, ElMessage, FormInstance, FormRules, UploadUserFile, ElLoading } from 'element-plus'
import { jobCreate, fileUpload } from '@/api/user'
import { UploadFilled } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

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
const ruleForm = ref<RuleForm>({
  file_id: -1,
  job_name: '',
  job_type: 1,
  job_intro: '此工单是关于',
  client_budget: '1500',
  expected_time: '',
})

const uploadedFiles = ref<UploadUserFile[]>([])

// 禁用过去的日期
const disabledDate = (time: Date) => time.getTime() < Date.now()

const currentStep = ref(0)
const rules = reactive<FormRules<RuleForm>>({
  job_name: [{ required: true, message: '请填写工单名', trigger: 'blur' }],
  job_type: [{ required: true, message: '请选择工单类型', trigger: 'blur' }],
  client_budget: [{ required: true, message: '请填写预估金额', trigger: 'blur' }],
  expected_time: [{ required: true, message: '请选择预期完成时间', trigger: 'blur' }],
})

const goNextStep = () => {
  if (currentStep.value < 1) currentStep.value++
}
const goPrevStep = () => {
  if (currentStep.value > 0) currentStep.value--
}

// 上传文件
const beforeUpload = async (file: File) => {
  if (file.size / 1024 / 1024 > 100) {
    ElMessage.error('文件大小不应超过100 MB！')
    return false
  }

  uploadedFiles.value = [{ name: file.name, url: URL.createObjectURL(file) }]
  const formData = new FormData()
  formData.append('file', file)

  try {
    const res = await fileUpload(formData)
    ruleForm.value.file_id = res.data.data.data
    ElMessage.success('文件上传成功')
  } catch (err) {
    console.error(err)
    ElMessage.error('文件上传失败')
  }
  return false
}

// 提交表单 + 加载状态
const submitForm = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate(async (valid) => {
    if (!valid) return

    // 🌀 显示全屏加载遮罩
    const loadingInstance = ElLoading.service({
      lock: true,
      text: '正在创建工单并分析文件，请稍候...',
      background: 'rgba(0, 0, 0, 0.5)',
    })

    try {
      const res = await jobCreate(ruleForm.value)
      if (res.data.code === 200) {
        ElMessage.success('工单创建成功！')
        router.push('/jobManage')
      } else {
        ElMessage.error(res.data.msg || '工单创建失败')
      }
    } catch (error) {
      console.error(error)
      ElMessage.error('请求失败，请稍后再试')
    } finally {
      // ✅ 关闭加载遮罩
      loadingInstance.close()
    }
  })
}

const resetForm = (formEl: FormInstance | undefined) => {
  if (!formEl) return
  formEl.resetFields()
}
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
  width: 66% !important;
  margin: 0 auto;
  background-color: #fff !important;
  border-radius: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  padding: 1px;
}

.my-title {
  text-align: center;
  color: #1890ff !important;
  margin: 0 auto;
  font-size: 24px;
  font-weight: bold;
}

.job-title + .layout-container {
  margin-top: 30px !important;
}

.step-container {
  margin-bottom: 20px;
  height: 40vh;
  width: 150px;
}

.form-container,
.table-container {
  background-color: #fff;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  width: 700px;
}
</style>