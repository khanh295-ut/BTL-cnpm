import { getJson, postJson } from "./http.js";
import { showAlert } from "./alerts.js";

export function initProfilePanel() {
  const profileForm = document.getElementById("profileForm");
  const passwordForm = document.getElementById("passwordForm");

  async function loadProfile() {
    const { response, data } = await getJson("/api/profile");
    if (!response.ok) {
      window.location.href = "/login";
      return;
    }

    profileForm.username.value = data.user.username;
    profileForm.full_name.value = data.user.full_name || "";
    profileForm.email.value = data.user.email;
    profileForm.bio.value = data.user.bio || "";
  }

  if (profileForm) {
    profileForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const payload = {
        full_name: profileForm.full_name.value.trim(),
        email: profileForm.email.value.trim(),
        bio: profileForm.bio.value.trim()
      };

      const { response, data } = await postJson("/profile/update", payload);
      showAlert("alertBox", data.message || data.error, response.ok ? "success" : "error");
      if (response.ok) {
        loadProfile();
      }
    });
  }

  if (passwordForm) {
    passwordForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const payload = {
        current_password: passwordForm.current_password.value,
        new_password: passwordForm.new_password.value
      };
      const { response, data } = await postJson("/profile/change-password", payload);
      showAlert("alertBox", data.message || data.error, response.ok ? "success" : "error");
      if (response.ok) {
        passwordForm.reset();
      }
    });
  }

  loadProfile();
}
