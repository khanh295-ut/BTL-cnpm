import axiosClient from "./axiosClient";


const aiServiceApi = {
  // ======================================================
  // ADMIN / INTERNAL LIST
  // GET /api/ai-services
  // ======================================================

  getAll() {
    return axiosClient.get(
      "/ai-services"
    );
  },


  // ======================================================
  // GET BY ID
  // GET /api/ai-services/{service_id}
  // ======================================================

  getById(serviceId) {
    return axiosClient.get(
      `/ai-services/${serviceId}`
    );
  },


  // ======================================================
  // GET BY SLUG - INTERNAL
  // GET /api/ai-services/slug/{slug}
  // ======================================================

  getBySlug(slug) {
    return axiosClient.get(
      `/ai-services/slug/${encodeURIComponent(slug)}`
    );
  },


  // ======================================================
  // GET BY EXPERT
  // GET /api/ai-services/expert/{expert_id}
  // ======================================================

  getByExpert(expertId) {
    return axiosClient.get(
      `/ai-services/expert/${expertId}`
    );
  },


  // ======================================================
  // GET BY CATEGORY
  // GET /api/ai-services/category/{category_id}
  // ======================================================

  getByCategory(categoryId) {
    return axiosClient.get(
      `/ai-services/category/${categoryId}`
    );
  },


  // ======================================================
  // MARKETPLACE SEARCH
  // GET /api/ai-services/marketplace
  // ======================================================

  searchMarketplace(params = {}) {
    return axiosClient.get(
      "/ai-services/marketplace",
      {
        params,
      }
    );
  },


  // ======================================================
  // MARKETPLACE DETAIL BY SLUG
  // GET /api/ai-services/marketplace/{slug}
  // ======================================================

  getMarketplaceDetail(
    slug,
    increaseView = true
  ) {
    return axiosClient.get(
      `/ai-services/marketplace/${encodeURIComponent(slug)}`,
      {
        params: {
          increase_view: increaseView,
        },
      }
    );
  },


  // ======================================================
  // CREATE SERVICE
  // POST /api/ai-services
  // ======================================================

  create(data) {
    return axiosClient.post(
      "/ai-services",
      data
    );
  },


  // ======================================================
  // UPDATE SERVICE
  // PUT /api/ai-services/{service_id}
  // ======================================================

  update(
    serviceId,
    data
  ) {
    return axiosClient.put(
      `/ai-services/${serviceId}`,
      data
    );
  },


  // ======================================================
  // SUBMIT FOR REVIEW
  // PATCH /api/ai-services/{service_id}/submit
  // ======================================================

  submitForReview(serviceId) {
    return axiosClient.patch(
      `/ai-services/${serviceId}/submit`
    );
  },


  // ======================================================
  // UPDATE STATUS
  // PATCH /api/ai-services/{service_id}/status
  // ======================================================

  updateStatus(
    serviceId,
    data
  ) {
    return axiosClient.patch(
      `/ai-services/${serviceId}/status`,
      data
    );
  },


  // ======================================================
  // UPDATE FEATURED
  // PATCH /api/ai-services/{service_id}/featured
  // ======================================================

  updateFeatured(
    serviceId,
    isFeatured
  ) {
    return axiosClient.patch(
      `/ai-services/${serviceId}/featured`,
      {
        is_featured: Boolean(
          isFeatured
        ),
      }
    );
  },


  // ======================================================
  // INCREMENT VIEW
  // PATCH /api/ai-services/{service_id}/view
  // ======================================================

  incrementView(serviceId) {
    return axiosClient.patch(
      `/ai-services/${serviceId}/view`
    );
  },


  // ======================================================
  // INCREMENT ORDER COUNT
  //
  // Tạm thời dùng endpoint hiện tại.
  // Sau này nên để ServiceOrder tự tăng order_count.
  // ======================================================

  incrementOrderCount(serviceId) {
    return axiosClient.patch(
      `/ai-services/${serviceId}/order`
    );
  },


  // ======================================================
  // DELETE SERVICE
  // DELETE /api/ai-services/{service_id}
  // ======================================================

  delete(serviceId) {
    return axiosClient.delete(
      `/ai-services/${serviceId}`
    );
  },
};


export default aiServiceApi;