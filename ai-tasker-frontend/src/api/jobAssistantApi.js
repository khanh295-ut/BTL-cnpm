import axiosClient from "./axiosClient";


const jobAssistantApi = {
  // ======================================================
  // HEALTH
  // GET /api/job-assistant/health
  // ======================================================

  getHealth() {
    return axiosClient.get(
      "/job-assistant/health"
    );
  },


  // ======================================================
  // GENERATE FULL PROJECT SUGGESTION
  // POST /api/job-assistant/generate
  // ======================================================

  generate(data) {
    return axiosClient.post(
      "/job-assistant/generate",
      data
    );
  },


  // ======================================================
  // QUICK GENERATE
  // POST /api/job-assistant/quick-generate?idea=...
  // ======================================================

  quickGenerate(idea) {
    return axiosClient.post(
      "/job-assistant/quick-generate",
      null,
      {
        params: {
          idea,
        },
      }
    );
  },


  // ======================================================
  // GET TEMPLATE
  // GET /api/job-assistant/template
  // ======================================================

  getTemplate() {
    return axiosClient.get(
      "/job-assistant/template"
    );
  },


  // ======================================================
  // GET SUPPORTED LANGUAGES
  // GET /api/job-assistant/languages
  // ======================================================

  getLanguages() {
    return axiosClient.get(
      "/job-assistant/languages"
    );
  },


  // ======================================================
  // GET DETAIL LEVELS
  // GET /api/job-assistant/detail-levels
  // ======================================================

  getDetailLevels() {
    return axiosClient.get(
      "/job-assistant/detail-levels"
    );
  },
};


export default jobAssistantApi;