import React, { useMemo, useState } from "react";

import {
  Alert,
  App,
  Button,
  Card,
  Checkbox,
  Col,
  Divider,
  Flex,
  Form,
  Input,
  Modal,
  Row,
  Select,
  Space,
  Tag,
  Typography,
} from "antd";

import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  ExclamationCircleOutlined,
  FileDoneOutlined,
  PlayCircleOutlined,
  SafetyCertificateOutlined,
  StopOutlined,
  WarningOutlined,
} from "@ant-design/icons";

import serviceOrderApi from "../../api/serviceOrderApi";


const {
  Text,
  Paragraph,
} = Typography;

const {
  TextArea,
} = Input;


// ==========================================================
// STATUS CONFIG
// ==========================================================

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


// ==========================================================
// HELPERS
// ==========================================================

const normalizeStatus = (value) => (
  String(value || "PENDING")
    .trim()
    .toUpperCase()
);


const extractErrorMessage = (error) => {
  const detail = error?.response?.data?.detail;

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map(
        (item) => (
          item?.msg
          || "Dữ liệu không hợp lệ."
        )
      )
      .join(", ");
  }

  return (
    error?.message
    || "Không thể thực hiện thao tác."
  );
};


// ==========================================================
// MAIN COMPONENT
// ==========================================================

