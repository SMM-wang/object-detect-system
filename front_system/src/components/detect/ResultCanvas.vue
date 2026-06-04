<template>
  <div ref="wrapRef" class="result-canvas-wrap">
    <img v-if="imageUrl" ref="imageRef" :src="imageUrl" alt="检测结果" @load="draw" />
    <div v-else class="canvas-placeholder">请选择图片并完成检测后查看标注结果</div>
    <canvas ref="canvasRef" />
    
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { drawDetectionObjects } from '@/utils/canvas'

const props = defineProps({
  imageUrl: {
    type: String,
    default: ''
  },
  objects: {
    type: Array,
    default: () => []
  },
  imageWidth: {
    type: Number,
    default: 0
  },
  imageHeight: {
    type: Number,
    default: 0
  },
  showLabels: {
    type: Boolean,
    default: true
  }
})

const wrapRef = ref(null)
const imageRef = ref(null)
const canvasRef = ref(null)
let resizeObserver = null

function clearCanvas() {
  const canvas = canvasRef.value
  const context = canvas?.getContext('2d')
  if (canvas && context) context.clearRect(0, 0, canvas.width, canvas.height)
}

async function draw() {
  await nextTick()
  const image = imageRef.value
  const canvas = canvasRef.value
  if (!image || !canvas) return clearCanvas()

  const rect = image.getBoundingClientRect()
  const dpr = window.devicePixelRatio || 1
  canvas.style.width = `${rect.width}px`
  canvas.style.height = `${rect.height}px`
  canvas.width = rect.width * dpr
  canvas.height = rect.height * dpr

  const context = canvas.getContext('2d')
  context.setTransform(dpr, 0, 0, dpr, 0, 0)
  context.clearRect(0, 0, rect.width, rect.height)

  const naturalWidth = props.imageWidth || image.naturalWidth
  const naturalHeight = props.imageHeight || image.naturalHeight
  drawDetectionObjects(context, props.objects, rect.width / naturalWidth, rect.height / naturalHeight, props.showLabels)
}

watch(() => [props.imageUrl, props.objects, props.imageWidth, props.imageHeight, props.showLabels], draw, { deep: true })

watch(wrapRef, (element) => {
  resizeObserver?.disconnect()
  if (!element) return
  resizeObserver = new ResizeObserver(draw)
  resizeObserver.observe(element)
})

onBeforeUnmount(() => resizeObserver?.disconnect())

defineExpose({ draw })
</script>

<style scoped>
.result-canvas-wrap {
  position: relative;
  display: flex;
  min-height: 360px;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: #0f172a;
  border-radius: 12px;
}

.result-canvas-wrap img {
  display: block;
  max-width: 100%;
  max-height: 620px;
  object-fit: contain;
}

.result-canvas-wrap canvas {
  position: absolute;
  pointer-events: none;
}

.canvas-placeholder,
.empty-result {
  color: #cbd5e1;
}

.empty-result {
  position: absolute;
  padding: 8px 14px;
  background: rgb(15 23 42 / 75%);
  border-radius: 999px;
}
</style>
