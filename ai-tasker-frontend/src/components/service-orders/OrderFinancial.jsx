import React, { useMemo } from "react";

import {
  Alert,
  Button,
  Card,
  Col,
  Descriptions,
  Empty,
  Flex,
  Progress,
  Row,
  Space,
  Statistic,
  Tag,
  Typography,
} from "antd";

import {
  BankOutlined,
  CheckCircleOutlined,
  DollarOutlined,
  FileProtectOutlined,
  LockOutlined,
  SafetyCertificateOutlined,
  TransactionOutlined,
  WalletOutlined,
} from "@ant-design/icons";


const {
  Text,
  Paragraph,
} = Typography;


// ==========================================================
// HELPERS
// ==========================================================

const normalizeStatus = (value, fallback = "UNKNOWN") => (
  String(value || fallback)
    .trim()
    .toUpperCase()
);


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


const clampPercentage = (value) => (
  Math.max(
    0,
    Math.min(
      Number(value || 0),
      100
    )
  )
);


const ESCROW_STATUS_LABELS = {
  PENDING: "Chờ nạp tiền",
  CREATED: "Đã tạo",
  FUNDED: "Đã nạp tiền",
  HELD: "Đang giữ tiền",
  PARTIALLY_RELEASED: "Đã giải ngân một phần",
  RELEASED: "Đã giải ngân",
  PARTIALLY_REFUNDED: "Đã hoàn tiền một phần",
  REFUNDED: "Đã hoàn tiền",
  DISPUTED: "Đang tranh chấp",
  CANCELLED: "Đã hủy",
};


const ESCROW_STATUS_COLORS = {
  PENDING: "gold",
  CREATED: "default",
  FUNDED: "blue",
  HELD: "cyan",
  PARTIALLY_RELEASED: "processing",
  RELEASED: "green",
  PARTIALLY_REFUNDED: "purple",
  REFUNDED: "purple",
  DISPUTED: "red",
  CANCELLED: "default",
};


const CONTRACT_STATUS_LABELS = {
  DRAFT: "Bản nháp",
  PENDING: "Chờ xác nhận",
  ACTIVE: "Đang hiệu lực",
  COMPLETED: "Hoàn thành",
  CANCELLED: "Đã hủy",
  DISPUTED: "Đang tranh chấp",
};


const CONTRACT_STATUS_COLORS = {
  DRAFT: "default",
  PENDING: "gold",
  ACTIVE: "blue",
  COMPLETED: "green",
  CANCELLED: "default",
  DISPUTED: "red",
};


// ==========================================================
// CONTRACT CARD
// ==========================================================

function ContractCard({
  contract,
  contractId,
  currency,
  onViewContract,
}) {
  if (!contract && !contractId) {
    return (
      <Card
        title={
          <Space>
            <FileProtectOutlined />
            <span>Hợp đồng</span>
          </Space>
        }
        style={{
          height: "100%",
        }}
      >
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description="Đơn hàng chưa liên kết hợp đồng."
        />
      </Card>
    );
  }

  const status = normalizeStatus(
    contract?.status,
    "PENDING"
  );

  return (
    <Card
      title={
        <Space>
          <FileProtectOutlined />
          <span>Hợp đồng</span>
        </Space>
      }
      style={{
        height: "100%",
      }}
      extra={
        typeof onViewContract === "function"
          && (
            <Button
              type="link"
              onClick={() => {
                onViewContract(
                  contract?.id || contractId
                );
              }}
            >
              Xem hợp đồng
            </Button>
          )
      }
    >
      <Descriptions
        bordered
        size="small"
        column={1}
      >
        <Descriptions.Item
          label="Contract ID"
        >
          <Text copyable>
            {contract?.id || contractId}
          </Text>
        </Descriptions.Item>

        <Descriptions.Item
          label="Tiêu đề"
        >
          {contract?.title
            || "Hợp đồng dịch vụ AI"}
        </Descriptions.Item>

        <Descriptions.Item
          label="Trạng thái"
        >
          <Tag
            color={
              CONTRACT_STATUS_COLORS[status]
              || "default"
            }
          >
            {CONTRACT_STATUS_LABELS[status]
              || status}
          </Tag>
        </Descriptions.Item>

        <Descriptions.Item
          label="Giá trị hợp đồng"
        >
          <Text strong>
            {formatCurrency(
              contract?.total_amount,
              contract?.currency || currency
            )}
          </Text>
        </Descriptions.Item>

        <Descriptions.Item
          label="Ngày tạo"
        >
          {formatDateTime(
            contract?.created_at
          )}
        </Descriptions.Item>

        <Descriptions.Item
          label="Ngày cập nhật"
        >
          {formatDateTime(
            contract?.updated_at
          )}
        </Descriptions.Item>
      </Descriptions>

      {contract?.description && (
        <Paragraph
          type="secondary"
          ellipsis={{
            rows: 4,
            expandable: true,
            symbol: "Xem thêm",
          }}
          style={{
            marginTop: 16,
            marginBottom: 0,
            lineHeight: 1.7,
          }}
        >
          {contract.description}
        </Paragraph>
      )}
    </Card>
  );
}


