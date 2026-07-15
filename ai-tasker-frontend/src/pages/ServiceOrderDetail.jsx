import React, {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  App,
  Button,
  Card,
  Result,
  Skeleton,
} from "antd";

import {
  ReloadOutlined,
  ShoppingCartOutlined,
} from "@ant-design/icons";

import {
  useNavigate,
  useParams,
} from "react-router-dom";

import serviceOrderApi from "../api/serviceOrderApi";

import OrderActions from "../components/service-orders/OrderActions";
import OrderFinancial from "../components/service-orders/OrderFinancial";
import OrderHeader from "../components/service-orders/OrderHeader";
import OrderParties from "../components/service-orders/OrderParties";
import OrderSteps from "../components/service-orders/OrderSteps";
import OrderSummary from "../components/service-orders/OrderSummary";


const normalizeResponse = (response) => (
  response?.data ?? response
);


const getErrorMessage = (error) => {
  const detail = error?.response?.data?.detail;

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => (
        item?.msg
        || "Dữ liệu không hợp lệ."
      ))
      .join(", ");
  }

  if (error?.response?.status === 404) {
    return "Không tìm thấy đơn đặt dịch vụ.";
  }

  return (
    error?.message
    || "Không thể tải đơn đặt dịch vụ."
  );
};


function ServiceOrderDetail() {
  const navigate = useNavigate();

  const {
    orderId,
  } = useParams();

  const {
    message,
  } = App.useApp();

  const [order, setOrder] = useState(null);

  const [loading, setLoading] = useState(true);

  const [refreshing, setRefreshing] = useState(false);

  const [actionLoading, setActionLoading] = useState(false);

  const [error, setError] = useState("");


  // ======================================================
  // DERIVED VALUES
  // ======================================================

  const status = useMemo(
    () => String(
      order?.status || "PENDING"
    )
      .trim()
      .toUpperCase(),
    [order?.status]
  );


  // ======================================================
  // LOAD ORDER
  // ======================================================

  const loadOrder = useCallback(
    async ({
      showMessage = false,
      silent = false,
    } = {}) => {
      if (!orderId) {
        setOrder(null);
        setError(
          "Mã đơn đặt dịch vụ không hợp lệ."
        );
        setLoading(false);
        setRefreshing(false);
        return null;
      }

      if (silent) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      setError("");

      try {
        const response = await serviceOrderApi.getById(
          orderId
        );

        const data = normalizeResponse(
          response
        );

        if (!data?.id) {
          throw new Error(
            "Backend không trả về đơn hàng hợp lệ."
          );
        }

        setOrder(data);

        if (showMessage) {
          message.success(
            "Đã cập nhật dữ liệu đơn hàng."
          );
        }

        return data;
      } catch (requestError) {
        const errorMessage = getErrorMessage(
          requestError
        );

        setOrder(null);
        setError(errorMessage);

        if (showMessage) {
          message.error(errorMessage);
        }

        return null;
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [
      message,
      orderId,
    ]
  );


  useEffect(() => {
    loadOrder();
  }, [loadOrder]);


  // ======================================================
  // ACTION WRAPPER
  // ======================================================

  const runAction = async (
    action,
    successMessage
  ) => {
    setActionLoading(true);

    try {
      await action();

      message.success(
        successMessage
      );

      await loadOrder({
        silent: true,
      });
    } catch (requestError) {
      const errorMessage = getErrorMessage(
        requestError
      );

      message.error(errorMessage);

      throw requestError;
    } finally {
      setActionLoading(false);
    }
  };


  // ======================================================
  // NAVIGATION
  // ======================================================

  const handleBack = () => {
    navigate("/service-orders");
  };


  const handleViewService = () => {
    const slug = (
      order?.service?.slug
    );

    if (slug) {
      navigate(
        `/ai-services/${encodeURIComponent(slug)}`
      );

      return;
    }

    navigate("/ai-services");
  };


  const handleViewEnterprise = (
    enterpriseId
  ) => {
    if (!enterpriseId) {
      message.warning(
        "Không tìm thấy thông tin doanh nghiệp."
      );

      return;
    }

    navigate(
      `/enterprises?enterprise_id=${enterpriseId}`
    );
  };


  const handleViewExpert = (
    expertId
  ) => {
    if (!expertId) {
      message.warning(
        "Không tìm thấy thông tin chuyên gia."
      );

      return;
    }

    navigate(
      `/experts?expert_id=${expertId}`
    );
  };


  const handleViewContract = (
    contractId
  ) => {
    if (!contractId) {
      message.warning(
        "Đơn hàng chưa liên kết hợp đồng."
      );

      return;
    }

    navigate(
      `/contracts?contract_id=${contractId}`
    );
  };


  const handleViewEscrow = (
    escrowId
  ) => {
    if (!escrowId) {
      message.warning(
        "Đơn hàng chưa liên kết Escrow."
      );

      return;
    }

    navigate(
      `/contracts?escrow_id=${escrowId}`
    );
  };


  const handleViewPayment = (
    paymentId
  ) => {
    if (!paymentId) {
      message.warning(
        "Không tìm thấy giao dịch thanh toán."
      );

      return;
    }

    navigate(
      `/payments?payment_id=${paymentId}`
    );
  };


  // ======================================================
  // LOADING
  // ======================================================

  if (loading) {
    return (
      <Card>
        <Skeleton
          active
          paragraph={{
            rows: 16,
          }}
        />
      </Card>
    );
  }


  // ======================================================
  // ERROR
  // ======================================================

  if (error || !order) {
    return (
      <Card>
        <Result
          status="404"
          title="Không tìm thấy đơn hàng"
          subTitle={
            error
            || "Đơn đặt dịch vụ không tồn tại."
          }
          extra={[
            <Button
              key="orders"
              type="primary"
              icon={<ShoppingCartOutlined />}
              onClick={handleBack}
            >
              Danh sách đơn hàng
            </Button>,

            <Button
              key="reload"
              icon={<ReloadOutlined />}
              onClick={() => loadOrder()}
            >
              Thử lại
            </Button>,
          ]}
        />
      </Card>
    );
  }


  // ======================================================
  // RENDER
  // ======================================================

  return (
    <div>
      <OrderHeader
        order={order}
        loading={refreshing}
        onBack={handleBack}
        onReload={() => loadOrder({
          showMessage: true,
          silent: true,
        })}
      />

      <OrderSteps
        order={order}
      />

      <OrderSummary
        order={order}
        onViewService={
          handleViewService
        }
      />

      <OrderParties
        order={order}
        onViewEnterprise={
          handleViewEnterprise
        }
        onViewExpert={
          handleViewExpert
        }
      />

      <OrderFinancial
        order={order}
        onViewContract={
          handleViewContract
        }
        onViewEscrow={
          handleViewEscrow
        }
        onViewPayment={
          handleViewPayment
        }
      />

      <OrderActions
        order={order}
        status={status}
        loading={actionLoading}
        runAction={runAction}
      />
    </div>
  );
}


export default ServiceOrderDetail;