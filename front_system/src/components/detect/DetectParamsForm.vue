<template>
  <el-form label-position="top" class="params-form">
    <el-form-item label="模型版本">
      <el-select v-model="localParams.modelVersion" class="full-width" @change="emitChange">
        <el-option v-for="item in modelOptions" :key="item.value" :label="item.label" :value="item.value" />
      </el-select>
    </el-form-item>

    <el-form-item label="置信度阈值">
      <el-slider v-model="localParams.confidence" :min="0.01" :max="1" :step="0.01" show-input @change="emitChange" />
    </el-form-item>

    <el-form-item label="IoU 阈值">
      <el-slider v-model="localParams.iou" :min="0.01" :max="1" :step="0.01" show-input @change="emitChange" />
    </el-form-item>

    <el-form-item label="视频抽帧间隔">
      <el-input-number v-model="localParams.frameInterval" :min="1" :max="120" class="full-width" @change="emitChange" />
    </el-form-item>
  </el-form>
</template>

<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  modelOptions: {
    type: Array,
    default: () => []
  }
})
const emit = defineEmits(['update:modelValue'])

const localParams = reactive({ ...props.modelValue })

watch(
  () => props.modelValue,
  (value) => Object.assign(localParams, value),
  { deep: true }
)

watch(localParams, emitChange, { deep: true })

function emitChange() {
  emit('update:modelValue', { ...localParams })
}
</script>

<style scoped>
.full-width {
  width: 100%;
}
</style>
