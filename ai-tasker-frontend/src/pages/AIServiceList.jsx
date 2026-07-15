import React, {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  App,
  Avatar,
  Badge,
  Button,
  Card,
  Col,
  Empty,
  Flex,
  Form,
  Input,
  InputNumber,
  Pagination,
  Row,
  Select,
  Skeleton,
  Space,
  Statistic,
  Tag,
  Tooltip,
  Typography,
} from "antd";

import {
  AppstoreOutlined,
  CalendarOutlined,
  ClearOutlined,
  DollarOutlined,
  EyeOutlined,
  FilterOutlined,
  FireOutlined,
  ReloadOutlined,
  RocketOutlined,
  SearchOutlined,
  ShoppingCartOutlined,
  StarOutlined,
  UserOutlined,
} from "@ant-design/icons";

import { useNavigate } from "react-router-dom";

import aiServiceApi from "../api/aiServiceApi";
import categoryApi from "../api/categoryApi";


const {
  Title,
  Text,
  Paragraph,
} = Typography;


const DEFAULT_FILTERS = {
  keyword: "",
  category_id: undefined,
  min_price: undefined,
  max_price: undefined,
  max_delivery_days: undefined,
  skill: "",
  is_featured: undefined,
};


const DEFAULT_PAGE_SIZE = 12;


