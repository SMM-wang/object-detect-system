export const ROLES = {
  USER: 'user',
  ADMIN: 'admin',
  MAINTAINER: 'maintainer'
}

export const ROLE_LABELS = {
  [ROLES.USER]: '普通用户',
  [ROLES.ADMIN]: '管理员',
  [ROLES.MAINTAINER]: '系统维护人员'
}

export const ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'mp4']
export const IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png']
export const VIDEO_EXTENSIONS = ['mp4']
export const MAX_FILE_SIZE = 500 * 1024 * 1024
export const MAX_BATCH_COUNT = 50

export const DETECT_STATUS = {
  SUCCESS: 'success',
  FAILED: 'failed',
  RUNNING: 'running',
  PENDING: 'pending'
}

export const STATUS_LABELS = {
  [DETECT_STATUS.SUCCESS]: '成功',
  [DETECT_STATUS.FAILED]: '失败',
  [DETECT_STATUS.RUNNING]: '处理中',
  [DETECT_STATUS.PENDING]: '等待中'
}

export const STATUS_TAG_TYPES = {
  [DETECT_STATUS.SUCCESS]: 'success',
  [DETECT_STATUS.FAILED]: 'danger',
  [DETECT_STATUS.RUNNING]: 'primary',
  [DETECT_STATUS.PENDING]: 'info'
}