// ==========================================================
// ESCROW CARD
// ==========================================================

function EscrowCard({
  escrow,
  escrowId,
  orderPrice,
  currency,
  onViewEscrow,
}) {
  if (!escrow && !escrowId) {
    return (
      <Card
        title={
          <Space>
            <SafetyCertificateOutlined />
            <span>Escrow</span>
          </Space>
        }
        style={{
          height: "100%",
        }}
      >
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description="Đơn hàng chưa liên kết Escrow."
        />
      </Card>
    );
  }

  const status = normalizeStatus(
    escrow?.status,
    "PENDING"
  );

  const totalAmount = Number(
    escrow?.amount
    ?? escrow?.total_amount
    ?? orderPrice
    ?? 0
  );

  const releasedAmount = Number(
    escrow?.released_amount || 0
  );

  const refundedAmount = Number(
    escrow?.refunded_amount || 0
  );

  const remainingAmount = Math.max(
    0,
    totalAmount
      - releasedAmount
      - refundedAmount
  );

  const releasedPercentage = totalAmount > 0
    ? clampPercentage(
        releasedAmount
          / totalAmount
          * 100
      )
    : 0;

  const refundedPercentage = totalAmount > 0
    ? clampPercentage(
        refundedAmount
          / totalAmount
          * 100
      )
    : 0;

  return (
    <Card
      title={
        <Space>
          <SafetyCertificateOutlined />
          <span>Escrow</span>
        </Space>
      }
      style={{
        height: "100%",
      }}
      extra={
        typeof onViewEscrow === "function"
          && (
            <Button
              type="link"
              onClick={() => {
                onViewEscrow(
                  escrow?.id || escrowId
                );
              }}
            >
              Xem Escrow
            </Button>
          )
      }
    >
      <Descriptions
        bordered
        size="small"
        column={1}
      >
        <Descriptions.Item
          label="Escrow ID"
        >
          <Text copyable>
            {escrow?.id || escrowId}
          </Text>
        </Descriptions.Item>

        <Descriptions.Item
          label="Trạng thái"
        >
          <Tag
            color={
              ESCROW_STATUS_COLORS[status]
              || "default"
            }
          >
            {ESCROW_STATUS_LABELS[status]
              || status}
          </Tag>
        </Descriptions.Item>

        <Descriptions.Item
          label="Tổng tiền ký quỹ"
        >
          <Text strong>
            {formatCurrency(
              totalAmount,
              escrow?.currency || currency
            )}
          </Text>
        </Descriptions.Item>

        <Descriptions.Item
          label="Đã giải ngân"
        >
          {formatCurrency(
            releasedAmount,
            escrow?.currency || currency
          )}
        </Descriptions.Item>

        <Descriptions.Item
          label="Đã hoàn tiền"
        >
          {formatCurrency(
            refundedAmount,
            escrow?.currency || currency
          )}
        </Descriptions.Item>

        <Descriptions.Item
          label="Đang được giữ"
        >
          <Text
            strong
            style={{
              color: "#13c2c2",
            }}
          >
            {formatCurrency(
              remainingAmount,
              escrow?.currency || currency
            )}
          </Text>
        </Descriptions.Item>
      </Descriptions>

      <div
        style={{
          marginTop: 18,
        }}
      >
        <Text
          type="secondary"
          style={{
            display: "block",
            marginBottom: 7,
          }}
        >
          Tỷ lệ đã giải ngân
        </Text>

        <Progress
          percent={Number(
            releasedPercentage.toFixed(2)
          )}
          strokeColor={{
            "0%": "#1677ff",
            "100%": "#52c41a",
          }}
        />
      </div>

      {refundedAmount > 0 && (
        <div
          style={{
            marginTop: 12,
          }}
        >
          <Text
            type="secondary"
            style={{
              display: "block",
              marginBottom: 7,
            }}
          >
            Tỷ lệ đã hoàn tiền
          </Text>

          <Progress
            percent={Number(
              refundedPercentage.toFixed(2)
            )}
            strokeColor="#722ed1"
          />
        </div>
      )}

      <Alert
        type={
          status === "DISPUTED"
            ? "error"
            : status === "RELEASED"
              ? "success"
              : "info"
        }
        showIcon
        icon={
          status === "RELEASED"
            ? <CheckCircleOutlined />
            : status === "DISPUTED"
              ? <LockOutlined />
              : <SafetyCertificateOutlined />
        }
        message={
          status === "RELEASED"
            ? "Escrow đã giải ngân"
            : status === "DISPUTED"
              ? "Escrow đang bị khóa do tranh chấp"
              : "Khoản thanh toán được bảo vệ"
        }
        description={
          status === "RELEASED"
            ? (
              "Toàn bộ tiền ký quỹ đã được chuyển "
              + "cho chuyên gia."
            )
            : status === "DISPUTED"
              ? (
                "Tiền ký quỹ tạm thời không thể giải ngân "
                + "cho đến khi tranh chấp được xử lý."
              )
              : (
                "Tiền chỉ được giải ngân sau khi "
                + "doanh nghiệp nghiệm thu kết quả."
              )
        }
        style={{
          marginTop: 18,
        }}
      />
    </Card>
  );
}


