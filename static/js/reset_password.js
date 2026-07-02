import { postJson } from "/static/js/components/http.js";
import { showAlert } from "/static/js/components/alerts.js";

const resetForm = document.getElementById("resetForm");
if (resetForm) {
  resetForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = new FormData(resetForm);
    const password = formData.get("password");
    const confirmPassword = formData.get("confirm_password");

    if (!password || !confirmPassword) {
      showAlert("alertBox", "Vui lòng nhập đầy đủ mật khẩu.", "error");
      return;
    }

    if (password !== confirmPassword) {
      showAlert("alertBox", "Mật khẩu xác nhận không khớp.", "error");
      return;
    }

    const { response, data } = await postJson(`/reset-password/${window.resetToken}`, { password, confirm_password: confirmPassword });
    showAlert("alertBox", data.message || data.error, response.ok ? "success" : "error");
    if (response.ok) {
      setTimeout(() => {
        window.location.href = "/login";
      }, 900);
    }
  });
}
