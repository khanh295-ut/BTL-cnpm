import React, { useMemo } from "react";

import {
  Button,
  Card,
  Col,
  Flex,
  Row,
  Space,
  Tag,
  Typography,
} from "antd";

import {
  ArrowLeftOutlined,
  ReloadOutlined,
  ShoppingCartOutlined,
} from "@ant-design/icons";


const {
  Title,
  Text,
  Paragraph,
} = Typography;


const STATUS_LABELS = {
  PENDING: "Chờ xác nhận",
  CONFIRMED: "Đã xác nhận",
  IN_PROGRESS: "Đang thực hiện",
  DELIVERED: "Đã bàn giao",
  COMPLETED: "Hoàn thành",
  DISPUTED: "Đang tranh chấp",
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


const normalizeStatus = (value) => (
  String(value || "PENDING")
    .trim()
    .toUpperCase()
);


function OrderHeader({
  order,
  onBack,
  onReload,
  loading = false,
}) {
  const status = useMemo(
    () => normalizeStatus(order?.status),
    [order?.status]
  );

  const statusLabel = (
    STATUS_LABELS[status]
    || status
  );

  const statusColor = (
    STATUS_COLORS[status]
    || "default"
  );

  const orderTitle = (
    order?.service_title
    || order?.service?.title
    || "Đơn đặt dịch vụ AI"
  );

  const shortOrderId = order?.id
    ? String(order.id).slice(0, 8)
    : "N/A";

  return (
    <Card
      bordered={false}
      style={{
        marginBottom: 24,
        overflow: "hidden",
        background:
          "linear-gradient("
          + "135deg, "
          + "#111827 0%, "
          + "#1e1b4b 55%, "
          + "#312e81 100%"
          + ")",
      }}
      styles={{
        body: {
          padding: 28,
        },
      }}
    >
      <Row
        gutter={[24, 24]}
        align="middle"
        justify="space-between"
      >
        <Col
          xs={24}
          lg={17}
        >
          <Space
            direction="vertical"
            size={9}
            style={{
              width: "100%",
            }}
          >
            <Flex
              gap={8}
              wrap="wrap"
              align="center"
            >
              <Tag color={statusColor}>
                {statusLabel}
              </Tag>

              <Tag color="geekblue">
                Service Order
              </Tag>

              <Tag>
                #{shortOrderId}
              </Tag>
            </Flex>

            <Title
              level={2}
              style={{
                margin: 0,
                color: "#ffffff",
                lineHeight: 1.3,
              }}
            >
              <ShoppingCartOutlined />
              {" "}
              {orderTitle}
            </Title>

            <Paragraph
              style={{
                margin: 0,
                color: "#cbd5e1",
                fontSize: 15,
                lineHeight: 1.7,
              }}
            >
              Theo dõi tiến độ thực hiện, hợp đồng,
              Escrow và các thao tác xử lý đơn hàng.
            </Paragraph>

            {order?.id && (
              <Text
                copyable={{
                  text: String(order.id),
                }}
                style={{
                  color: "#a5b4fc",
                  fontSize: 13,
                }}
              >
                Mã đơn: {order.id}
              </Text>
            )}
          </Space>
        </Col>

        <Col
          xs={24}
          lg="auto"
        >
          <Flex
            gap={10}
            wrap="wrap"
          >
            <Button
              size="large"
              icon={<ArrowLeftOutlined />}
              onClick={onBack}
            >
              Quay lại
            </Button>

            <Button
              type="primary"
              size="large"
              icon={<ReloadOutlined />}
              loading={loading}
              onClick={onReload}
            >
              Cập nhật
            </Button>
          </Flex>
        </Col>
      </Row>
    </Card>
  );
}


export default OrderHeader;