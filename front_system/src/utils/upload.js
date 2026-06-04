import { ALLOWED_EXTENSIONS, IMAGE_EXTENSIONS, MAX_BATCH_COUNT, MAX_FILE_SIZE, VIDEO_EXTENSIONS } from '@/constants'

export function getFileExtension(file) {
  return file.name.split('.').pop()?.toLowerCase() || ''
}

export function getFileType(file) {
  const extension = getFileExtension(file)
  if (IMAGE_EXTENSIONS.includes(extension)) return 'image'
  if (VIDEO_EXTENSIONS.includes(extension)) return 'video'
  return 'unknown'
}

export function formatFileSize(size) {
  if (size >= 1024 * 1024) return `${(size / 1024 / 1024).toFixed(1)} MB`
  if (size >= 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${size} B`
}

export function validateFile(file) {
  const extension = getFileExtension(file)
  if (!ALLOWED_EXTENSIONS.includes(extension)) {
    return { valid: false, message: `${file.name} 文件格式不支持，仅支持 jpg、jpeg、png、mp4` }
  }

  if (file.size > MAX_FILE_SIZE) {
    return { valid: false, message: `${file.name} 超过 ${formatFileSize(MAX_FILE_SIZE)} 限制` }
  }

  return { valid: true, type: getFileType(file) }
}

export function validateFiles(files) {
  const errors = []
  const validFiles = []

  if (files.length > MAX_BATCH_COUNT) {
    errors.push(`单次最多选择 ${MAX_BATCH_COUNT} 个文件`)
  }

  files.slice(0, MAX_BATCH_COUNT).forEach((file) => {
    const result = validateFile(file)
    if (result.valid) {
      validFiles.push(file)
    } else {
      errors.push(result.message)
    }
  })

  return { validFiles, errors }
}
