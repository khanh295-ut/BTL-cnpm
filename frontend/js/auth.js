function setToken(token) {
  window.localStorage.setItem('aitasker_token', token)
}

function getToken() {
  return window.localStorage.getItem('aitasker_token') || null
}

function logoutUser() {
  removeToken()
  window.location.href = 'index.html'
}

function removeToken() {
  window.localStorage.removeItem('aitasker_token')
}

function attachLogoutLinks() {
  const logoutLinks = document.querySelectorAll('#logout-link')
  logoutLinks.forEach(link => {
    link.addEventListener('click', async (event) => {
      event.preventDefault()
      try {
        await apiPost('/auth/logout', {})
      } catch (err) {
        // ignore logout errors
      }
      logoutUser()
    })
  })
}

function ensureAuthenticated() {
  const token = getToken()
  if (!token) {
    window.location.href = 'index.html'
  }
}
