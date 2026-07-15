import React, { useMemo } from "react";

import {
  Card,
  Steps,
  Tag,
  Typography,
} from "antd";

import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  FileDoneOutlined,
  FileTextOutlined,
  LoadingOutlined,
} from "@ant-design/icons";

const { Text } = Typography;

// ===========================================
// STATUS
// ===========================================

const STATUS_LABELS = {
  PENDING: "Chờ xác nhận",
  CONFIRMED: "Đã xác nhận",
  IN_PROGRESS: "Đang thực hiện",
  DELIVERED: "Đã bàn giao",
  COMPLETED: "Hoàn thành",
  DISPUTED: "Tranh chấp",
  CANCELLED: "Đã hủy",
  REFUNDED: "Đã hoàn tiền",
};

const STATUS_COLORS = {
  PENDING: "gold",
  CONFIRMED: "blue",
  IN_PROGRESS: "processing",
  DELIVERED: "cyan",
  COMPLETED: "green",
  DISPUTED: "red",
  CANCELLED: "default",
  REFUNDED: "purple",
};

const FLOW = [
  "PENDING",
  "CONFIRMED",
  "IN_PROGRESS",
  "DELIVERED",
  "COMPLETED",
];

// ===========================================

const normalizeStatus = (status) =>
  String(status || "PENDING")
    .trim()
    .toUpperCase();

const formatDate = (value) => {
  if (!value) return "";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "";
  }

  return new Intl.DateTimeFormat(
    "vi-VN",
    {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }
  ).format(date);
};

// ===========================================

function OrderSteps({ order }) {
  const status = useMemo(
    () => normalizeStatus(order?.status),
    [order]
  );

  const current = useMemo(() => {
    const index = FLOW.indexOf(status);

    if (index >= 0) return index;

    return 0;
  }, [status]);

  const stepStatus = useMemo(() => {
    if (
      status === "DISPUTED" ||
      status === "CANCELLED" ||
      status === "REFUNDED"
    ) {
      return "error";
    }

    if (status === "COMPLETED") {
      return "finish";
    }

    return "process";
  }, [status]);

  const items = [
    {
      title: "Pending",
      description:
        formatDate(order?.created_at) ||
        "Đơn hàng vừa được tạo",
      icon: <FileTextOutlined />,
    },
    {
      title: "Confirmed",
      description:
        formatDate(order?.confirmed_at) ||
        "Chờ xác nhận",
      icon: <CheckCircleOutlined />,
    },
    {
      title: "In Progress",
      description:
        formatDate(order?.started_at) ||
        "Chưa bắt đầu",
      icon: <LoadingOutlined />,
    },
    {
      title: "Delivered",
      description:
        formatDate(order?.delivered_at) ||
        "Chưa bàn giao",
      icon: <FileDoneOutlined />,
    },
    {
      title: "Completed",
      description:
        formatDate(order?.completed_at) ||
        "Chưa hoàn thành",
      icon: <CheckCircleOutlined />,
    },
  ];

  return (
    <Card
      title="Tiến trình đơn hàng"
      style={{
        marginBottom: 24,
      }}
    >
      <div
        style={{
          marginBottom: 18,
        }}
      >
        <Tag
          color={
            STATUS_COLORS[status] ||
            "default"
          }
        >
          {STATUS_LABELS[status] || status}
        </Tag>

        <Text
          type="secondary"
          style={{
            marginLeft: 12,
          }}
        >
          Theo dõi toàn bộ tiến trình xử lý
          Service Order.
        </Text>
      </div>

      <Steps
        current={current}
        status={stepStatus}
        responsive
        items={items}
      />

      {(status === "DISPUTED" ||
        status === "CANCELLED" ||
        status === "REFUNDED") && (
        <div
          style={{
            marginTop: 24,
          }}
        >
          <Tag color="red">
            Trạng thái đặc biệt
          </Tag>

          <Text
            type="secondary"
            style={{
              display: "block",
              marginTop: 8,
            }}
          >
            Đơn hàng không còn tiếp tục theo
            quy trình thông thường.
          </Text>
        </div>
      )}
    </Card>
  );
}

export default OrderSteps;