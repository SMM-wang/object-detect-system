const PALETTE = [
  '#2f6fed',
  '#18a058',
  '#f0a020',
  '#d03050',
  '#8a5cf6',
  '#00a2ae',
  '#f06b42',
  '#7cb342',
  '#c2185b',
  '#0097a7'
]

const CLASS_COLOR_INDEX = {
  pedestrian: 0,
  people: 1,
  bicycle: 2,
  car: 3,
  van: 4,
  truck: 5,
  tricycle: 6,
  'awning-tricycle': 7,
  bus: 8,
  motor: 9
}

export function getClassColor(className = '') {
  const index = CLASS_COLOR_INDEX[className]
  if (index !== undefined) return PALETTE[index % PALETTE.length]
  const seed = [...className].reduce((sum, char) => sum + char.charCodeAt(0), 0)
  return PALETTE[seed % PALETTE.length]
}

export function normalizeBbox(bbox) {
  if (Array.isArray(bbox)) {
    const [x, y, width, height] = bbox
    return { x, y, width, height }
  }

  if (!bbox) return { x: 0, y: 0, width: 0, height: 0 }

  const x = bbox.x ?? bbox.left ?? bbox.x1 ?? 0
  const y = bbox.y ?? bbox.top ?? bbox.y1 ?? 0
  const width = bbox.width ?? bbox.w ?? ((bbox.x2 ?? x) - x)
  const height = bbox.height ?? bbox.h ?? ((bbox.y2 ?? y) - y)
  return { x, y, width, height }
}

export function drawDetectionObjects(ctx, objects, scaleX, scaleY, showLabels = true) {
  objects.forEach((item) => {
    const { x, y, width, height } = normalizeBbox(item.bbox)
    const color = getClassColor(item.className)
    const left = x * scaleX
    const top = y * scaleY
    const boxWidth = width * scaleX
    const boxHeight = height * scaleY

    ctx.strokeStyle = color
    ctx.lineWidth = 2
    ctx.strokeRect(left, top, boxWidth, boxHeight)

    if (!showLabels) return

    const label = `${item.className || '目标'} ${Math.round((item.confidence || 0) * 100)}%`
    ctx.font = '12px sans-serif'
    const labelWidth = ctx.measureText(label).width + 12
    const labelTop = Math.max(0, top - 22)
    ctx.fillStyle = color
    ctx.fillRect(left, labelTop, labelWidth, 20)
    ctx.fillStyle = '#fff'
    ctx.fillText(label, left + 6, labelTop + 14)
  })
}
