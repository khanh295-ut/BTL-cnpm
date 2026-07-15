import React, {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  Alert,
  App,
  Avatar,
  Breadcrumb,
  Button,
  Card,
  Col,
  Descriptions,
  Divider,
  Empty,
  Flex,
  Form,
  Input,
  Result,
  Row,
  Select,
  Space,
  Spin,
  Statistic,
  Tag,
  Typography,
} from "antd";

import {
  ArrowLeftOutlined,
  CalendarOutlined,
  CheckCircleOutlined,
  DollarOutlined,
  FileTextOutlined,
  LoadingOutlined,
  RocketOutlined,
  SaveOutlined,
  ShopOutlined,
  ShoppingCartOutlined,
  UserOutlined,
} from "@ant-design/icons";

import {
  useLocation,
  useNavigate,
} from "react-router-dom";

import aiServiceApi from "../api/aiServiceApi";
import enterpriseApi from "../api/enterpriseApi";
import serviceOrderApi from "../api/serviceOrderApi";


const {
  Title,
  Text,
  Paragraph,
} = Typography;

const {
  TextArea,
} = Input;


/**
 * Hỗ trợ hai kiểu axiosClient:
 *
 * 1. Trả về toàn bộ AxiosResponse.
 * 2. Interceptor đã trả trực tiếp response.data.
 */
const normalizeApiResponse = (response) => {
  if (!response) {
    return null;
  }

  return response.data ?? response;
};


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

  if (error?.response?.status === 404) {
    return "Không tìm thấy dữ liệu yêu cầu.";
  }

  return (
    error?.message
    || "Không thể tạo đơn đặt dịch vụ."
  );
};


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


const getQueryParameter = (
  search,
  key
) => {
  const params = new URLSearchParams(
    search
  );

  return params.get(key);
};


const readSelectedService = () => {
  try {
    const rawValue = localStorage.getItem(
      "aitasker_selected_ai_service"
    );

    if (!rawValue) {
      return null;
    }

    return JSON.parse(rawValue);
  } catch {
    return null;
  }
};


