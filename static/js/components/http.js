export async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json"
    },
    body: JSON.stringify(payload),
    credentials: "same-origin"
  });
  const data = await response.json().catch(() => ({ error: "Lỗi kết nối." }));
  return { response, data };
}

export async function getJson(url) {
  const response = await fetch(url, {
    method: "GET",
    headers: {
      "Accept": "application/json"
    },
    credentials: "same-origin"
  });
  const data = await response.json().catch(() => ({ error: "Lỗi kết nối." }));
  return { response, data };
}
