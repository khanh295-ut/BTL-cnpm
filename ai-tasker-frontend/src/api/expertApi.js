import axiosClient from "./axiosClient";

const expertApi = {
  // =========================
  // GET ALL
  // =========================
  getAll: (params) =>
    axiosClient.get("/experts", { params }),

  // =========================
  // GET BY ID
  // =========================
  getById: (id) =>
    axiosClient.get(`/experts/${id}`),

  // =========================
  // CREATE
  // =========================
  create: (data) =>
    axiosClient.post("/experts", data),

  // =========================
  // UPDATE
  // =========================
  update: (id, data) =>
    axiosClient.put(`/experts/${id}`, data),

  // =========================
  // DELETE
  // =========================
  delete: (id) =>
    axiosClient.delete(`/experts/${id}`),
};

export default expertApi;