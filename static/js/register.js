const registerForm = document.getElementById("registerForm");
if (registerForm) {
  registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = new FormData(registerForm);
    const username = formData.get("username").trim();
    const email = formData.get("email").trim();
    const password = formData.get("password");
    const confirmPassword = formData.get("confirm_password");

    if (!username || !email || !password || !confirmPassword) {
      showAlert("alertBox", "Vui lòng điền đầy đủ thông tin.", "error");
      return;
    }

    if (password !== confirmPassword) {
      showAlert("alertBox", "Mật khẩu xác nhận không khớp.", "error");
      return;
    }

    const { response, data } = await postJson("/register", { username, email, password });
    const status = response.ok ? "success" : "error";
    showAlert("alertBox", data.message || data.error, status);

    if (response.ok) {
      setTimeout(() => {
        window.location.href = "/login";
      }, 1000);
    }
  });
}