// ==========================================================
// PAYMENT SUMMARY
// ==========================================================

function PaymentSummary({
  payment,
  currency,
  onViewPayment,
}) {
  if (!payment) {
    return (
      <Card
        title={
          <Space>
            <TransactionOutlined />
            <span>Thanh toán</span>
          </Space>
        }
      >
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description="Chưa có giao dịch thanh toán."
        />
      </Card>
    );
  }

  const paymentStatus = normalizeStatus(
    payment.status,
    "PENDING"
  );

  const paymentStatusColors = {
    PENDING: "gold",
    PROCESSING: "processing",
    SUCCESS: "green",
    COMPLETED: "green",
    FAILED: "red",
    CANCELLED: "default",
    REFUNDED: "purple",
  };

  return (
    <Card
      title={
        <Space>
          <TransactionOutlined />
          <span>Thanh toán</span>
        </Space>
      }
      extra={
        typeof onViewPayment === "function"
          && (
            <Button
              type="link"
              onClick={() => {
                onViewPayment(payment.id);
              }}
            >
              Xem giao dịch
            </Button>
          )
      }
    >
      <Row gutter={[16, 16]}>
        <Col
          xs={24}
          sm={12}
          lg={6}
        >
          <Statistic
            title="Số tiền"
            value={Number(
              payment.amount || 0
            )}
            precision={0}
            prefix={<DollarOutlined />}
            suffix={
              payment.currency
              || currency
              || "VND"
            }
            formatter={(value) => (
              Number(value).toLocaleString(
                "vi-VN"
              )
            )}
          />
        </Col>

        <Col
          xs={24}
          sm={12}
          lg={6}
        >
          <Statistic
            title="Phương thức"
            value={
              payment.payment_method
              || payment.method
              || "N/A"
            }
            prefix={<BankOutlined />}
            valueStyle={{
              fontSize: 18,
            }}
          />
        </Col>

        <Col
          xs={24}
          sm={12}
          lg={6}
        >
          <Statistic
            title="Trạng thái"
            value={
              paymentStatus
            }
            prefix={<TransactionOutlined />}
            valueStyle={{
              fontSize: 18,
            }}
          />
        </Col>

        <Col
          xs={24}
          sm={12}
          lg={6}
        >
          <Statistic
            title="Thời điểm"
            value={
              formatDateTime(
                payment.paid_at
                || payment.created_at
              )
            }
            valueStyle={{
              fontSize: 15,
            }}
          />
        </Col>
      </Row>

      <Flex
        gap={8}
        wrap="wrap"
        style={{
          marginTop: 16,
        }}
      >
        <Tag
          color={
            paymentStatusColors[paymentStatus]
            || "default"
          }
        >
          {paymentStatus}
        </Tag>

        {payment.transaction_code && (
          <Tag>
            Mã GD: {payment.transaction_code}
          </Tag>
        )}

        {payment.provider && (
          <Tag color="blue">
            {payment.provider}
          </Tag>
        )}
      </Flex>
    </Card>
  );
}


