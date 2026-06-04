export function hasRole(userRole, allowedRoles = []) {
  if (!allowedRoles.length) return true
  return allowedRoles.includes(userRole)
}

export function filterMenuRoutes(routes, role) {
  return routes
    .filter((route) => route.meta?.title && !route.meta?.hidden && hasRole(role, route.meta?.roles || []))
    .map((route) => ({
      path: route.path,
      title: route.meta.title,
      icon: route.meta.icon
    }))
}
