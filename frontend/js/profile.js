async function loadProfileData() {
  try {
    const user = await apiGet('/users/me')
    const usernameEl = document.getElementById('profile-username')
    const emailEl = document.getElementById('profile-email')
    const fullNameEl = document.getElementById('profile-fullname')
    const bioEl = document.getElementById('profile-bio')

    if (usernameEl) usernameEl.textContent = user.username || ''
    if (emailEl) emailEl.textContent = user.email || ''
    if (fullNameEl) fullNameEl.textContent = user.full_name || '—'
    if (bioEl) bioEl.textContent = user.bio || '—'

    const editFullName = document.getElementById('edit-fullname')
    const editEmail = document.getElementById('edit-email')
    const editBio = document.getElementById('edit-bio')
    if (editFullName) editFullName.value = user.full_name || ''
    if (editEmail) editEmail.value = user.email || ''
    if (editBio) editBio.value = user.bio || ''
    const dashboardWelcome = document.getElementById('dashboard-welcome')
    if (dashboardWelcome) dashboardWelcome.textContent = `Hello, ${user.full_name || user.username}!` 

  } catch (err) {
    showPageError(parseError(err, 'Unable to load profile.'))
  }
}

function showPageError(message) {
  const errorEl = document.querySelector('.toast-error')
  if (errorEl) {
    errorEl.textContent = message
    errorEl.classList.remove('hidden')
  }
}

function initEditProfile() {
  const form = document.getElementById('edit-profile-form')
  const errorEl = document.getElementById('edit-profile-error')
  const successEl = document.getElementById('edit-profile-success')

  if (!form) return

  form.addEventListener('submit', async (event) => {
    event.preventDefault()
    errorEl.classList.add('hidden')
    successEl.classList.add('hidden')

    const full_name = document.getElementById('edit-fullname').value.trim()
    const email = document.getElementById('edit-email').value.trim()
    const bio = document.getElementById('edit-bio').value.trim()

    if (!email) {
      showError(errorEl, 'Email is required.')
      return
    }

    try {
      const user = await apiPut('/users/me', { full_name, email, bio })
      showSuccess(successEl, 'Profile updated successfully.')
      setTimeout(() => window.location.href = 'profile.html', 1200)
    } catch (err) {
      showError(errorEl, parseError(err, 'Profile update failed.'))
    }
  })
}

function initChangePassword() {
  const form = document.getElementById('change-password-form')
  const errorEl = document.getElementById('change-password-error')
  const successEl = document.getElementById('change-password-success')

  if (!form) return

  form.addEventListener('submit', async (event) => {
    event.preventDefault()
    errorEl.classList.add('hidden')
    successEl.classList.add('hidden')

    const current_password = document.getElementById('current-password').value
    const new_password = document.getElementById('new-password').value

    if (!current_password || !new_password) {
      showError(errorEl, 'Both current and new password are required.')
      return
    }
    if (new_password.length < 6) {
      showError(errorEl, 'New password must be at least 6 characters.')
      return
    }

    try {
      await apiPut('/users/change-password', { current_password, new_password })
      showSuccess(successEl, 'Password changed successfully.')
      setTimeout(() => window.location.href = 'profile.html', 1200)
    } catch (err) {
      showError(errorEl, parseError(err, 'Password update failed.'))
    }
  })
}
