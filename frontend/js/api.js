function getToken() {
  return window.localStorage.getItem('aitasker_token') || null
}

function setToken(token) {
  window.localStorage.setItem('aitasker_token', token)
}

function removeToken() {
  window.localStorage.removeItem('aitasker_token')
}

async function fetchWithAuth(path, options = {}) {
  const token = getToken()
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  const response = await fetch(getBackendUrl(path), {
    ...options,
    headers,
  })

  if (response.status === 401) {
    removeToken()
    window.location.href = 'index.html'
    throw new Error('Unauthorized')
  }

  const text = await response.text()
  let data

  try {
    data = text ? JSON.parse(text) : null
  } catch (err) {
    throw new Error('Invalid JSON response')
  }

  if (!response.ok) {
    const message = data?.detail || data?.message || response.statusText || 'Request failed'
    throw new Error(message)
  }

  return data
}

async function apiGet(path) {
  return fetchWithAuth(path, { method: 'GET' })
}

async function apiPost(path, body) {
  return fetchWithAuth(path, { method: 'POST', body: JSON.stringify(body) })
}

async function apiPut(path, body) {
  return fetchWithAuth(path, { method: 'PUT', body: JSON.stringify(body) })
}

async function apiDelete(path) {
  return fetchWithAuth(path, { method: 'DELETE' })
}
