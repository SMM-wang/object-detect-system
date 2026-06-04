import * as echarts from 'echarts'
import { nextTick, onBeforeUnmount, ref } from 'vue'

export function useECharts(containerRef) {
  const chart = ref(null)
  let resizeObserver = null

  async function init() {
    await nextTick()
    if (!containerRef.value || chart.value) return

    chart.value = echarts.init(containerRef.value)
    resizeObserver = new ResizeObserver(() => chart.value?.resize())
    resizeObserver.observe(containerRef.value)
  }

  async function setOptions(options) {
    await init()
    chart.value?.setOption(options || {}, true)
  }

  function resize() {
    chart.value?.resize()
  }

  onBeforeUnmount(() => {
    resizeObserver?.disconnect()
    chart.value?.dispose()
    chart.value = null
  })

  return { chart, init, setOptions, resize }
}
