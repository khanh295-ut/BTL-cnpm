const API_BASE_URL = 'http://127.0.0.1:5000/api'

function getBackendUrl(path) {
  return `${API_BASE_URL}${path}`
}
