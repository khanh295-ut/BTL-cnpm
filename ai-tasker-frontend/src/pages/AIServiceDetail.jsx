import React, {
  useCallback,
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
  Image,
  List,
  Result,
  Row,
  Skeleton,
  Space,
  Statistic,
  Tag,
  Typography,
} from "antd";

import {
  ArrowLeftOutlined,
  CalendarOutlined,
  CheckCircleOutlined,
  CodeOutlined,
  DollarOutlined,
  EyeOutlined,
  FileDoneOutlined,
  GlobalOutlined,
  LinkOutlined,
  ReloadOutlined,
  RocketOutlined,
  SafetyCertificateOutlined,
  ShoppingCartOutlined,
  StarFilled,
  ToolOutlined,
  UserOutlined,
} from "@ant-design/icons";

import {
  useNavigate,
  useParams,
} from "react-router-dom";

import aiServiceApi from "../api/aiServiceApi";


const {
  Title,
  Text,
  Paragraph,
} = Typography;


/**
 * Hỗ trợ cả hai kiểu axiosClient:
 *
 * 1. Trả nguyên AxiosResponse.
 * 2. Interceptor đã trả response.data.
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
    return "Không tìm thấy dịch vụ AI.";
  }

  return (
    error?.message
    || "Không thể tải thông tin dịch vụ AI."
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


const isFeaturedService = (value) => (
  String(value || "")
    .trim()
    .toUpperCase()
  === "YES"
);


const StringTagList = ({
  items,
  color = "blue",
  emptyText = "Chưa có dữ liệu.",
}) => {
  if (!Array.isArray(items) || items.length === 0) {
    return (
      <Text type="secondary">
        {emptyText}
      </Text>
    );
  }

  return (
    <Flex
      wrap="wrap"
      gap={8}
    >
      {items.map((item, index) => (
        <Tag
          key={`${item}-${index}`}
          color={color}
          style={{
            marginInlineEnd: 0,
            padding: "5px 11px",
            borderRadius: 999,
          }}
        >
          {item}
        </Tag>
      ))}
    </Flex>
  );
};


const StringList = ({
  items,
  icon,
  emptyText = "Chưa có dữ liệu.",
}) => {
  if (!Array.isArray(items) || items.length === 0) {
    return (
      <Empty
        image={Empty.PRESENTED_IMAGE_SIMPLE}
        description={emptyText}
      />
    );
  }

  return (
    <List
      size="small"
      split={false}
      dataSource={items}
      renderItem={(item) => (
        <List.Item>
          <Space align="start">
            {icon}

            <Text
              style={{
                lineHeight: 1.7,
              }}
            >
              {item}
            </Text>
          </Space>
        </List.Item>
      )}
    />
  );
};


function AIServiceDetail() {
  const navigate = useNavigate();

  const {
    slug,
  } = useParams();

  const {
    message,
  } = App.useApp();

  const [service, setService] = useState(null);
  const [loading, setLoading] = useState(true);
  const [ordering, setOrdering] = useState(false);
  const [error, setError] = useState("");


  // ======================================================
  // LOAD SERVICE
  // ======================================================

  const loadService = useCallback(async () => {
    if (!slug) {
      setError(
        "Đường dẫn dịch vụ không hợp lệ."
      );

      setLoading(false);
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = (
        await aiServiceApi.getMarketplaceDetail(
          slug,
          true
        )
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
      setLoading(false);
    }
  }, [slug]);


  useEffect(() => {
    loadService();
  }, [loadService]);


  // ======================================================
  // DERIVED VALUES
  // ======================================================

  const featured = useMemo(
    () => isFeaturedService(
      service?.is_featured
    ),
    [service]
  );


  const serviceStatus = useMemo(
    () => String(
      service?.status || ""
    ).trim().toUpperCase(),
    [service]
  );


  // ======================================================
  // ACTIONS
  // ======================================================

  const handleBack = () => {
    navigate("/ai-services");
  };


  const handleOrder = async () => {
    if (!service?.id) {
      message.error(
        "Dịch vụ không hợp lệ."
      );

      return;
    }

    if (serviceStatus !== "PUBLISHED") {
      message.warning(
        "Dịch vụ này chưa sẵn sàng để đặt."
      );

      return;
    }

    setOrdering(true);

    try {
      /*
       * Lưu thông tin dịch vụ để trang tạo Service Order
       * có thể lấy lại và điền dữ liệu ban đầu.
       */
      localStorage.setItem(
        "aitasker_selected_ai_service",
        JSON.stringify({
          id: service.id,
          service_id: service.id,
          slug: service.slug,
          title: service.title,
          expert_id: service.expert_id,
          expert_name: service.expert?.full_name
            || service.expert_name
            || "Chuyên gia",
          price: service.price,
          currency: service.currency,
          delivery_days: service.delivery_days,
          revision_count: service.revision_count,
          image_url: service.image_url,
        })
      );

      message.success(
        "Đã chọn dịch vụ. Vui lòng điền thông tin đặt hàng."
      );

      navigate(
        `/service-orders/create?service_id=${service.id}`
      );
    } finally {
      setOrdering(false);
    }
  };


  const openExternalLink = (
    url,
    label
  ) => {
    if (!url) {
      message.warning(
        `${label} chưa được cung cấp.`
      );

      return;
    }

    window.open(
      url,
      "_blank",
      "noopener,noreferrer"
    );
  };


  // ======================================================
  // LOADING
  // ======================================================

  if (loading) {
    return (
      <div>
        <Skeleton
          active
          paragraph={{
            rows: 1,
          }}
          style={{
            marginBottom: 20,
          }}
        />

        <Row gutter={[24, 24]}>
          <Col
            xs={24}
            lg={16}
          >
            <Card>
              <Skeleton
                active
                paragraph={{
                  rows: 12,
                }}
              />
            </Card>
          </Col>

          <Col
            xs={24}
            lg={8}
          >
            <Card>
              <Skeleton
                active
                paragraph={{
                  rows: 8,
                }}
              />
            </Card>
          </Col>
        </Row>
      </div>
    );
  }


  // ======================================================
  // ERROR
  // ======================================================

  if (error || !service) {
    return (
      <Card>
        <Result
          status="404"
          title="Không tìm thấy dịch vụ"
          subTitle={
            error
            || "Dịch vụ không tồn tại hoặc chưa được xuất bản."
          }
          extra={[
            <Button
              key="back"
              icon={<ArrowLeftOutlined />}
              onClick={handleBack}
            >
              Quay lại Marketplace
            </Button>,

            <Button
              key="reload"
              type="primary"
              icon={<ReloadOutlined />}
              onClick={loadService}
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
                onClick={() => navigate("/dashboard")}
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
                onClick={handleBack}
              >
                Dịch vụ AI
              </span>
            ),
          },
          {
            title: service.title,
          },
        ]}
      />

      <Flex
        justify="space-between"
        align="center"
        wrap="wrap"
        gap={12}
        style={{
          marginBottom: 20,
        }}
      >
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={handleBack}
        >
          Quay lại Marketplace
        </Button>

        <Space wrap>
          <Tag
            color={
              serviceStatus === "PUBLISHED"
                ? "green"
                : "default"
            }
          >
            {serviceStatus || "UNKNOWN"}
          </Tag>

          {featured && (
            <Tag
              color="purple"
              icon={<StarFilled />}
            >
              Dịch vụ nổi bật
            </Tag>
          )}
        </Space>
      </Flex>

      <Row gutter={[24, 24]}>
        {/* =================================================
            LEFT CONTENT
        ================================================= */}

        <Col
          xs={24}
          xl={16}
        >
          <Card
            bordered={false}
            style={{
              overflow: "hidden",
            }}
            styles={{
              body: {
                padding: 0,
              },
            }}
          >
            <div
              style={{
                minHeight: 350,
                background:
                  "linear-gradient(135deg, #111827 0%, #1e1b4b 55%, #312e81 100%)",
              }}
            >
              {service.image_url ? (
                <Image
                  src={service.image_url}
                  alt={service.title}
                  width="100%"
                  height={430}
                  style={{
                    objectFit: "cover",
                  }}
                  fallback={
                    "data:image/svg+xml;charset=UTF-8,"
                    + encodeURIComponent(
                      `
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          width="1200"
                          height="600"
                        >
                          <rect
                            width="100%"
                            height="100%"
                            fill="#1e1b4b"
                          />
                          <text
                            x="50%"
                            y="50%"
                            fill="#a5b4fc"
                            font-size="42"
                            text-anchor="middle"
                          >
                            AITasker AI Service
                          </text>
                        </svg>
                      `
                    )
                  }
                />
              ) : (
                <Flex
                  vertical
                  justify="center"
                  align="center"
                  gap={18}
                  style={{
                    height: 400,
                  }}
                >
                  <RocketOutlined
                    style={{
                      color: "#a5b4fc",
                      fontSize: 76,
                    }}
                  />

                  <Text
                    style={{
                      color: "#c7d2fe",
                      fontSize: 18,
                    }}
                  >
                    AITasker AI Marketplace
                  </Text>
                </Flex>
              )}
            </div>

            <div
              style={{
                padding: 28,
              }}
            >
              <Space
                direction="vertical"
                size={14}
                style={{
                  width: "100%",
                }}
              >
                <Flex
                  justify="space-between"
                  align="flex-start"
                  wrap="wrap"
                  gap={16}
                >
                  <div
                    style={{
                      flex: 1,
                      minWidth: 260,
                    }}
                  >
                    {service.category?.name && (
                      <Tag
                        color="geekblue"
                        style={{
                          marginBottom: 12,
                        }}
                      >
                        {service.category.name}
                      </Tag>
                    )}

                    <Title
                      level={2}
                      style={{
                        margin: 0,
                      }}
                    >
                      {service.title}
                    </Title>
                  </div>

                  {featured && (
                    <Tag
                      color="purple"
                      icon={<StarFilled />}
                      style={{
                        padding: "6px 12px",
                        borderRadius: 999,
                      }}
                    >
                      Nổi bật
                    </Tag>
                  )}
                </Flex>

                <Paragraph
                  type="secondary"
                  style={{
                    margin: 0,
                    fontSize: 16,
                    lineHeight: 1.75,
                  }}
                >
                  {service.short_description
                    || "Chưa có mô tả ngắn."}
                </Paragraph>

                <Flex
                  wrap="wrap"
                  gap={10}
                >
                  <Tag
                    icon={<CalendarOutlined />}
                    color="cyan"
                  >
                    {service.delivery_days} ngày
                  </Tag>

                  <Tag
                    icon={<ReloadOutlined />}
                    color="blue"
                  >
                    {service.revision_count} lần chỉnh sửa
                  </Tag>

                  <Tag
                    icon={<EyeOutlined />}
                  >
                    {Number(
                      service.view_count || 0
                    ).toLocaleString("vi-VN")} lượt xem
                  </Tag>

                  <Tag
                    icon={<ShoppingCartOutlined />}
                  >
                    {Number(
                      service.order_count || 0
                    ).toLocaleString("vi-VN")} lượt đặt
                  </Tag>
                </Flex>
              </Space>

              <Divider />

              <Title level={4}>
                Mô tả dịch vụ
              </Title>

              <Paragraph
                style={{
                  whiteSpace: "pre-line",
                  lineHeight: 1.9,
                  fontSize: 15,
                }}
              >
                {service.description}
              </Paragraph>

              <Divider />

              <Title level={4}>
                <CodeOutlined />
                {" "}Kỹ năng chuyên môn
              </Title>

              <StringTagList
                items={service.skills}
                color="blue"
                emptyText="Dịch vụ chưa khai báo kỹ năng."
              />

              <Divider />

              <Row gutter={[24, 24]}>
                <Col
                  xs={24}
                  md={12}
                >
                  <Card
                    title={
                      <Space>
                        <ToolOutlined />
                        Tính năng
                      </Space>
                    }
                    size="small"
                    style={{
                      height: "100%",
                    }}
                  >
                    <StringList
                      items={service.features}
                      icon={
                        <CheckCircleOutlined
                          style={{
                            color: "#52c41a",
                            marginTop: 4,
                          }}
                        />
                      }
                      emptyText="Chưa có tính năng được khai báo."
                    />
                  </Card>
                </Col>

                <Col
                  xs={24}
                  md={12}
                >
                  <Card
                    title={
                      <Space>
                        <FileDoneOutlined />
                        Sản phẩm bàn giao
                      </Space>
                    }
                    size="small"
                    style={{
                      height: "100%",
                    }}
                  >
                    <StringList
                      items={service.deliverables}
                      icon={
                        <CheckCircleOutlined
                          style={{
                            color: "#1677ff",
                            marginTop: 4,
                          }}
                        />
                      }
                      emptyText="Chưa có sản phẩm bàn giao."
                    />
                  </Card>
                </Col>
              </Row>

              <Card
                title={
                  <Space>
                    <SafetyCertificateOutlined />
                    Yêu cầu từ khách hàng
                  </Space>
                }
                size="small"
                style={{
                  marginTop: 24,
                }}
              >
                <StringList
                  items={service.requirements}
                  icon={
                    <CheckCircleOutlined
                      style={{
                        color: "#722ed1",
                        marginTop: 4,
                      }}
                    />
                  }
                  emptyText={
                    "Dịch vụ không yêu cầu thông tin đặc biệt."
                  }
                />
              </Card>

              {(service.demo_url
                || service.portfolio_url) && (
                <>
                  <Divider />

                  <Title level={4}>
                    Liên kết tham khảo
                  </Title>

                  <Flex
                    wrap="wrap"
                    gap={12}
                  >
                    {service.demo_url && (
                      <Button
                        icon={<GlobalOutlined />}
                        onClick={() => (
                          openExternalLink(
                            service.demo_url,
                            "Demo"
                          )
                        )}
                      >
                        Xem Demo
                      </Button>
                    )}

                    {service.portfolio_url && (
                      <Button
                        icon={<LinkOutlined />}
                        onClick={() => (
                          openExternalLink(
                            service.portfolio_url,
                            "Portfolio"
                          )
                        )}
                      >
                        Xem Portfolio
                      </Button>
                    )}
                  </Flex>
                </>
              )}
            </div>
          </Card>
        </Col>


        {/* =================================================
            RIGHT SIDEBAR
        ================================================= */}

        <Col
          xs={24}
          xl={8}
        >
          <div
            style={{
              position: "sticky",
              top: 94,
            }}
          >
            <Card
              bordered
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
                <div>
                  <Text type="secondary">
                    Giá dịch vụ
                  </Text>

                  <Title
                    level={2}
                    style={{
                      color: "#52c41a",
                      margin: "4px 0 0",
                    }}
                  >
                    {formatCurrency(
                      service.price,
                      service.currency
                    )}
                  </Title>
                </div>

                <Descriptions
                  bordered
                  size="small"
                  column={1}
                >
                  <Descriptions.Item
                    label="Thời gian"
                  >
                    {service.delivery_days} ngày
                  </Descriptions.Item>

                  <Descriptions.Item
                    label="Chỉnh sửa"
                  >
                    {service.revision_count} lần
                  </Descriptions.Item>

                  <Descriptions.Item
                    label="Đơn vị tiền"
                  >
                    {service.currency}
                  </Descriptions.Item>
                </Descriptions>

                <Button
                  type="primary"
                  size="large"
                  block
                  icon={<ShoppingCartOutlined />}
                  loading={ordering}
                  disabled={
                    serviceStatus !== "PUBLISHED"
                  }
                  onClick={handleOrder}
                >
                  Đặt dịch vụ
                </Button>

                <Button
                  block
                  icon={<ArrowLeftOutlined />}
                  onClick={handleBack}
                >
                  Xem dịch vụ khác
                </Button>

                <Alert
                  type="info"
                  showIcon
                  message="Thanh toán được bảo vệ"
                  description={
                    "Tiền được giữ trong Escrow và chỉ "
                    + "giải ngân sau khi bạn duyệt kết quả."
                  }
                />
              </Space>
            </Card>

            <Card
              title="Thông tin chuyên gia"
            >
              <Flex
                align="center"
                gap={14}
                style={{
                  marginBottom: 18,
                }}
              >
                <Avatar
                  size={56}
                  icon={<UserOutlined />}
                  style={{
                    background:
                      "linear-gradient(135deg, #4f46e5, #7c3aed)",
                  }}
                />

                <div>
                  <Text
                    strong
                    style={{
                      display: "block",
                      fontSize: 16,
                    }}
                  >
                    {service.expert?.full_name
                      || service.expert_name
                      || "Chuyên gia AI"}
                  </Text>

                  <Text type="secondary">
                    {service.expert?.title
                      || service.expert_title
                      || "AI Expert"}
                  </Text>
                </div>
              </Flex>

              <Row gutter={[12, 12]}>
                <Col span={12}>
                  <Card
                    size="small"
                    styles={{
                      body: {
                        padding: 12,
                      },
                    }}
                  >
                    <Statistic
                      title="Lượt xem"
                      value={Number(
                        service.view_count || 0
                      )}
                      prefix={<EyeOutlined />}
                    />
                  </Card>
                </Col>

                <Col span={12}>
                  <Card
                    size="small"
                    styles={{
                      body: {
                        padding: 12,
                      },
                    }}
                  >
                    <Statistic
                      title="Đơn hàng"
                      value={Number(
                        service.order_count || 0
                      )}
                      prefix={<ShoppingCartOutlined />}
                    />
                  </Card>
                </Col>
              </Row>

              <Divider />

              <Button
                block
                icon={<UserOutlined />}
                onClick={() => {
                  if (service.expert_id) {
                    navigate(
                      `/experts?expert_id=${service.expert_id}`
                    );
                  }
                }}
              >
                Xem hồ sơ chuyên gia
              </Button>
            </Card>
          </div>
        </Col>
      </Row>
    </div>
  );
}


export default AIServiceDetail;