function parseError(error, fallback) {
  if (!error) return fallback
  if (typeof error === 'string') return error
  if (error.message) return error.message
  return fallback
}

function showError(target, message) {
  if (!target) return
  target.textContent = message
  target.classList.remove('hidden')
}

function showSuccess(target, message) {
  if (!target) return
  target.textContent = message
  target.classList.remove('hidden')
}