function OrderActions({
  order,
  status: statusProp,
  loading = false,
  runAction,
}) {
  const {
    message,
    modal,
  } = App.useApp();

  const [confirmForm] = Form.useForm();
  const [startForm] = Form.useForm();
  const [deliverForm] = Form.useForm();
  const [completeForm] = Form.useForm();
  const [cancelForm] = Form.useForm();
  const [disputeForm] = Form.useForm();

  const [activeModal, setActiveModal] = useState(null);
  const [localLoading, setLocalLoading] = useState(false);


  const status = useMemo(
    () => normalizeStatus(
      statusProp || order?.status
    ),
    [
      order?.status,
      statusProp,
    ]
  );


  const statusLabel = (
    STATUS_LABELS[status]
    || status
  );


  const statusColor = (
    STATUS_COLORS[status]
    || "default"
  );


  const actionLoading = (
    loading || localLoading
  );


  // ======================================================
  // PERMISSIONS
  // ======================================================

  const permissions = useMemo(
    () => ({
      canConfirm:
        status === "PENDING",

      canStart:
        status === "CONFIRMED",

      canDeliver:
        status === "IN_PROGRESS",

      canComplete:
        status === "DELIVERED",

      canCancel: [
        "PENDING",
        "CONFIRMED",
        "IN_PROGRESS",
      ].includes(status),

      canDispute: [
        "CONFIRMED",
        "IN_PROGRESS",
        "DELIVERED",
      ].includes(status),
    }),
    [status]
  );


  const hasAnyAction = Object.values(
    permissions
  ).some(Boolean);


  // ======================================================
  // ACTION EXECUTION
  // ======================================================

  const executeAction = async (
    action,
    successMessage
  ) => {
    if (typeof runAction === "function") {
      await runAction(
        action,
        successMessage
      );

      return;
    }

    setLocalLoading(true);

    try {
      await action();

      message.success(
        successMessage
      );
    } catch (error) {
      message.error(
        extractErrorMessage(error)
      );

      throw error;
    } finally {
      setLocalLoading(false);
    }
  };


  const closeModal = () => {
    setActiveModal(null);
  };


  // ======================================================
  // CONFIRM
  // ======================================================

  const handleConfirmOrder = async () => {
    try {
      const values = (
        await confirmForm.validateFields()
      );

      await executeAction(
        () => serviceOrderApi.confirm(
          order.id,
          {
            payment_id:
              values.payment_id?.trim()
              || null,

            payer_wallet_id:
              values.payer_wallet_id?.trim()
              || null,

            note:
              values.note?.trim()
              || null,
          }
        ),
        "Đã xác nhận đơn hàng."
      );

      confirmForm.resetFields();
      closeModal();
    } catch (error) {
      if (!error?.errorFields) {
        message.error(
          extractErrorMessage(error)
        );
      }
    }
  };


  // ======================================================
  // START
  // ======================================================

  const handleStartOrder = async () => {
    try {
      const values = (
        await startForm.validateFields()
      );

      await executeAction(
        () => serviceOrderApi.start(
          order.id,
          {
            note:
              values.note?.trim()
              || null,
          }
        ),
        "Đơn hàng đã chuyển sang trạng thái đang thực hiện."
      );

      startForm.resetFields();
      closeModal();
    } catch (error) {
      if (!error?.errorFields) {
        message.error(
          extractErrorMessage(error)
        );
      }
    }
  };


  // ======================================================
  // DELIVER
  // ======================================================

  const handleDeliverOrder = async () => {
    try {
      const values = (
        await deliverForm.validateFields()
      );

      await executeAction(
        () => serviceOrderApi.deliver(
          order.id,
          {
            deliverable_id:
              values.deliverable_id?.trim()
              || null,

            note:
              values.note?.trim()
              || null,
          }
        ),
        "Đã đánh dấu đơn hàng là đã bàn giao."
      );

      deliverForm.resetFields();
      closeModal();
    } catch (error) {
      if (!error?.errorFields) {
        message.error(
          extractErrorMessage(error)
        );
      }
    }
  };


  // ======================================================
  // COMPLETE
  // ======================================================

  const handleCompleteOrder = async () => {
    try {
      const values = (
        await completeForm.validateFields()
      );

      await executeAction(
        () => serviceOrderApi.complete(
          order.id,
          {
            release_escrow:
              values.release_escrow
              ?? true,

            note:
              values.note?.trim()
              || null,
          }
        ),
        "Đơn hàng đã hoàn thành."
      );

      completeForm.resetFields();
      closeModal();
    } catch (error) {
      if (!error?.errorFields) {
        message.error(
          extractErrorMessage(error)
        );
      }
    }
  };


  // ======================================================
  // CANCEL
  // ======================================================

  const handleCancelOrder = async () => {
    try {
      const values = (
        await cancelForm.validateFields()
      );

      await executeAction(
        () => serviceOrderApi.cancel(
          order.id,
          {
            cancellation_reason:
              values.cancellation_reason.trim(),

            refund_escrow:
              values.refund_escrow
              ?? true,
          }
        ),
        "Đã hủy đơn hàng."
      );

      cancelForm.resetFields();
      closeModal();
    } catch (error) {
      if (!error?.errorFields) {
        message.error(
          extractErrorMessage(error)
        );
      }
    }
  };


  // ======================================================
  // DISPUTE
  // ======================================================

  const handleDisputeOrder = async () => {
    try {
      const values = (
        await disputeForm.validateFields()
      );

      await executeAction(
        () => serviceOrderApi.dispute(
          order.id,
          {
            reason:
              values.reason,

            description:
              values.description.trim(),

            evidence_url:
              values.evidence_url?.trim()
              || null,
          }
        ),
        "Đã mở tranh chấp cho đơn hàng."
      );

      disputeForm.resetFields();
      closeModal();
    } catch (error) {
      if (!error?.errorFields) {
        message.error(
          extractErrorMessage(error)
        );
      }
    }
  };


  // ======================================================
  // FINAL STATUS MESSAGE
  // ======================================================

  const renderFinalStatus = () => {
    if (status === "COMPLETED") {
      return (
        <Alert
          type="success"
          showIcon
          icon={<CheckCircleOutlined />}
          message="Đơn hàng đã hoàn thành"
          description={
            "Quy trình thực hiện đã kết thúc. "
            + "Escrow có thể đã được giải ngân cho chuyên gia."
          }
        />
      );
    }

    if (status === "DISPUTED") {
      return (
        <Alert
          type="error"
          showIcon
          icon={<WarningOutlined />}
          message="Đơn hàng đang tranh chấp"
          description={
            "Các thao tác nghiệp vụ thông thường "
            + "được tạm dừng cho đến khi Admin xử lý."
          }
        />
      );
    }

    if (status === "CANCELLED") {
      return (
        <Alert
          type="warning"
          showIcon
          icon={<StopOutlined />}
          message="Đơn hàng đã bị hủy"
          description={
            order?.cancellation_reason
            || "Chưa có lý do hủy."
          }
        />
      );
    }

    if (status === "REFUNDED") {
      return (
        <Alert
          type="info"
          showIcon
          icon={<SafetyCertificateOutlined />}
          message="Đơn hàng đã hoàn tiền"
          description={
            order?.cancellation_reason
            || "Khoản Escrow đã được hoàn lại."
          }
        />
      );
    }

    return null;
  };


  // ======================================================
  // RENDER
  // ======================================================

  return (
    <>
      <Card
        title={
          <Space>
            <ExclamationCircleOutlined />
            <span>Thao tác đơn hàng</span>
          </Space>
        }
        style={{
          marginTop: 24,
        }}
        extra={
          <Tag color={statusColor}>
            {statusLabel}
          </Tag>
        }
      >
        {renderFinalStatus()}

        {hasAnyAction && (
          <>
            <Paragraph
              type="secondary"
              style={{
                marginBottom: 18,
              }}
            >
              Các nút bên dưới được hiển thị theo trạng thái
              hiện tại của đơn hàng.
            </Paragraph>

            <Row gutter={[12, 12]}>
              {permissions.canConfirm && (
                <Col
                  xs={24}
                  sm={12}
                  lg={8}
                >
                  <Button
                    type="primary"
                    block
                    size="large"
                    icon={<CheckCircleOutlined />}
                    loading={actionLoading}
                    onClick={() => {
                      setActiveModal(
                        "confirm"
                      );
                    }}
                  >
                    Xác nhận đơn
                  </Button>
                </Col>
              )}

              {permissions.canStart && (
                <Col
                  xs={24}
                  sm={12}
                  lg={8}
                >
                  <Button
                    type="primary"
                    block
                    size="large"
                    icon={<PlayCircleOutlined />}
                    loading={actionLoading}
                    onClick={() => {
                      setActiveModal(
                        "start"
                      );
                    }}
                  >
                    Bắt đầu thực hiện
                  </Button>
                </Col>
              )}

              {permissions.canDeliver && (
                <Col
                  xs={24}
                  sm={12}
                  lg={8}
                >
                  <Button
                    type="primary"
                    block
                    size="large"
                    icon={<FileDoneOutlined />}
                    loading={actionLoading}
                    onClick={() => {
                      setActiveModal(
                        "deliver"
                      );
                    }}
                  >
                    Bàn giao kết quả
                  </Button>
                </Col>
              )}

              {permissions.canComplete && (
                <Col
                  xs={24}
                  sm={12}
                  lg={8}
                >
                  <Button
                    type="primary"
                    block
                    size="large"
                    icon={<CheckCircleOutlined />}
                    loading={actionLoading}
                    onClick={() => {
                      setActiveModal(
                        "complete"
                      );
                    }}
                  >
                    Hoàn thành đơn
                  </Button>
                </Col>
              )}

              {permissions.canCancel && (
                <Col
                  xs={24}
                  sm={12}
                  lg={8}
                >
                  <Button
                    danger
                    block
                    size="large"
                    icon={<CloseCircleOutlined />}
                    loading={actionLoading}
                    onClick={() => {
                      setActiveModal(
                        "cancel"
                      );
                    }}
                  >
                    Hủy đơn hàng
                  </Button>
                </Col>
              )}

              {permissions.canDispute && (
                <Col
                  xs={24}
                  sm={12}
                  lg={8}
                >
                  <Button
                    danger
                    ghost
                    block
                    size="large"
                    icon={<WarningOutlined />}
                    loading={actionLoading}
                    onClick={() => {
                      setActiveModal(
                        "dispute"
                      );
                    }}
                  >
                    Mở tranh chấp
                  </Button>
                </Col>
              )}
            </Row>
          </>
        )}

        {!hasAnyAction && ![
          "COMPLETED",
          "DISPUTED",
          "CANCELLED",
          "REFUNDED",
        ].includes(status) && (
          <Alert
            type="info"
            showIcon
            message="Không có thao tác khả dụng"
            description={
              "Trạng thái hiện tại không hỗ trợ "
              + "thao tác nghiệp vụ từ giao diện này."
            }
          />
        )}
      </Card>


      {/* ==================================================
          CONFIRM MODAL
      ================================================== */}

      <Modal
        open={activeModal === "confirm"}
        title="Xác nhận đơn hàng"
        okText="Xác nhận"
        cancelText="Đóng"
        confirmLoading={actionLoading}
        onOk={handleConfirmOrder}
        onCancel={closeModal}
        destroyOnHidden
      >
        <Alert
          type="info"
          showIcon
          message="Liên kết thanh toán và Escrow"
          description={
            "Bạn có thể để trống Payment ID và Wallet ID "
            + "nếu đơn chưa có giao dịch tài chính."
          }
          style={{
            marginBottom: 18,
          }}
        />

        <Form
          form={confirmForm}
          layout="vertical"
        >
          <Form.Item
            name="payment_id"
            label="Payment ID"
          >
            <Input
              placeholder="UUID của giao dịch thanh toán"
            />
          </Form.Item>

          <Form.Item
            name="payer_wallet_id"
            label="Ví thanh toán"
          >
            <Input
              placeholder="UUID của ví doanh nghiệp"
            />
          </Form.Item>

          <Form.Item
            name="note"
            label="Ghi chú"
            rules={[
              {
                max: 5000,
                message:
                  "Ghi chú không được vượt quá 5.000 ký tự.",
              },
            ]}
          >
            <TextArea
              rows={4}
              maxLength={5000}
              showCount
            />
          </Form.Item>
        </Form>
      </Modal>


      {/* ==================================================
          START MODAL
      ================================================== */}

      <Modal
        open={activeModal === "start"}
        title="Bắt đầu thực hiện đơn hàng"
        okText="Bắt đầu"
        cancelText="Đóng"
        confirmLoading={actionLoading}
        onOk={handleStartOrder}
        onCancel={closeModal}
        destroyOnHidden
      >
        <Form
          form={startForm}
          layout="vertical"
        >
          <Form.Item
            name="note"
            label="Ghi chú bắt đầu"
            rules={[
              {
                max: 5000,
                message:
                  "Ghi chú không được vượt quá 5.000 ký tự.",
              },
            ]}
          >
            <TextArea
              rows={5}
              maxLength={5000}
              showCount
              placeholder={
                "Ví dụ: Đã tiếp nhận yêu cầu và bắt đầu "
                + "phân tích dữ liệu..."
              }
            />
          </Form.Item>
        </Form>
      </Modal>


      {/* ==================================================
          DELIVER MODAL
      ================================================== */}

      <Modal
        open={activeModal === "deliver"}
        title="Bàn giao kết quả"
        okText="Xác nhận bàn giao"
        cancelText="Đóng"
        confirmLoading={actionLoading}
        onOk={handleDeliverOrder}
        onCancel={closeModal}
        destroyOnHidden
      >
        <Alert
          type="warning"
          showIcon
          message="Kiểm tra sản phẩm trước khi bàn giao"
          description={
            "Deliverable ID có thể để trống nếu sản phẩm "
            + "được gửi bằng phương thức khác."
          }
          style={{
            marginBottom: 18,
          }}
        />

        <Form
          form={deliverForm}
          layout="vertical"
        >
          <Form.Item
            name="deliverable_id"
            label="Deliverable ID"
          >
            <Input
              placeholder="UUID sản phẩm bàn giao"
            />
          </Form.Item>

          <Form.Item
            name="note"
            label="Nội dung bàn giao"
            rules={[
              {
                max: 5000,
                message:
                  "Nội dung không được vượt quá 5.000 ký tự.",
              },
            ]}
          >
            <TextArea
              rows={5}
              maxLength={5000}
              showCount
              placeholder={
                "Mô tả phiên bản, đường dẫn tải, "
                + "tài khoản dùng thử hoặc hướng dẫn kiểm tra..."
              }
            />
          </Form.Item>
        </Form>
      </Modal>


      {/* ==================================================
          COMPLETE MODAL
      ================================================== */}

      <Modal
        open={activeModal === "complete"}
        title="Hoàn thành đơn hàng"
        okText="Hoàn thành"
        cancelText="Đóng"
        confirmLoading={actionLoading}
        onOk={handleCompleteOrder}
        onCancel={closeModal}
        destroyOnHidden
      >
        <Alert
          type="success"
          showIcon
          message="Xác nhận nghiệm thu"
          description={
            "Khi bật giải ngân Escrow, hệ thống sẽ chuyển "
            + "số tiền còn lại cho chuyên gia."
          }
          style={{
            marginBottom: 18,
          }}
        />

        <Form
          form={completeForm}
          layout="vertical"
          initialValues={{
            release_escrow: true,
          }}
        >
          <Form.Item
            name="release_escrow"
            valuePropName="checked"
          >
            <Checkbox>
              Giải ngân toàn bộ Escrow còn lại
            </Checkbox>
          </Form.Item>

          <Form.Item
            name="note"
            label="Ghi chú nghiệm thu"
            rules={[
              {
                max: 5000,
                message:
                  "Ghi chú không được vượt quá 5.000 ký tự.",
              },
            ]}
          >
            <TextArea
              rows={5}
              maxLength={5000}
              showCount
              placeholder={
                "Ví dụ: Sản phẩm đáp ứng yêu cầu và "
                + "được chấp nhận nghiệm thu."
              }
            />
          </Form.Item>
        </Form>
      </Modal>


      {/* ==================================================
          CANCEL MODAL
      ================================================== */}

      <Modal
        open={activeModal === "cancel"}
        title="Hủy đơn hàng"
        okText="Xác nhận hủy"
        okButtonProps={{
          danger: true,
        }}
        cancelText="Đóng"
        confirmLoading={actionLoading}
        onOk={handleCancelOrder}
        onCancel={closeModal}
        destroyOnHidden
      >
        <Alert
          type="error"
          showIcon
          message="Thao tác này ảnh hưởng đến quy trình đơn hàng"
          description={
            "Hãy nhập lý do rõ ràng. Nếu có Escrow, "
            + "bạn có thể yêu cầu hoàn tiền."
          }
          style={{
            marginBottom: 18,
          }}
        />

        <Form
          form={cancelForm}
          layout="vertical"
          initialValues={{
            refund_escrow: true,
          }}
        >
          <Form.Item
            name="cancellation_reason"
            label="Lý do hủy"
            rules={[
              {
                required: true,
                message:
                  "Vui lòng nhập lý do hủy.",
              },
              {
                min: 3,
                message:
                  "Lý do hủy phải có ít nhất 3 ký tự.",
              },
              {
                max: 5000,
                message:
                  "Lý do không được vượt quá 5.000 ký tự.",
              },
            ]}
          >
            <TextArea
              rows={5}
              maxLength={5000}
              showCount
              placeholder="Nhập lý do hủy đơn hàng..."
            />
          </Form.Item>

          <Form.Item
            name="refund_escrow"
            valuePropName="checked"
          >
            <Checkbox>
              Hoàn tiền Escrow nếu có
            </Checkbox>
          </Form.Item>
        </Form>
      </Modal>


      {/* ==================================================
          DISPUTE MODAL
      ================================================== */}

      <Modal
        open={activeModal === "dispute"}
        title="Mở tranh chấp"
        okText="Gửi tranh chấp"
        okButtonProps={{
          danger: true,
        }}
        cancelText="Đóng"
        confirmLoading={actionLoading}
        onOk={handleDisputeOrder}
        onCancel={closeModal}
        destroyOnHidden
      >
        <Alert
          type="warning"
          showIcon
          message="Escrow có thể bị khóa"
          description={
            "Sau khi mở tranh chấp, Admin sẽ xem xét "
            + "thông tin và bằng chứng của các bên."
          }
          style={{
            marginBottom: 18,
          }}
        />

        <Form
          form={disputeForm}
          layout="vertical"
        >
          <Form.Item
            name="reason"
            label="Loại tranh chấp"
            rules={[
              {
                required: true,
                message:
                  "Vui lòng chọn loại tranh chấp.",
              },
            ]}
          >
            <Select
              placeholder="Chọn nguyên nhân"
              options={[
                {
                  value: "QUALITY",
                  label: "Chất lượng không đạt",
                },
                {
                  value: "DELAY",
                  label: "Chậm tiến độ",
                },
                {
                  value: "SCOPE",
                  label: "Không đúng phạm vi",
                },
                {
                  value: "PAYMENT",
                  label: "Vấn đề thanh toán",
                },
                {
                  value: "COMMUNICATION",
                  label: "Vấn đề trao đổi",
                },
                {
                  value: "OTHER",
                  label: "Nguyên nhân khác",
                },
              ]}
            />
          </Form.Item>

          <Form.Item
            name="description"
            label="Mô tả tranh chấp"
            rules={[
              {
                required: true,
                message:
                  "Vui lòng mô tả tranh chấp.",
              },
              {
                min: 10,
                message:
                  "Mô tả phải có ít nhất 10 ký tự.",
              },
              {
                max: 5000,
                message:
                  "Mô tả không được vượt quá 5.000 ký tự.",
              },
            ]}
          >
            <TextArea
              rows={6}
              maxLength={5000}
              showCount
              placeholder={
                "Mô tả sự việc, kết quả mong muốn "
                + "và các bước đã trao đổi trước đó..."
              }
            />
          </Form.Item>

          <Form.Item
            name="evidence_url"
            label="Đường dẫn bằng chứng"
            rules={[
              {
                type: "url",
                warningOnly: true,
                message:
                  "Đường dẫn có thể không đúng định dạng URL.",
              },
              {
                max: 500,
                message:
                  "URL không được vượt quá 500 ký tự.",
              },
            ]}
          >
            <Input
              placeholder="https://..."
            />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}


export default OrderActions;