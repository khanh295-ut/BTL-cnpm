import { getJson, postJson } from "./http.js";
import { showAlert } from "./alerts.js";

export function initDashboardPanel() {
  const usernameLabel = document.getElementById("usernameLabel");
  const emailLabel = document.getElementById("emailLabel");
  const roleLabel = document.getElementById("roleLabel");
  const adminPanel = document.getElementById("adminPanel");
  const adminNotice = document.getElementById("adminNotice");
  const userTableBody = document.getElementById("userTableBody");
  const logoutButton = document.getElementById("logoutButton");

  async function loadUsers() {
    const response = await fetch("/admin/users", {
      headers: { "Accept": "application/json" },
      credentials: "same-origin"
    });
    if (!response.ok) {
      adminNotice.textContent = "Không thể tải danh sách người dùng.";
      return;
    }

    const data = await response.json();
    userTableBody.innerHTML = data.users.map(user => `
      <tr>
        <td>${user.id}</td>
        <td>${user.username}</td>
        <td>${user.email}</td>
        <td>
          <select class="role-select" data-user-id="${user.id}">
            <option value="User" ${user.role === "User" ? "selected" : ""}>User</option>
            <option value="Admin" ${user.role === "Admin" ? "selected" : ""}>Admin</option>
          </select>
        </td>
        <td><button class="button button-secondary update-role" data-user-id="${user.id}">Cập nhật</button></td>
      </tr>`).join("");

    document.querySelectorAll(".update-role").forEach(button => {
      button.addEventListener("click", async () => {
        const userId = button.dataset.userId;
        const select = document.querySelector(`select[data-user-id='${userId}']`);
        const role = select.value;
        const result = await postJson(`/admin/users/${userId}/role`, { role });
        if (result.response.ok) {
          showAlert("alertBox", "Cập nhật vai trò thành công.", "success");
        } else {
          showAlert("alertBox", result.data.error || "Cập nhật thất bại.", "error");
        }
        renderDashboard();
      });
    });
  }

  async function renderDashboard() {
    const { response, data } = await getJson("/api/profile");
    if (!response.ok) {
      window.location.href = "/login";
      return;
    }

    usernameLabel.textContent = data.user.username;
    emailLabel.textContent = data.user.email;
    roleLabel.textContent = data.user.role;

    if (data.user.role === "Admin") {
      adminPanel.classList.remove("hidden");
      adminNotice.textContent = "Bạn đang ở chế độ Admin. Quản lý người dùng được hiển thị bên dưới.";
      loadUsers();
    } else {
      adminPanel.classList.add("hidden");
      adminNotice.textContent = "Chỉ Admin mới có thể xem nội dung này.";
    }
  }

  if (logoutButton) {
    logoutButton.addEventListener("click", async () => {
      await postJson("/logout", {});
      window.location.href = "/login";
    });
  }

  renderDashboard();
}