/**
 * Hỗ trợ hai kiểu axiosClient:
 *
 * 1. Trả nguyên AxiosResponse.
 * 2. Interceptor trả trực tiếp response.data.
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
    return "Không tìm thấy dữ liệu dịch vụ AI.";
  }

  return (
    error?.message
    || "Không thể tải danh sách dịch vụ AI."
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


function AIServiceList() {
  const navigate = useNavigate();

  const {
    message,
  } = App.useApp();

  const [form] = Form.useForm();

  const [services, setServices] = useState([]);
  const [categories, setCategories] = useState([]);

  const [loading, setLoading] = useState(true);

  const [
    loadingCategories,
    setLoadingCategories,
  ] = useState(true);

  const [page, setPage] = useState(1);

  const [pageSize, setPageSize] = useState(
    DEFAULT_PAGE_SIZE
  );

  const [total, setTotal] = useState(0);

  const [
    activeFilters,
    setActiveFilters,
  ] = useState(DEFAULT_FILTERS);


  // ======================================================
  // LOAD CATEGORIES
  // ======================================================

  const loadCategories = useCallback(async () => {
    setLoadingCategories(true);

    try {
      const response = await categoryApi.getAll();

      const data = normalizeApiResponse(
        response
      );

      if (Array.isArray(data)) {
        setCategories(data);
        return;
      }

      if (Array.isArray(data?.items)) {
        setCategories(data.items);
        return;
      }

      setCategories([]);
    } catch (error) {
      setCategories([]);

      console.error(
        "Không thể tải danh mục:",
        error
      );
    } finally {
      setLoadingCategories(false);
    }
  }, []);


  // ======================================================
  // BUILD MARKETPLACE PARAMETERS
  // ======================================================

  const buildMarketplaceParams = useCallback(() => {
    const params = {
      page,
      page_size: pageSize,
    };

    if (activeFilters.keyword?.trim()) {
      params.keyword =
        activeFilters.keyword.trim();
    }

    if (activeFilters.category_id) {
      params.category_id =
        activeFilters.category_id;
    }

    if (
      activeFilters.min_price !== undefined
      && activeFilters.min_price !== null
    ) {
      params.min_price =
        activeFilters.min_price;
    }

    if (
      activeFilters.max_price !== undefined
      && activeFilters.max_price !== null
    ) {
      params.max_price =
        activeFilters.max_price;
    }

    if (
      activeFilters.max_delivery_days !== undefined
      && activeFilters.max_delivery_days !== null
    ) {
      params.max_delivery_days =
        activeFilters.max_delivery_days;
    }

    if (activeFilters.skill?.trim()) {
      params.skill =
        activeFilters.skill.trim();
    }

    if (
      activeFilters.is_featured !== undefined
      && activeFilters.is_featured !== null
    ) {
      params.is_featured =
        activeFilters.is_featured;
    }

    return params;
  }, [
    activeFilters,
    page,
    pageSize,
  ]);


  // ======================================================
  // LOAD SERVICES
  // ======================================================

  const loadServices = useCallback(async () => {
    setLoading(true);

    try {
      const params = buildMarketplaceParams();

      const response = (
        await aiServiceApi.searchMarketplace(
          params
        )
      );

      const data = normalizeApiResponse(
        response
      );

      const items = Array.isArray(data?.items)
        ? data.items
        : [];

      setServices(items);

      setTotal(
        Number(data?.total || 0)
      );
    } catch (error) {
      setServices([]);
      setTotal(0);

      message.error(
        extractErrorMessage(error)
      );
    } finally {
      setLoading(false);
    }
  }, [
    buildMarketplaceParams,
    message,
  ]);


  useEffect(() => {
    loadCategories();
  }, [loadCategories]);


  useEffect(() => {
    loadServices();
  }, [loadServices]);


  // ======================================================
  // SUMMARY VALUES
  // ======================================================

  const featuredCount = useMemo(
    () => (
      services.filter(
        (service) => (
          isFeaturedService(
            service?.is_featured
          )
        )
      ).length
    ),
    [services]
  );


  const averagePrice = useMemo(() => {
    if (services.length === 0) {
      return 0;
    }

    const totalPrice = services.reduce(
      (sum, service) => (
        sum + Number(service?.price || 0)
      ),
      0
    );

    return totalPrice / services.length;
  }, [services]);


  const totalOrders = useMemo(
    () => (
      services.reduce(
        (sum, service) => (
          sum
          + Number(
            service?.order_count || 0
          )
        ),
        0
      )
    ),
    [services]
  );


  // ======================================================
  // FILTER HANDLERS
  // ======================================================

  const handleSearch = async () => {
    try {
      const values = (
        await form.validateFields()
      );

      const hasMinPrice = (
        values.min_price !== undefined
        && values.min_price !== null
      );

      const hasMaxPrice = (
        values.max_price !== undefined
        && values.max_price !== null
      );

      if (
        hasMinPrice
        && hasMaxPrice
        && Number(values.min_price)
          > Number(values.max_price)
      ) {
        message.warning(
          "Giá tối thiểu không được lớn hơn giá tối đa."
        );

        return;
      }

      setPage(1);

      setActiveFilters({
        keyword: values.keyword || "",
        category_id: values.category_id,
        min_price: values.min_price,
        max_price: values.max_price,
        max_delivery_days:
          values.max_delivery_days,
        skill: values.skill || "",
        is_featured:
          values.is_featured,
      });
    } catch {
      message.warning(
        "Vui lòng kiểm tra lại bộ lọc."
      );
    }
  };


  const handleReset = () => {
    form.resetFields();

    form.setFieldsValue(
      DEFAULT_FILTERS
    );

    setPage(1);
    setPageSize(DEFAULT_PAGE_SIZE);

    setActiveFilters({
      ...DEFAULT_FILTERS,
    });

    message.success(
      "Đã xóa bộ lọc."
    );
  };


  const handlePageChange = (
    nextPage,
    nextPageSize
  ) => {
    if (nextPageSize !== pageSize) {
      setPage(1);
      setPageSize(nextPageSize);
      return;
    }

    setPage(nextPage);
  };


  // ======================================================
  // NAVIGATION
  // ======================================================

  const handleViewDetail = (service) => {
    const slug = String(
      service?.slug || ""
    ).trim();

    if (!slug) {
      message.warning(
        "Dịch vụ chưa có slug hợp lệ."
      );

      return;
    }

    navigate(
      `/ai-services/${encodeURIComponent(slug)}`
    );
  };


  const handleCreateService = () => {
    navigate("/ai-services/create");
  };


  // ======================================================
  // CARD RENDER
  // ======================================================

  const renderServiceCard = (service) => {
    const featured = isFeaturedService(
      service?.is_featured
    );

    const skills = Array.isArray(
      service?.skills
    )
      ? service.skills
      : [];

    return (
      <Badge.Ribbon
        key={service.id}
        text="Nổi bật"
        color="purple"
        style={{
          display: featured
            ? "block"
            : "none",
        }}
      >
        <Card
          hoverable
          variant="outlined"
          cover={
            service.image_url ? (
              <div
                style={{
                  height: 190,
                  overflow: "hidden",
                  background: "#0f172a",
                }}
              >
                <img
                  src={service.image_url}
                  alt={
                    service.title
                    || "AI Service"
                  }
                  style={{
                    width: "100%",
                    height: "100%",
                    objectFit: "cover",
                  }}
                  onError={(event) => {
                    event.currentTarget.style.display =
                      "none";
                  }}
                />
              </div>
            ) : (
              <div
                style={{
                  height: 190,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  background:
                    "linear-gradient("
                    + "135deg, "
                    + "#1e1b4b 0%, "
                    + "#312e81 60%, "
                    + "#0f172a 100%"
                    + ")",
                }}
              >
                <RocketOutlined
                  style={{
                    fontSize: 56,
                    color: "#a5b4fc",
                  }}
                />
              </div>
            )
          }
          styles={{
            body: {
              padding: 18,
            },
          }}
          onClick={() => {
            handleViewDetail(service);
          }}
        >
          <Space
            orientation="vertical"
            size={12}
            style={{
              width: "100%",
            }}
          >
            <Flex
              justify="space-between"
              align="flex-start"
              gap={12}
            >
              <div
                style={{
                  minWidth: 0,
                  flex: 1,
                }}
              >
                <Title
                  level={4}
                  ellipsis={{
                    rows: 2,
                  }}
                  style={{
                    margin: 0,
                    minHeight: 56,
                  }}
                >
                  {service.title
                    || "Dịch vụ AI"}
                </Title>
              </div>

              {featured && (
                <Tooltip title="Dịch vụ nổi bật">
                  <FireOutlined
                    style={{
                      color: "#fa541c",
                      fontSize: 20,
                    }}
                  />
                </Tooltip>
              )}
            </Flex>

            <Paragraph
              type="secondary"
              ellipsis={{
                rows: 3,
              }}
              style={{
                minHeight: 66,
                marginBottom: 0,
              }}
            >
              {service.short_description
                || "Chưa có mô tả ngắn."}
            </Paragraph>

            <Flex
              wrap="wrap"
              gap={6}
              style={{
                minHeight: 34,
              }}
            >
              {skills
                .slice(0, 4)
                .map((skill, index) => (
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
                ))}

              {skills.length > 4 && (
                <Tag
                  style={{
                    marginInlineEnd: 0,
                    borderRadius: 999,
                  }}
                >
                  +{skills.length - 4}
                </Tag>
              )}

              {skills.length === 0 && (
                <Text
                  type="secondary"
                  style={{
                    fontSize: 12,
                  }}
                >
                  Chưa khai báo kỹ năng
                </Text>
              )}
            </Flex>

            <Flex
              justify="space-between"
              align="center"
              gap={12}
            >
              <Space>
                <Avatar
                  size="small"
                  icon={<UserOutlined />}
                  style={{
                    background: "#4f46e5",
                  }}
                />

                <div>
                  <Text
                    strong
                    style={{
                      display: "block",
                      fontSize: 13,
                    }}
                  >
                    {service.expert_name
                      || service.expert?.full_name
                      || "Chuyên gia"}
                  </Text>

                  <Text
                    type="secondary"
                    style={{
                      fontSize: 11,
                    }}
                  >
                    {service.expert_title
                      || service.expert?.title
                      || "AI Expert"}
                  </Text>
                </div>
              </Space>

              {(
                service.category_name
                || service.category?.name
              ) && (
                <Tag color="geekblue">
                  {service.category_name
                    || service.category?.name}
                </Tag>
              )}
            </Flex>

            <Flex
              justify="space-between"
              align="center"
              wrap="wrap"
              gap={10}
            >
              <Space wrap>
                <Tag
                  icon={<CalendarOutlined />}
                  color="cyan"
                >
                  {Number(
                    service.delivery_days || 0
                  )} ngày
                </Tag>

                <Tag icon={<EyeOutlined />}>
                  {Number(
                    service.view_count || 0
                  ).toLocaleString("vi-VN")}
                </Tag>

                <Tag
                  icon={<ShoppingCartOutlined />}
                >
                  {Number(
                    service.order_count || 0
                  ).toLocaleString("vi-VN")}
                </Tag>
              </Space>

              <Text
                strong
                style={{
                  color: "#52c41a",
                  fontSize: 17,
                }}
              >
                {formatCurrency(
                  service.price,
                  service.currency
                )}
              </Text>
            </Flex>

            <Button
              type="primary"
              block
              icon={<EyeOutlined />}
              onClick={(event) => {
                event.stopPropagation();

                handleViewDetail(service);
              }}
            >
              Xem chi tiết
            </Button>
          </Space>
        </Card>
      </Badge.Ribbon>
    );
  };


  // ======================================================
  // RENDER
  // ======================================================

  return (
    <div>
      {/* ==================================================
          MARKETPLACE HEADER
      ================================================== */}

      <Card
        variant="borderless"
        style={{
          marginBottom: 24,
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
            lg={16}
          >
            <Space
              orientation="vertical"
              size={8}
            >
              <Tag color="purple">
                AI Marketplace
              </Tag>

              <Title
                level={2}
                style={{
                  margin: 0,
                  color: "#ffffff",
                }}
              >
                <AppstoreOutlined />
                {" "}
                Dịch vụ AI
              </Title>

              <Paragraph
                style={{
                  margin: 0,
                  color: "#cbd5e1",
                  maxWidth: 760,
                  fontSize: 15,
                  lineHeight: 1.7,
                }}
              >
                Khám phá các dịch vụ AI do chuyên gia
                đăng tải, lọc theo danh mục, ngân sách,
                kỹ năng và thời gian bàn giao.
              </Paragraph>
            </Space>
          </Col>

          <Col
            xs={24}
            lg="auto"
          >
            <Button
              type="primary"
              size="large"
              icon={<RocketOutlined />}
              onClick={handleCreateService}
            >
              Tạo dịch vụ AI
            </Button>
          </Col>
        </Row>
      </Card>


      {/* ==================================================
          SUMMARY
      ================================================== */}

      <Row
        gutter={[16, 16]}
        style={{
          marginBottom: 24,
        }}
      >
        <Col
          xs={24}
          sm={12}
          lg={6}
        >
          <Card variant="outlined">
            <Statistic
              title="Tổng kết quả"
              value={total}
              prefix={<AppstoreOutlined />}
            />
          </Card>
        </Col>

        <Col
          xs={24}
          sm={12}
          lg={6}
        >
          <Card variant="outlined">
            <Statistic
              title="Dịch vụ nổi bật"
              value={featuredCount}
              prefix={<StarOutlined />}
            />
          </Card>
        </Col>

        <Col
          xs={24}
          sm={12}
          lg={6}
        >
          <Card variant="outlined">
            <Statistic
              title="Giá trung bình"
              value={averagePrice}
              precision={0}
              prefix={<DollarOutlined />}
              suffix="VND"
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
          lg={6}
        >
          <Card variant="outlined">
            <Statistic
              title="Tổng lượt đặt"
              value={totalOrders}
              prefix={<ShoppingCartOutlined />}
            />
          </Card>
        </Col>
      </Row>


      {/* ==================================================
          FILTERS
      ================================================== */}

      <Card
        variant="outlined"
        title={
          <Space>
            <FilterOutlined />
            <span>Bộ lọc Marketplace</span>
          </Space>
        }
        style={{
          marginBottom: 24,
        }}
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={DEFAULT_FILTERS}
        >
          <Row gutter={[16, 8]}>
            <Col
              xs={24}
              md={12}
              xl={8}
            >
              <Form.Item
                name="keyword"
                label="Từ khóa"
              >
                <Input
                  allowClear
                  prefix={<SearchOutlined />}
                  placeholder="Chatbot, Computer Vision..."
                  onPressEnter={handleSearch}
                />
              </Form.Item>
            </Col>

            <Col
              xs={24}
              md={12}
              xl={8}
            >
              <Form.Item
                name="category_id"
                label="Danh mục"
              >
                <Select
                  allowClear
                  showSearch
                  loading={loadingCategories}
                  placeholder="Chọn danh mục"
                  optionFilterProp="label"
                  options={categories.map(
                    (category) => ({
                      value: category.id,
                      label: category.name,
                    })
                  )}
                />
              </Form.Item>
            </Col>

            <Col
              xs={24}
              md={12}
              xl={8}
            >
              <Form.Item
                name="skill"
                label="Kỹ năng"
              >
                <Input
                  allowClear
                  placeholder="Python, FastAPI, RAG..."
                />
              </Form.Item>
            </Col>

            <Col
              xs={24}
              sm={12}
              xl={6}
            >
              <Form.Item
                name="min_price"
                label="Giá tối thiểu"
              >
                <InputNumber
                  min={0}
                  step={100000}
                  style={{
                    width: "100%",
                  }}
                  formatter={(value) => (
                    value
                      ? `${value}`.replace(
                          /\B(?=(\d{3})+(?!\d))/g,
                          "."
                        )
                      : ""
                  )}
                  parser={(value) => (
                    value?.replace(/\./g, "")
                  )}
                  placeholder="0 VND"
                />
              </Form.Item>
            </Col>

            <Col
              xs={24}
              sm={12}
              xl={6}
            >
              <Form.Item
                name="max_price"
                label="Giá tối đa"
              >
                <InputNumber
                  min={0}
                  step={100000}
                  style={{
                    width: "100%",
                  }}
                  formatter={(value) => (
                    value
                      ? `${value}`.replace(
                          /\B(?=(\d{3})+(?!\d))/g,
                          "."
                        )
                      : ""
                  )}
                  parser={(value) => (
                    value?.replace(/\./g, "")
                  )}
                  placeholder="Không giới hạn"
                />
              </Form.Item>
            </Col>

            <Col
              xs={24}
              sm={12}
              xl={6}
            >
              <Form.Item
                name="max_delivery_days"
                label="Thời gian tối đa"
              >
                <InputNumber
                  min={1}
                  max={365}
                  style={{
                    width: "100%",
                  }}
                  placeholder="Số ngày"
                />
              </Form.Item>
            </Col>

            <Col
              xs={24}
              sm={12}
              xl={6}
            >
              <Form.Item
                name="is_featured"
                label="Loại dịch vụ"
              >
                <Select
                  allowClear
                  placeholder="Tất cả"
                  options={[
                    {
                      value: true,
                      label: "Dịch vụ nổi bật",
                    },
                    {
                      value: false,
                      label: "Dịch vụ thường",
                    },
                  ]}
                />
              </Form.Item>
            </Col>
          </Row>

          <Flex
            gap={10}
            wrap="wrap"
          >
            <Button
              type="primary"
              icon={<SearchOutlined />}
              onClick={handleSearch}
            >
              Tìm kiếm
            </Button>

            <Button
              icon={<ClearOutlined />}
              onClick={handleReset}
            >
              Xóa bộ lọc
            </Button>

            <Button
              icon={<ReloadOutlined />}
              loading={loading}
              onClick={loadServices}
            >
              Tải lại
            </Button>
          </Flex>
        </Form>
      </Card>


      {/* ==================================================
          SERVICE RESULTS
      ================================================== */}

      {loading ? (
        <Row gutter={[20, 20]}>
          {Array.from({
            length: pageSize,
          }).map((_, index) => (
            <Col
              key={index}
              xs={24}
              sm={12}
              xl={8}
              xxl={6}
            >
              <Card variant="outlined">
                <Skeleton
                  active
                  avatar={false}
                  paragraph={{
                    rows: 6,
                  }}
                />
              </Card>
            </Col>
          ))}
        </Row>
      ) : services.length === 0 ? (
        <Card variant="outlined">
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description={
              <Space
                orientation="vertical"
                size={4}
              >
                <Text>
                  Không tìm thấy dịch vụ phù hợp.
                </Text>

                <Text type="secondary">
                  Hãy thay đổi bộ lọc hoặc tạo dịch vụ mới.
                </Text>
              </Space>
            }
          >
            <Button
              type="primary"
              icon={<RocketOutlined />}
              onClick={handleCreateService}
            >
              Tạo dịch vụ AI
            </Button>
          </Empty>
        </Card>
      ) : (
        <>
          <Row gutter={[20, 20]}>
            {services.map((service) => (
              <Col
                key={service.id}
                xs={24}
                sm={12}
                xl={8}
                xxl={6}
              >
                {renderServiceCard(service)}
              </Col>
            ))}
          </Row>

          <Card
            variant="outlined"
            style={{
              marginTop: 24,
            }}
          >
            <Flex
              justify="space-between"
              align="center"
              wrap="wrap"
              gap={16}
            >
              <Text type="secondary">
                Hiển thị{" "}
                {services.length} trong tổng số{" "}
                {total} dịch vụ.
              </Text>

              <Pagination
                current={page}
                pageSize={pageSize}
                total={total}
                showSizeChanger
                pageSizeOptions={[
                  "8",
                  "12",
                  "24",
                  "48",
                ]}
                showQuickJumper
                onChange={handlePageChange}
                showTotal={(value) => (
                  `${value} dịch vụ`
                )}
              />
            </Flex>
          </Card>
        </>
      )}
    </div>
  );
}


export default AIServiceList;