import React, { useMemo } from "react";

import {
  Avatar,
  Button,
  Card,
  Col,
  Descriptions,
  Divider,
  Flex,
  Row,
  Space,
  Statistic,
  Tag,
  Typography,
} from "antd";

import {
  CalendarOutlined,
  DollarOutlined,
  EyeOutlined,
  FileTextOutlined,
  ReloadOutlined,
  RocketOutlined,
  ShoppingCartOutlined,
} from "@ant-design/icons";


const {
  Title,
  Text,
  Paragraph,
} = Typography;


// ==========================================================
// HELPERS
// ==========================================================

const formatCurrency = (
  value,
  currency = "VND"
) => {
  const numericValue = Number(value || 0);

  if (!Number.isFinite(numericValue)) {
    return `0 ${currency}`;
  }

  try {
    return new Intl.NumberFormat(
      "vi-VN",
      {
        style: "currency",
        currency: currency || "VND",
        maximumFractionDigits: 0,
      }
    ).format(numericValue);
  } catch {
    return (
      `${numericValue.toLocaleString("vi-VN")} `
      + `${currency || "VND"}`
    );
  }
};


const formatDateTime = (value) => {
  if (!value) {
    return "Chưa cập nhật";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Không hợp lệ";
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


const normalizeStatus = (value) => (
  String(value || "PENDING")
    .trim()
    .toUpperCase()
);


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


function OrderSummary({
  order,
  onViewService,
}) {
  const status = useMemo(
    () => normalizeStatus(
      order?.status
    ),
    [order?.status]
  );

  const service = useMemo(
    () => (
      order?.service
      || {
        id: order?.service_id,
        title: order?.service_title,
      }
    ),
    [order]
  );

  const statusLabel = (
    STATUS_LABELS[status]
    || status
  );

  const statusColor = (
    STATUS_COLORS[status]
    || "default"
  );


  return (
    <Space
      direction="vertical"
      size={24}
      style={{
        width: "100%",
      }}
    >
      {/* ==================================================
          STATISTICS
      ================================================== */}

      <Row gutter={[16, 16]}>
        <Col
          xs={24}
          sm={12}
          xl={6}
        >
          <Card>
            <Statistic
              title="Giá trị đơn hàng"
              value={Number(
                order?.price || 0
              )}
              precision={0}
              prefix={<DollarOutlined />}
              suffix={
                order?.currency || "VND"
              }
              formatter={(value) => (
                Number(value).toLocaleString(
                  "vi-VN"
                )
              )}
            />
          </Card>
        </Col>

        <Col
          xs={24}
          sm={12}
          xl={6}
        >
          <Card>
            <Statistic
              title="Thời gian thực hiện"
              value={
                order?.delivery_days || 0
              }
              prefix={<CalendarOutlined />}
              suffix="ngày"
            />
          </Card>
        </Col>

        <Col
          xs={24}
          sm={12}
          xl={6}
        >
          <Card>
            <Statistic
              title="Số lần chỉnh sửa"
              value={
                order?.revision_count || 0
              }
              prefix={<ReloadOutlined />}
            />
          </Card>
        </Col>

        <Col
          xs={24}
          sm={12}
          xl={6}
        >
          <Card>
            <Statistic
              title="Trạng thái"
              value={statusLabel}
              prefix={<ShoppingCartOutlined />}
              valueStyle={{
                fontSize: 18,
              }}
            />
          </Card>
        </Col>
      </Row>


      {/* ==================================================
          ORDER INFORMATION
      ================================================== */}

      <Card
        title={
          <Space>
            <FileTextOutlined />
            <span>Thông tin đơn hàng</span>
          </Space>
        }
      >
        <Descriptions
          bordered
          column={{
            xs: 1,
            sm: 2,
          }}
        >
          <Descriptions.Item
            label="Mã đơn hàng"
          >
            {order?.id ? (
              <Text copyable>
                {order.id}
              </Text>
            ) : (
              <Text type="secondary">
                Chưa có dữ liệu
              </Text>
            )}
          </Descriptions.Item>

          <Descriptions.Item
            label="Trạng thái"
          >
            <Tag color={statusColor}>
              {statusLabel}
            </Tag>
          </Descriptions.Item>

          <Descriptions.Item
            label="Ngày tạo"
          >
            {formatDateTime(
              order?.created_at
            )}
          </Descriptions.Item>

          <Descriptions.Item
            label="Cập nhật gần nhất"
          >
            {formatDateTime(
              order?.updated_at
            )}
          </Descriptions.Item>

          <Descriptions.Item
            label="Ngày xác nhận"
          >
            {formatDateTime(
              order?.confirmed_at
            )}
          </Descriptions.Item>

          <Descriptions.Item
            label="Ngày bắt đầu"
          >
            {formatDateTime(
              order?.started_at
            )}
          </Descriptions.Item>

          <Descriptions.Item
            label="Ngày bàn giao"
          >
            {formatDateTime(
              order?.delivered_at
            )}
          </Descriptions.Item>

          <Descriptions.Item
            label="Ngày hoàn thành"
          >
            {formatDateTime(
              order?.completed_at
            )}
          </Descriptions.Item>

          <Descriptions.Item
            label="Contract ID"
          >
            {order?.contract_id ? (
              <Text copyable>
                {order.contract_id}
              </Text>
            ) : (
              <Text type="secondary">
                Chưa liên kết
              </Text>
            )}
          </Descriptions.Item>

          <Descriptions.Item
            label="Escrow ID"
          >
            {order?.escrow_id ? (
              <Text copyable>
                {order.escrow_id}
              </Text>
            ) : (
              <Text type="secondary">
                Chưa liên kết
              </Text>
            )}
          </Descriptions.Item>
        </Descriptions>

        <Divider />

        <Title level={5}>
          Yêu cầu của doanh nghiệp
        </Title>

        <Paragraph
          style={{
            whiteSpace: "pre-line",
            lineHeight: 1.8,
            marginBottom: 0,
          }}
        >
          {order?.requirements
            || "Chưa có yêu cầu chi tiết."}
        </Paragraph>

        <Divider />

        <Title level={5}>
          Ghi chú
        </Title>

        <Paragraph
          style={{
            whiteSpace: "pre-line",
            lineHeight: 1.8,
            marginBottom: 0,
          }}
        >
          {order?.note
            || "Chưa có ghi chú."}
        </Paragraph>

        {order?.cancellation_reason && (
          <>
            <Divider />

            <Title
              level={5}
              type="danger"
            >
              Lý do hủy hoặc hoàn tiền
            </Title>

            <Paragraph
              type="danger"
              style={{
                whiteSpace: "pre-line",
                lineHeight: 1.8,
                marginBottom: 0,
              }}
            >
              {order.cancellation_reason}
            </Paragraph>
          </>
        )}
      </Card>


      {/* ==================================================
          SERVICE SUMMARY
      ================================================== */}

      <Card
        title={
          <Space>
            <RocketOutlined />
            <span>Dịch vụ AI</span>
          </Space>
        }
        extra={
          typeof onViewService === "function" && (
            <Button
              type="link"
              icon={<EyeOutlined />}
              onClick={onViewService}
            >
              Xem chi tiết
            </Button>
          )
        }
      >
        <Flex
          align="center"
          gap={18}
          wrap="wrap"
        >
          <Avatar
            size={78}
            shape="square"
            src={service?.image_url}
            icon={<RocketOutlined />}
            style={{
              background:
                "linear-gradient(135deg, #4f46e5, #7c3aed)",
            }}
          />

          <div
            style={{
              flex: 1,
              minWidth: 250,
            }}
          >
            <Title
              level={4}
              style={{
                marginBottom: 6,
              }}
            >
              {service?.title
                || order?.service_title
                || "Dịch vụ AI"}
            </Title>

            <Paragraph
              type="secondary"
              ellipsis={{
                rows: 3,
              }}
              style={{
                marginBottom: 12,
              }}
            >
              {service?.short_description
                || service?.description
                || "Dịch vụ AI thuộc Marketplace AITasker."}
            </Paragraph>

            <Flex
              gap={8}
              wrap="wrap"
            >
              <Tag color="green">
                {formatCurrency(
                  order?.price,
                  order?.currency
                )}
              </Tag>

              <Tag
                icon={<CalendarOutlined />}
                color="cyan"
              >
                {order?.delivery_days || 0} ngày
              </Tag>

              <Tag
                icon={<ReloadOutlined />}
                color="blue"
              >
                {order?.revision_count || 0} lần chỉnh sửa
              </Tag>

              {service?.category?.name && (
                <Tag color="geekblue">
                  {service.category.name}
                </Tag>
              )}
            </Flex>
          </div>
        </Flex>

        {Array.isArray(service?.skills)
          && service.skills.length > 0 && (
          <>
            <Divider />

            <Title level={5}>
              Kỹ năng liên quan
            </Title>

            <Flex
              gap={8}
              wrap="wrap"
            >
              {service.skills.map(
                (skill, index) => (
                  <Tag
                    key={`${skill}-${index}`}
                    color="blue"
                    style={{
                      marginInlineEnd: 0,
                      borderRadius: 999,
                    }}
                  >
                    {skill}
                  </Tag>
                )
              )}
            </Flex>
          </>
        )}
      </Card>
    </Space>
  );
}


export default OrderSummary;