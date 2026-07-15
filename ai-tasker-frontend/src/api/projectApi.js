import axiosClient from "./axiosClient";

const projectApi = {
  // =========================
  // GET ALL
  // =========================
  getAll: (params) =>
    axiosClient.get("/projects", { params }),

  // =========================
  // GET BY ID
  // =========================
  getById: (id) =>
    axiosClient.get(`/projects/${id}`),

  // =========================
  // CREATE
  // =========================
  create: (data) =>
    axiosClient.post("/projects", data),

  // =========================
  // UPDATE
  // =========================
  update: (id, data) =>
    axiosClient.put(`/projects/${id}`, data),

  // =========================
  // DELETE
  // =========================
  delete: (id) =>
    axiosClient.delete(`/projects/${id}`),
};

export default projectApi;