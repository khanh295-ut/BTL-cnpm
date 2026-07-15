import axiosClient from "./axiosClient";

const proposalApi = {
  // ===========================
  // Lấy toàn bộ Proposal
  // GET /api/proposals
  // ===========================
  getAll: (params) =>
    axiosClient.get("/proposals", { params }),

  // ===========================
  // Lấy Proposal theo ID
  // GET /api/proposals/{id}
  // ===========================
  getById: (id) =>
    axiosClient.get(`/proposals/${id}`),

  // ===========================
  // Tạo Proposal mới
  // POST /api/proposals
  // ===========================
  create: (data) =>
    axiosClient.post("/proposals", data),

  // ===========================
  // Cập nhật Proposal
  // PUT /api/proposals/{id}
  // ===========================
  update: (id, data) =>
    axiosClient.put(`/proposals/${id}`, data),

  // ===========================
  // Cập nhật trạng thái
  // PATCH /api/proposals/{id}/status
  // ===========================
  updateStatus: (id, status) =>
    axiosClient.patch(`/proposals/${id}/status`, {
      status,
    }),

  // ===========================
  // Xóa Proposal
  // DELETE /api/proposals/{id}
  // ===========================
  delete: (id) =>
    axiosClient.delete(`/proposals/${id}`),
};

export default proposalApi;