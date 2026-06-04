<template>
  <div>
    <el-upload
      drag
      multiple
      :auto-upload="false"
      :file-list="fileList"
      accept=".jpg,.jpeg,.png,.mp4"
      :on-change="handleChange"
      :on-remove="handleRemove"
    >
      <el-icon class="upload-icon"><UploadFilled /></el-icon>
      <div class="el-upload__text">拖拽文件到此处，或 <em>点击选择</em></div>
      <template #tip>
        <div class="el-upload__tip">支持 jpg、jpeg、png、mp4，单文件最大 500 MB，批量最多 50 个文件。</div>
      </template>
    </el-upload>

    <div class="dataset-actions">
      <el-button @click="openDirectoryPicker">选择数据集文件夹</el-button>
      <span>浏览器支持时可按文件夹批量导入。</span>
      <input ref="directoryInputRef" class="directory-input" type="file" multiple webkitdirectory directory @change="handleDirectoryChange" />
    </div>

    <el-alert v-if="errors.length" class="upload-errors" type="warning" show-icon :closable="false">
      <template #title>
        <div v-for="error in errors" :key="error">{{ error }}</div>
      </template>
    </el-alert>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { validateFiles } from '@/utils/upload'

const emit = defineEmits(['change'])
const fileList = ref([])
const errors = ref([])
const directoryInputRef = ref(null)

function emitValidatedFiles(rawFiles) {
  const result = validateFiles(rawFiles)
  errors.value = result.errors
  emit('change', result.validFiles)
  return result.validFiles
}

function syncFiles(list) {
  const rawFiles = list.map((item) => item.raw).filter(Boolean)
  const validFiles = emitValidatedFiles(rawFiles)
  fileList.value = list.filter((item) => validFiles.includes(item.raw))
}

function handleChange(_, list) {
  syncFiles(list)
}

function handleRemove(_, list) {
  syncFiles(list)
}

function openDirectoryPicker() {
  directoryInputRef.value?.click()
}

function handleDirectoryChange(event) {
  const rawFiles = Array.from(event.target.files || [])
  const validFiles = emitValidatedFiles(rawFiles)
  fileList.value = validFiles.map((file) => ({ name: file.webkitRelativePath || file.name, raw: file }))
  event.target.value = ''
}
</script>

<style scoped>
.upload-icon {
  color: var(--app-sidebar-active);
  font-size: 48px;
}

.dataset-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 12px;
  color: var(--app-muted);
  font-size: 13px;
}

.directory-input {
  display: none;
}

.upload-errors {
  margin-top: 12px;
}
</style>