// ==========================================================
// MAIN COMPONENT
// ==========================================================

function OrderFinancial({
  order,
  onViewContract,
  onViewEscrow,
  onViewPayment,
}) {
  const contract = useMemo(
    () => order?.contract || null,
    [order]
  );

  const escrow = useMemo(
    () => order?.escrow || null,
    [order]
  );

  const payment = useMemo(
    () => (
      order?.payment
      || escrow?.payment
      || contract?.payment
      || null
    ),
    [
      contract,
      escrow,
      order,
    ]
  );

  if (!order) {
    return (
      <Card>
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description={
            "Không có dữ liệu tài chính."
          }
        />
      </Card>
    );
  }

  return (
    <Space
      direction="vertical"
      size={24}
      style={{
        width: "100%",
        marginTop: 24,
      }}
    >
      <Row gutter={[24, 24]}>
        <Col
          xs={24}
          lg={12}
        >
          <ContractCard
            contract={contract}
            contractId={order.contract_id}
            currency={order.currency}
            onViewContract={onViewContract}
          />
        </Col>

        <Col
          xs={24}
          lg={12}
        >
          <EscrowCard
            escrow={escrow}
            escrowId={order.escrow_id}
            orderPrice={order.price}
            currency={order.currency}
            onViewEscrow={onViewEscrow}
          />
        </Col>
      </Row>

      <PaymentSummary
        payment={payment}
        currency={order.currency}
        onViewPayment={onViewPayment}
      />

      <Card>
        <Flex
          align="center"
          gap={14}
        >
          <WalletOutlined
            style={{
              color: "#52c41a",
              fontSize: 28,
            }}
          />

          <div>
            <Text strong>
              Bảo vệ giao dịch AITasker
            </Text>

            <Paragraph
              type="secondary"
              style={{
                marginTop: 4,
                marginBottom: 0,
              }}
            >
              Hệ thống sử dụng Wallet và Escrow để bảo vệ
              quyền lợi của doanh nghiệp và chuyên gia trong
              toàn bộ quá trình thực hiện dịch vụ.
            </Paragraph>
          </div>
        </Flex>
      </Card>
    </Space>
  );
}


export default OrderFinancial;