export function showAlert(targetId, message, type = "success") {
  const box = document.getElementById(targetId);
  if (!box) return;
  const className = type === "success" ? "alert alert-success" : "alert alert-danger";
  box.innerHTML = `<div class="${className}">${message}</div>`;
}
