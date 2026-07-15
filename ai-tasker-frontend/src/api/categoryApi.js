import axiosClient from "./axiosClient";

const categoryApi = {

  // ==================================
  // Lấy danh sách danh mục
  // ==================================
  getAll: (params) =>
    axiosClient.get("/categories", {
      params,
    }),

  // ==================================
  // Lấy danh mục theo ID
  // ==================================
  getById: (id) =>
    axiosClient.get(`/categories/${id}`),

  // ==================================
  // Thêm danh mục
  // ==================================
  create: (data) =>
    axiosClient.post("/categories", data),

  // ==================================
  // Cập nhật danh mục
  // ==================================
  update: (id, data) =>
    axiosClient.put(`/categories/${id}`, data),

  // ==================================
  // Xóa danh mục
  // ==================================
  delete: (id) =>
    axiosClient.delete(`/categories/${id}`),

};

export default categoryApi;