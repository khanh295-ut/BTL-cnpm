document.addEventListener('DOMContentLoaded', async () => {
  ensureAuthenticated()
  attachLogoutLinks()
  await loadProfileData()
})
