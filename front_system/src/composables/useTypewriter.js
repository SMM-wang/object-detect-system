import { onBeforeUnmount, ref, watch } from 'vue'

export function useTypewriter(source, speed = 28) {
  const displayText = ref('')
  let timer = null

  function stop() {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  function start(text = '') {
    stop()
    displayText.value = ''
    let index = 0

    if (!text) return

    timer = setInterval(() => {
      displayText.value += text[index]
      index += 1
      if (index >= text.length) stop()
    }, speed)
  }

  watch(source, (text) => start(text), { immediate: true })
  onBeforeUnmount(stop)

  return { displayText, restart: start }
}
