const forgotForm = document.getElementById("forgotForm");
if (forgotForm) {
  forgotForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = new FormData(forgotForm);
    const email = formData.get("email").trim();

    if (!email) {
      showAlert("alertBox", "Vui lòng nhập email.", "error");
      return;
    }

    const { response, data } = await postJson("/forgot-password", { email });
    showAlert("alertBox", data.message || data.error, response.ok ? "success" : "error");

    if (response.ok && data.reset_url) {
      const link = document.createElement("div");
      link.className = "alert alert-success";
      link.innerHTML = `Đường dẫn reset: <a href="${data.reset_url}">${data.reset_url}</a>`;
      document.getElementById("alertBox").appendChild(link);
    }
  });
}
