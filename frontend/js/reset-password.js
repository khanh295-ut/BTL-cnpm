document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('reset-password-form')
  const errorEl = document.getElementById('reset-password-error')
  const successEl = document.getElementById('reset-password-success')

  if (!form) return

  const params = new URLSearchParams(window.location.search)
  const token = params.get('token')

  if (!token) {
    showError(errorEl, 'Missing reset token.')
    return
  }

  form.addEventListener('submit', async (event) => {
    event.preventDefault()
    errorEl.classList.add('hidden')
    successEl.classList.add('hidden')

    const new_password = document.getElementById('reset-password').value
    const confirm_password = document.getElementById('reset-confirm-password').value

    if (!new_password || !confirm_password) {
      showError(errorEl, 'Both password fields are required.')
      return
    }

    if (new_password.length < 8) {
      showError(errorEl, 'Password must be at least 8 characters.')
      return
    }

    if (new_password !== confirm_password) {
      showError(errorEl, 'Passwords do not match.')
      return
    }

    try {
      const result = await apiPost('/auth/reset-password', { token, new_password, confirm_password })
      showSuccess(successEl, result.message || 'Password reset successfully.')
      setTimeout(() => {
        window.location.href = 'index.html'
      }, 1200)
    } catch (err) {
      showError(errorEl, parseError(err, 'Unable to reset password.'))
    }
  })
})
