document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('forgot-password-form')
  const errorEl = document.getElementById('forgot-password-error')
  const successEl = document.getElementById('forgot-password-success')

  if (!form) return

  form.addEventListener('submit', async (event) => {
    event.preventDefault()
    errorEl.classList.add('hidden')
    successEl.classList.add('hidden')

    const email = document.getElementById('forgot-email').value.trim()
    if (!email) {
      showError(errorEl, 'Please enter your email.')
      return
    }

    try {
      const result = await apiPost('/auth/forgot-password', { email })
      if (result.reset_token) {
        window.location.href = `reset-password.html?token=${encodeURIComponent(result.reset_token)}`
        return
      }
      showSuccess(successEl, result.message || 'If the email exists, the reset token has been generated.')
      form.reset()
    } catch (err) {
      showError(errorEl, parseError(err, 'Unable to process request.'))
    }
  })
})
