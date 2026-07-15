import axiosClient from "./axiosClient";

const enterpriseApi = {

  // ==========================
  // Lấy toàn bộ doanh nghiệp
  // ==========================
  getAll: (params) =>
    axiosClient.get("/enterprises", {
      params,
    }),

  // ==========================
  // Lấy doanh nghiệp theo ID
  // ==========================
  getById: (id) =>
    axiosClient.get(`/enterprises/${id}`),

  // ==========================
  // Thêm doanh nghiệp
  // ==========================
  create: (data) =>
    axiosClient.post("/enterprises", data),

  // ==========================
  // Cập nhật doanh nghiệp
  // ==========================
  update: (id, data) =>
    axiosClient.put(`/enterprises/${id}`, data),

  // ==========================
  // Xóa doanh nghiệp
  // ==========================
  delete: (id) =>
    axiosClient.delete(`/enterprises/${id}`),

};

export default enterpriseApi;