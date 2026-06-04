export const TOKEN_KEY = 'front_system_token'
export const USER_KEY = 'front_system_user'

export function getStorageItem(key, fallback = null) {
  const value = localStorage.getItem(key)
  if (!value) return fallback

  try {
    return JSON.parse(value)
  } catch {
    return value
  }
}

export function setStorageItem(key, value) {
  if (value === undefined || value === null) {
    localStorage.removeItem(key)
    return
  }

  localStorage.setItem(key, JSON.stringify(value))
}

export function removeStorageItem(key) {
  localStorage.removeItem(key)
}
