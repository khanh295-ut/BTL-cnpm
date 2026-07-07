import { postJson } from "/static/js/components/http.js";
import { showAlert } from "/static/js/components/alerts.js";

const loginForm = document.getElementById("loginForm");
if (loginForm) {
  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = new FormData(loginForm);
    const payload = {
      login: formData.get("login"),
      password: formData.get("password")
    };

    const { response, data } = await postJson("/login", payload);
    const status = response.ok ? "success" : "error";
    showAlert("alertBox", data.message || data.error, status);

    if (response.ok) {
      setTimeout(() => {
        window.location.href = "/dashboard";
      }, 900);
    }
  });
}
