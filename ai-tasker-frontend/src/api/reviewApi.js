import axiosClient from "./axiosClient";

const reviewApi = {
  // ==========================
  // GET ALL
  // ==========================
  getAll: (params) =>
    axiosClient.get("/reviews/", { params }),

  // ==========================
  // GET BY ID
  // ==========================
  getById: (id) =>
    axiosClient.get(`/reviews/${id}`),

  // ==========================
  // CREATE
  // ==========================
  create: (data) =>
    axiosClient.post("/reviews/", data),

  // ==========================
  // UPDATE
  // ==========================
  update: (id, data) =>
    axiosClient.put(`/reviews/${id}`, data),

  // ==========================
  // DELETE
  // ==========================
  delete: (id) =>
    axiosClient.delete(`/reviews/${id}`),
};

export default reviewApi;