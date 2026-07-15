import axiosClient from "./axiosClient";


const serviceOrderApi = {
  // ======================================================
  // GET ALL
  // GET /api/service-orders
  // ======================================================

  getAll(params = {}) {
    return axiosClient.get(
      "/service-orders",
      {
        params,
      }
    );
  },


  // ======================================================
  // GET SUMMARY
  // GET /api/service-orders/summary
  // ======================================================

  getSummary() {
    return axiosClient.get(
      "/service-orders/summary"
    );
  },


  // ======================================================
  // GET BY ID
  // GET /api/service-orders/{order_id}
  // ======================================================

  getById(orderId) {
    return axiosClient.get(
      `/service-orders/${orderId}`
    );
  },


  // ======================================================
  // GET BY ENTERPRISE
  // GET /api/service-orders/enterprise/{enterprise_id}
  // ======================================================

  getByEnterprise(enterpriseId) {
    return axiosClient.get(
      `/service-orders/enterprise/${enterpriseId}`
    );
  },


  // ======================================================
  // GET BY EXPERT
  // GET /api/service-orders/expert/{expert_id}
  // ======================================================

  getByExpert(expertId) {
    return axiosClient.get(
      `/service-orders/expert/${expertId}`
    );
  },


  // ======================================================
  // GET BY AI SERVICE
  // GET /api/service-orders/service/{service_id}
  // ======================================================

  getByService(serviceId) {
    return axiosClient.get(
      `/service-orders/service/${serviceId}`
    );
  },


  // ======================================================
  // GET BY STATUS
  // GET /api/service-orders/status/{status}
  // ======================================================

  getByStatus(statusValue) {
    return axiosClient.get(
      `/service-orders/status/${encodeURIComponent(
        statusValue
      )}`
    );
  },


  // ======================================================
  // CREATE ORDER
  // POST /api/service-orders
  //
  // Payload:
  // {
  //   service_id: UUID,
  //   enterprise_id: UUID,
  //   requirements: string | null,
  //   note: string | null
  // }
  // ======================================================

  create(data) {
    return axiosClient.post(
      "/service-orders",
      data
    );
  },


  // ======================================================
  // UPDATE ORDER
  // PUT /api/service-orders/{order_id}
  //
  // Chỉ áp dụng khi status = PENDING.
  // ======================================================

  update(
    orderId,
    data
  ) {
    return axiosClient.put(
      `/service-orders/${orderId}`,
      data
    );
  },


  // ======================================================
  // CONFIRM ORDER
  // PATCH /api/service-orders/{order_id}/confirm
  //
  // Payload:
  // {
  //   payment_id: UUID | null,
  //   payer_wallet_id: UUID | null,
  //   note: string | null
  // }
  // ======================================================

  confirm(
    orderId,
    data = {}
  ) {
    return axiosClient.patch(
      `/service-orders/${orderId}/confirm`,
      {
        payment_id: data.payment_id ?? null,
        payer_wallet_id:
          data.payer_wallet_id ?? null,
        note: data.note ?? null,
      }
    );
  },


  // ======================================================
  // START ORDER
  // PATCH /api/service-orders/{order_id}/start
  //
  // CONFIRMED -> IN_PROGRESS
  // ======================================================

  start(
    orderId,
    data = {}
  ) {
    return axiosClient.patch(
      `/service-orders/${orderId}/start`,
      {
        note: data.note ?? null,
      }
    );
  },


  // ======================================================
  // DELIVER ORDER
  // PATCH /api/service-orders/{order_id}/deliver
  //
  // Payload:
  // {
  //   deliverable_id: UUID | null,
  //   note: string | null
  // }
  // ======================================================

  deliver(
    orderId,
    data = {}
  ) {
    return axiosClient.patch(
      `/service-orders/${orderId}/deliver`,
      {
        deliverable_id:
          data.deliverable_id ?? null,
        note: data.note ?? null,
      }
    );
  },


  // ======================================================
  // COMPLETE ORDER
  // PATCH /api/service-orders/{order_id}/complete
  //
  // Payload:
  // {
  //   release_escrow: boolean,
  //   note: string | null
  // }
  // ======================================================

  complete(
    orderId,
    data = {}
  ) {
    return axiosClient.patch(
      `/service-orders/${orderId}/complete`,
      {
        release_escrow:
          data.release_escrow ?? true,
        note: data.note ?? null,
      }
    );
  },


  // ======================================================
  // CANCEL ORDER
  // PATCH /api/service-orders/{order_id}/cancel
  //
  // Payload:
  // {
  //   cancellation_reason: string,
  //   refund_escrow: boolean
  // }
  // ======================================================

  cancel(
    orderId,
    data
  ) {
    return axiosClient.patch(
      `/service-orders/${orderId}/cancel`,
      {
        cancellation_reason:
          data.cancellation_reason,
        refund_escrow:
          data.refund_escrow ?? true,
      }
    );
  },


  // ======================================================
  // DISPUTE ORDER
  // PATCH /api/service-orders/{order_id}/dispute
  //
  // Payload:
  // {
  //   reason: string,
  //   description: string,
  //   evidence_url: string | null
  // }
  // ======================================================

  dispute(
    orderId,
    data
  ) {
    return axiosClient.patch(
      `/service-orders/${orderId}/dispute`,
      {
        reason: data.reason,
        description: data.description,
        evidence_url:
          data.evidence_url ?? null,
      }
    );
  },


  // ======================================================
  // UPDATE STATUS
  // PATCH /api/service-orders/{order_id}/status
  //
  // Chỉ nên dùng cho Admin hoặc xử lý đặc biệt.
  // ======================================================

  updateStatus(
    orderId,
    statusValue,
    note = null
  ) {
    return axiosClient.patch(
      `/service-orders/${orderId}/status`,
      {
        status: statusValue,
        note,
      }
    );
  },


  // ======================================================
  // DELETE
  // DELETE /api/service-orders/{order_id}
  //
  // Chỉ xóa được PENDING/CANCELLED và chưa liên kết
  // Contract hoặc Escrow.
  // ======================================================

  delete(orderId) {
    return axiosClient.delete(
      `/service-orders/${orderId}`
    );
  },
};


export default serviceOrderApi;