function CreateServiceOrder() {
  const navigate = useNavigate();
  const location = useLocation();

  const {
    message,
    modal,
  } = App.useApp();

  const [form] = Form.useForm();

  const [service, setService] = useState(null);
  const [enterprises, setEnterprises] = useState([]);

  const [loadingService, setLoadingService] =
    useState(true);

  const [loadingEnterprises, setLoadingEnterprises] =
    useState(true);

  const [submitting, setSubmitting] = useState(false);

  const [error, setError] = useState("");

  const serviceIdFromQuery = useMemo(
    () => getQueryParameter(
      location.search,
      "service_id"
    ),
    [location.search]
  );


  // ======================================================
  // LOAD SERVICE
  // ======================================================

  useEffect(() => {
    const loadService = async () => {
      setLoadingService(true);
      setError("");

      try {
        const storedService =
          readSelectedService();

        const targetServiceId = (
          serviceIdFromQuery
          || storedService?.service_id
          || storedService?.id
        );

        if (!targetServiceId) {
          throw new Error(
            "Chưa chọn dịch vụ AI để đặt hàng."
          );
        }

        /*
         * Nếu localStorage chứa đúng dịch vụ đã chọn,
         * dùng trước để giao diện hiển thị nhanh.
         */
        if (
          storedService
          && String(
            storedService.id
            || storedService.service_id
          ) === String(targetServiceId)
        ) {
          setService(storedService);
        }

        /*
         * Gọi backend để lấy dữ liệu chính xác mới nhất.
         */
        const response = await aiServiceApi.getById(
          targetServiceId
        );

        const data = normalizeApiResponse(
          response
        );

        if (!data?.id) {
          throw new Error(
            "Backend không trả về dịch vụ hợp lệ."
          );
        }

        setService(data);
      } catch (requestError) {
        setService(null);

        setError(
          extractErrorMessage(
            requestError
          )
        );
      } finally {
        setLoadingService(false);
      }
    };

    loadService();
  }, [serviceIdFromQuery]);


  // ======================================================
  // LOAD ENTERPRISES
  // ======================================================

  useEffect(() => {
    const loadEnterprises = async () => {
      setLoadingEnterprises(true);

      try {
        /*
         * File enterpriseApi của bạn thường có getAll().
         * Đoạn này cũng hỗ trợ getEnterprises() nếu tên cũ.
         */
        let response;

        if (
          typeof enterpriseApi.getAll
          === "function"
        ) {
          response = await enterpriseApi.getAll();
        } else if (
          typeof enterpriseApi.getEnterprises
          === "function"
        ) {
          response =
            await enterpriseApi.getEnterprises();
        } else {
          throw new Error(
            "enterpriseApi chưa có hàm lấy danh sách."
          );
        }

        const data = normalizeApiResponse(
          response
        );

        const items = Array.isArray(data)
          ? data
          : Array.isArray(data?.items)
            ? data.items
            : [];

        setEnterprises(items);

        /*
         * Tự chọn Enterprise đầu tiên để thuận tiện test.
         */
        if (items.length > 0) {
          const currentEnterpriseId =
            form.getFieldValue(
              "enterprise_id"
            );

          if (!currentEnterpriseId) {
            form.setFieldValue(
              "enterprise_id",
              items[0].id
            );
          }
        }
      } catch (requestError) {
        setEnterprises([]);

        message.warning(
          "Không thể tải danh sách doanh nghiệp."
        );
      } finally {
        setLoadingEnterprises(false);
      }
    };

    loadEnterprises();
  }, [
    form,
    message,
  ]);


  // ======================================================
  // ACTIONS
  // ======================================================

  const handleBack = () => {
    if (service?.slug) {
      navigate(
        `/ai-services/${encodeURIComponent(
          service.slug
        )}`
      );

      return;
    }

    navigate("/ai-services");
  };


  const handleSubmit = async () => {
    if (!service?.id) {
      message.error(
        "Chưa có dịch vụ hợp lệ."
      );

      return;
    }

    try {
      const values =
        await form.validateFields();

      modal.confirm({
        title: "Xác nhận đặt dịch vụ",
        icon: <ShoppingCartOutlined />,
        content: (
          <Space
            direction="vertical"
            size={6}
          >
            <Text>
              Dịch vụ:{" "}
              <Text strong>
                {service.title}
              </Text>
            </Text>

            <Text>
              Giá trị:{" "}
              <Text strong>
                {formatCurrency(
                  service.price,
                  service.currency
                )}
              </Text>
            </Text>

            <Text type="secondary">
              Đơn hàng sẽ được tạo ở trạng thái
              PENDING.
            </Text>
          </Space>
        ),
        okText: "Tạo đơn hàng",
        cancelText: "Kiểm tra lại",
        onOk: async () => {
          setSubmitting(true);
          setError("");

          try {
            const payload = {
              service_id: service.id,
              enterprise_id:
                values.enterprise_id,
              requirements:
                values.requirements?.trim()
                || null,
              note:
                values.note?.trim()
                || null,
            };

            const response =
              await serviceOrderApi.create(
                payload
              );

            const createdOrder =
              normalizeApiResponse(
                response
              );

            if (!createdOrder?.id) {
              throw new Error(
                "Backend không trả về đơn hàng hợp lệ."
              );
            }

            localStorage.removeItem(
              "aitasker_selected_ai_service"
            );

            localStorage.setItem(
              "aitasker_last_service_order",
              JSON.stringify(createdOrder)
            );

            message.success(
              "Đã tạo đơn đặt dịch vụ thành công."
            );

            navigate(
              `/service-orders/${createdOrder.id}`
            );
          } catch (requestError) {
            const errorMessage =
              extractErrorMessage(
                requestError
              );

            setError(errorMessage);
            message.error(errorMessage);

            throw requestError;
          } finally {
            setSubmitting(false);
          }
        },
      });
    } catch (validationError) {
      if (validationError?.errorFields) {
        message.warning(
          "Vui lòng kiểm tra lại thông tin đơn hàng."
        );
      }
    }
  };


  const handleSaveDraft = async () => {
    const values = form.getFieldsValue();

    localStorage.setItem(
      "aitasker_service_order_draft",
      JSON.stringify({
        service_id: service?.id || null,
        enterprise_id:
          values.enterprise_id || null,
        requirements:
          values.requirements || "",
        note: values.note || "",
      })
    );

    message.success(
      "Đã lưu bản nháp đơn hàng."
    );
  };


  // ======================================================
  // RESTORE DRAFT
  // ======================================================

  useEffect(() => {
    try {
      const rawDraft = localStorage.getItem(
        "aitasker_service_order_draft"
      );

      if (!rawDraft) {
        return;
      }

      const draft = JSON.parse(rawDraft);

      if (
        draft?.service_id
        && serviceIdFromQuery
        && String(draft.service_id)
          !== String(serviceIdFromQuery)
      ) {
        return;
      }

      form.setFieldsValue({
        enterprise_id:
          draft.enterprise_id || undefined,
        requirements:
          draft.requirements || "",
        note:
          draft.note || "",
      });
    } catch {
      localStorage.removeItem(
        "aitasker_service_order_draft"
      );
    }
  }, [
    form,
    serviceIdFromQuery,
  ]);


  // ======================================================
  // LOADING
  // ======================================================

  if (loadingService) {
    return (
      <Card>
        <Flex
          vertical
          align="center"
          justify="center"
          gap={18}
          style={{
            minHeight: 420,
          }}
        >
          <Spin
            indicator={
              <LoadingOutlined
                style={{
                  fontSize: 54,
                }}
                spin
              />
            }
          />

          <Text type="secondary">
            Đang tải thông tin dịch vụ...
          </Text>
        </Flex>
      </Card>
    );
  }


  // ======================================================
  // ERROR
  // ======================================================

  if (!service) {
    return (
      <Card>
        <Result
          status="404"
          title="Không thể tạo đơn hàng"
          subTitle={
            error
            || "Bạn chưa chọn dịch vụ AI."
          }
          extra={[
            <Button
              key="marketplace"
              type="primary"
              icon={<RocketOutlined />}
              onClick={() => navigate(
                "/ai-services"
              )}
            >
              Mở AI Marketplace
            </Button>,

            <Button
              key="back"
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate(-1)}
            >
              Quay lại
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
      <Breadcrumb
        style={{
          marginBottom: 20,
        }}
        items={[
          {
            title: (
              <span
                style={{
                  cursor: "pointer",
                }}
                onClick={() => navigate(
                  "/dashboard"
                )}
              >
                Tổng quan
              </span>
            ),
          },
          {
            title: (
              <span
                style={{
                  cursor: "pointer",
                }}
                onClick={() => navigate(
                  "/ai-services"
                )}
              >
                Dịch vụ AI
              </span>
            ),
          },
          {
            title: "Đặt dịch vụ",
          },
        ]}
      />

      <Card
        bordered={false}
        style={{
          marginBottom: 24,
          background:
            "linear-gradient(135deg, #111827 0%, #1e1b4b 55%, #312e81 100%)",
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
              size={8}
            >
              <Tag color="purple">
                Service Order
              </Tag>

              <Title
                level={2}
                style={{
                  margin: 0,
                  color: "#ffffff",
                }}
              >
                <ShoppingCartOutlined />
                {" "}Đặt dịch vụ AI
              </Title>

              <Paragraph
                style={{
                  margin: 0,
                  maxWidth: 760,
                  color: "#cbd5e1",
                  fontSize: 15,
                  lineHeight: 1.7,
                }}
              >
                Cung cấp yêu cầu chi tiết để chuyên gia
                hiểu rõ mục tiêu và phạm vi công việc.
                Giá dịch vụ sẽ được giữ nguyên tại thời
                điểm tạo đơn.
              </Paragraph>
            </Space>
          </Col>

          <Col
            xs={24}
            lg="auto"
          >
            <Button
              size="large"
              icon={<ArrowLeftOutlined />}
              onClick={handleBack}
            >
              Quay lại dịch vụ
            </Button>
          </Col>
        </Row>
      </Card>

      {error && (
        <Alert
          type="error"
          showIcon
          closable
          message="Không thể tạo đơn hàng"
          description={error}
          style={{
            marginBottom: 20,
          }}
          onClose={() => setError("")}
        />
      )}

      <Row gutter={[24, 24]}>
        {/* =================================================
            ORDER FORM
        ================================================= */}

        <Col
          xs={24}
          xl={15}
        >
          <Card
            title={
              <Space>
                <FileTextOutlined />
                <span>Thông tin đặt hàng</span>
              </Space>
            }
          >
            <Form
              form={form}
              layout="vertical"
              initialValues={{
                enterprise_id: undefined,
                requirements: "",
                note: "",
              }}
              disabled={submitting}
            >
              <Form.Item
                name="enterprise_id"
                label="Doanh nghiệp đặt dịch vụ"
                rules={[
                  {
                    required: true,
                    message:
                      "Vui lòng chọn doanh nghiệp.",
                  },
                ]}
              >
                <Select
                  showSearch
                  loading={loadingEnterprises}
                  placeholder="Chọn doanh nghiệp"
                  optionFilterProp="label"
                  notFoundContent={
                    loadingEnterprises
                      ? <Spin size="small" />
                      : (
                        <Empty
                          image={
                            Empty.PRESENTED_IMAGE_SIMPLE
                          }
                          description={
                            "Chưa có doanh nghiệp."
                          }
                        />
                      )
                  }
                  options={enterprises.map(
                    (enterprise) => ({
                      value: enterprise.id,
                      label: (
                        enterprise.name
                        || enterprise.company_name
                        || enterprise.email
                        || enterprise.id
                      ),
                    })
                  )}
                  suffixIcon={<ShopOutlined />}
                />
              </Form.Item>

              <Form.Item
                name="requirements"
                label="Yêu cầu chi tiết"
                tooltip={
                  "Mô tả dữ liệu, chức năng, tích hợp "
                  + "và kết quả bạn mong muốn."
                }
                rules={[
                  {
                    max: 10000,
                    message:
                      "Yêu cầu không được vượt quá "
                      + "10.000 ký tự.",
                  },
                ]}
              >
                <TextArea
                  rows={8}
                  showCount
                  maxLength={10000}
                  placeholder={
                    "Ví dụ: Chatbot cần tích hợp dữ liệu "
                    + "tuyển sinh, trả lời bằng tiếng Việt, "
                    + "lưu lịch sử hội thoại và có trang "
                    + "quản trị câu hỏi..."
                  }
                />
              </Form.Item>

              <Form.Item
                name="note"
                label="Ghi chú bổ sung"
                rules={[
                  {
                    max: 5000,
                    message:
                      "Ghi chú không được vượt quá "
                      + "5.000 ký tự.",
                  },
                ]}
              >
                <TextArea
                  rows={4}
                  showCount
                  maxLength={5000}
                  placeholder={
                    "Thời gian họp, yêu cầu ưu tiên hoặc "
                    + "thông tin cần lưu ý..."
                  }
                />
              </Form.Item>

              <Alert
                type="info"
                showIcon
                message="Quy trình sau khi tạo đơn"
                description={
                  <Space
                    direction="vertical"
                    size={4}
                  >
                    <Text>
                      1. Đơn được tạo ở trạng thái
                      PENDING.
                    </Text>

                    <Text>
                      2. Admin hoặc doanh nghiệp xác nhận
                      thanh toán và Escrow.
                    </Text>

                    <Text>
                      3. Chuyên gia bắt đầu thực hiện và
                      bàn giao kết quả.
                    </Text>

                    <Text>
                      4. Doanh nghiệp nghiệm thu và hệ
                      thống giải ngân.
                    </Text>
                  </Space>
                }
              />

              <Divider />

              <Flex
                gap={12}
                wrap="wrap"
              >
                <Button
                  type="primary"
                  size="large"
                  icon={<ShoppingCartOutlined />}
                  loading={submitting}
                  onClick={handleSubmit}
                >
                  Tạo đơn đặt dịch vụ
                </Button>

                <Button
                  size="large"
                  icon={<SaveOutlined />}
                  disabled={submitting}
                  onClick={handleSaveDraft}
                >
                  Lưu bản nháp
                </Button>

                <Button
                  size="large"
                  icon={<ArrowLeftOutlined />}
                  disabled={submitting}
                  onClick={handleBack}
                >
                  Hủy
                </Button>
              </Flex>
            </Form>
          </Card>
        </Col>


        {/* =================================================
            SERVICE SUMMARY
        ================================================= */}

        <Col
          xs={24}
          xl={9}
        >
          <div
            style={{
              position: "sticky",
              top: 94,
            }}
          >
            <Card
              title={
                <Space>
                  <RocketOutlined />
                  <span>Dịch vụ đã chọn</span>
                </Space>
              }
              style={{
                marginBottom: 20,
              }}
            >
              <Space
                direction="vertical"
                size={18}
                style={{
                  width: "100%",
                }}
              >
                <Flex
                  align="center"
                  gap={14}
                >
                  <Avatar
                    size={58}
                    shape="square"
                    src={service.image_url}
                    icon={<RocketOutlined />}
                    style={{
                      background:
                        "linear-gradient(135deg, #4f46e5, #7c3aed)",
                    }}
                  />

                  <div
                    style={{
                      flex: 1,
                      minWidth: 0,
                    }}
                  >
                    <Title
                      level={4}
                      ellipsis={{
                        rows: 2,
                      }}
                      style={{
                        margin: 0,
                      }}
                    >
                      {service.title}
                    </Title>

                    <Text type="secondary">
                      {service.short_description
                        || "Dịch vụ AI"}
                    </Text>
                  </div>
                </Flex>

                <Divider
                  style={{
                    margin: 0,
                  }}
                />

                <Statistic
                  title="Tổng giá trị đơn hàng"
                  value={Number(
                    service.price || 0
                  )}
                  precision={0}
                  prefix={<DollarOutlined />}
                  suffix={
                    service.currency || "VND"
                  }
                  formatter={(value) => (
                    Number(value).toLocaleString(
                      "vi-VN"
                    )
                  )}
                />

                <Descriptions
                  bordered
                  size="small"
                  column={1}
                >
                  <Descriptions.Item
                    label="Chuyên gia"
                  >
                    <Space>
                      <UserOutlined />

                      {service.expert?.full_name
                        || service.expert_name
                        || "Chuyên gia AI"}
                    </Space>
                  </Descriptions.Item>

                  <Descriptions.Item
                    label="Thời gian"
                  >
                    <Space>
                      <CalendarOutlined />

                      {service.delivery_days} ngày
                    </Space>
                  </Descriptions.Item>

                  <Descriptions.Item
                    label="Số lần chỉnh sửa"
                  >
                    {service.revision_count || 0}
                  </Descriptions.Item>

                  <Descriptions.Item
                    label="Trạng thái"
                  >
                    <Tag color="green">
                      {service.status
                        || "PUBLISHED"}
                    </Tag>
                  </Descriptions.Item>
                </Descriptions>

                {Array.isArray(service.skills)
                  && service.skills.length > 0 && (
                  <div>
                    <Text
                      strong
                      style={{
                        display: "block",
                        marginBottom: 10,
                      }}
                    >
                      Kỹ năng
                    </Text>

                    <Flex
                      gap={6}
                      wrap="wrap"
                    >
                      {service.skills
                        .slice(0, 6)
                        .map((skill, index) => (
                          <Tag
                            key={`${skill}-${index}`}
                            color="blue"
                            style={{
                              marginInlineEnd: 0,
                            }}
                          >
                            {skill}
                          </Tag>
                        ))}
                    </Flex>
                  </div>
                )}

                <Alert
                  type="success"
                  showIcon
                  icon={<CheckCircleOutlined />}
                  message="Giá được cố định"
                  description={
                    "Giá, thời gian và số lần chỉnh sửa "
                    + "được lưu lại khi đơn hàng được tạo."
                  }
                />
              </Space>
            </Card>

            <Card>
              <Space
                direction="vertical"
                size={8}
              >
                <Text strong>
                  Thanh toán an toàn với Escrow
                </Text>

                <Text type="secondary">
                  Tiền chỉ được giải ngân cho chuyên gia
                  sau khi doanh nghiệp xác nhận hoàn thành.
                </Text>
              </Space>
            </Card>
          </div>
        </Col>
      </Row>
    </div>
  );
}


export default CreateServiceOrder;