import React, {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  Alert,
  App,
  Breadcrumb,
  Button,
  Card,
  Col,
  Divider,
  Empty,
  Flex,
  Form,
  Image,
  Input,
  InputNumber,
  Row,
  Select,
  Space,
  Spin,
  Tag,
  Typography,
} from "antd";

import {
  ArrowLeftOutlined,
  CalendarOutlined,
  CheckCircleOutlined,
  CodeOutlined,
  DollarOutlined,
  FileDoneOutlined,
  GlobalOutlined,
  LinkOutlined,
  LoadingOutlined,
  RocketOutlined,
  SaveOutlined,
  ToolOutlined,
  UserOutlined,
} from "@ant-design/icons";

import { useNavigate } from "react-router-dom";

import aiServiceApi from "../api/aiServiceApi";
import categoryApi from "../api/categoryApi";
import expertApi from "../api/expertApi";


const {
  Title,
  Text,
  Paragraph,
} = Typography;

const {
  TextArea,
} = Input;


// ==========================================================
// CONSTANTS
// ==========================================================

const DEFAULT_VALUES = {
  expert_id: undefined,
  category_id: undefined,

  title: "",
  short_description: "",
  description: "",

  price: null,
  currency: "VND",
  delivery_days: 7,
  revision_count: 1,

  skills: [],
  features: [],
  deliverables: [],
  requirements: [],

  image_url: "",
  demo_url: "",
  portfolio_url: "",
};


const SKILL_OPTIONS = [
  "Python",
  "FastAPI",
  "PostgreSQL",
  "React",
  "JavaScript",
  "TypeScript",
  "Docker",
  "Git",
  "Gemini API",
  "OpenAI API",
  "LLM",
  "RAG",
  "NLP",
  "Machine Learning",
  "Deep Learning",
  "Computer Vision",
  "OpenCV",
  "PyTorch",
  "TensorFlow",
  "Scikit-learn",
  "Pandas",
  "NumPy",
  "Data Analysis",
  "Prompt Engineering",
  "API Integration",
].map((item) => ({
  label: item,
  value: item,
}));


const FEATURE_OPTIONS = [
  "Trả lời câu hỏi tự động",
  "Lưu lịch sử hội thoại",
  "Tìm kiếm ngữ nghĩa",
  "Phân tích dữ liệu",
  "Tạo báo cáo tự động",
  "Nhận dạng hình ảnh",
  "Nhận dạng văn bản OCR",
  "Phân loại nội dung",
  "Tóm tắt văn bản",
  "Phân tích cảm xúc",
  "Đề xuất nội dung",
  "Tích hợp API bên thứ ba",
  "Trang quản trị",
  "Phân quyền người dùng",
  "Thông báo thời gian thực",
  "Xuất dữ liệu Excel hoặc PDF",
].map((item) => ({
  label: item,
  value: item,
}));


const DELIVERABLE_OPTIONS = [
  "Mã nguồn hoàn chỉnh",
  "Backend API",
  "Giao diện frontend",
  "Cơ sở dữ liệu",
  "Mô hình AI",
  "Tài liệu API",
  "Tài liệu kỹ thuật",
  "Tài liệu hướng dẫn sử dụng",
  "Báo cáo kiểm thử",
  "Dockerfile",
  "Tệp triển khai",
  "Video hướng dẫn",
].map((item) => ({
  label: item,
  value: item,
}));


const REQUIREMENT_OPTIONS = [
  "Dữ liệu mẫu",
  "Tài liệu nghiệp vụ",
  "Tài khoản API",
  "Thông tin hệ thống cần tích hợp",
  "Quyền truy cập cơ sở dữ liệu",
  "Bộ câu hỏi thường gặp",
  "Mẫu kết quả mong muốn",
  "Thông tin máy chủ triển khai",
].map((item) => ({
  label: item,
  value: item,
}));


const CURRENCY_OPTIONS = [
  {
    label: "VND",
    value: "VND",
  },
  {
    label: "USD",
    value: "USD",
  },
];


// ==========================================================
// HELPERS
// ==========================================================

const normalizeApiResponse = (response) => {
  if (!response) {
    return null;
  }

  return response.data ?? response;
};


const extractCollection = (response) => {
  const data = normalizeApiResponse(response);

  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data?.items)) {
    return data.items;
  }

  if (Array.isArray(data?.data)) {
    return data.data;
  }

  return [];
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

  if (error?.code === "ECONNABORTED") {
    return (
      "Yêu cầu xử lý quá thời gian. "
      + "Vui lòng thử lại."
    );
  }

  if (!error?.response) {
    return (
      "Không thể kết nối tới backend. "
      + "Hãy kiểm tra FastAPI đang hoạt động."
    );
  }

  return (
    error?.message
    || "Không thể tạo dịch vụ AI."
  );
};


const cleanStringList = (values) => {
  if (!Array.isArray(values)) {
    return [];
  }

  const uniqueValues = new Set();

  values.forEach((value) => {
    const cleaned = String(
      value || ""
    ).trim();

    if (cleaned) {
      uniqueValues.add(cleaned);
    }
  });

  return Array.from(uniqueValues);
};


const cleanOptionalUrl = (value) => {
  const cleaned = String(
    value || ""
  ).trim();

  return cleaned || null;
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


const isValidHttpUrl = (value) => {
  if (!value) {
    return true;
  }

  try {
    const url = new URL(value);

    return (
      url.protocol === "http:"
      || url.protocol === "https:"
    );
  } catch {
    return false;
  }
};


// ==========================================================
// COMPONENT
// ==========================================================

function CreateAIService() {
  const navigate = useNavigate();

  const {
    message,
    modal,
  } = App.useApp();

  const [form] = Form.useForm();

  const [categories, setCategories] = useState([]);
  const [experts, setExperts] = useState([]);

  const [
    loadingOptions,
    setLoadingOptions,
  ] = useState(true);

  const [
    submitting,
    setSubmitting,
  ] = useState(false);

  const [error, setError] = useState("");

  const watchedValues = Form.useWatch(
    [],
    form
  ) || DEFAULT_VALUES;


  // ======================================================
  // LOAD FORM OPTIONS
  // ======================================================

  useEffect(() => {
    const loadOptions = async () => {
      setLoadingOptions(true);
      setError("");

      const results = await Promise.allSettled([
        categoryApi.getAll(),
        expertApi.getAll(),
      ]);

      const [
        categoryResult,
        expertResult,
      ] = results;

      if (categoryResult.status === "fulfilled") {
        setCategories(
          extractCollection(
            categoryResult.value
          )
        );
      } else {
        setCategories([]);
      }

      if (expertResult.status === "fulfilled") {
        setExperts(
          extractCollection(
            expertResult.value
          )
        );
      } else {
        setExperts([]);
      }

      if (
        categoryResult.status === "rejected"
        || expertResult.status === "rejected"
      ) {
        setError(
          "Không thể tải đầy đủ danh mục hoặc chuyên gia. "
          + "Hãy kiểm tra các API liên quan."
        );
      }

      setLoadingOptions(false);
    };

    loadOptions();
  }, []);


  // ======================================================
  // RESTORE DRAFT
  // ======================================================

  useEffect(() => {
    try {
      const rawDraft = localStorage.getItem(
        "aitasker_ai_service_draft"
      );

      if (!rawDraft) {
        return;
      }

      const draft = JSON.parse(rawDraft);

      form.setFieldsValue({
        ...DEFAULT_VALUES,
        ...draft,
        skills: Array.isArray(draft.skills)
          ? draft.skills
          : [],
        features: Array.isArray(draft.features)
          ? draft.features
          : [],
        deliverables: Array.isArray(
          draft.deliverables
        )
          ? draft.deliverables
          : [],
        requirements: Array.isArray(
          draft.requirements
        )
          ? draft.requirements
          : [],
      });
    } catch {
      localStorage.removeItem(
        "aitasker_ai_service_draft"
      );
    }
  }, [form]);


  // ======================================================
  // DERIVED VALUES
  // ======================================================

  const selectedExpert = useMemo(
    () => (
      experts.find(
        (expert) => (
          String(expert.id)
          === String(
            watchedValues.expert_id
          )
        )
      ) || null
    ),
    [
      experts,
      watchedValues.expert_id,
    ]
  );


  const selectedCategory = useMemo(
    () => (
      categories.find(
        (category) => (
          String(category.id)
          === String(
            watchedValues.category_id
          )
        )
      ) || null
    ),
    [
      categories,
      watchedValues.category_id,
    ]
  );


  // ======================================================
  // ACTIONS
  // ======================================================

  const handleBack = () => {
    navigate("/ai-services");
  };


  const handleSaveDraft = () => {
    const values = form.getFieldsValue(
      true
    );

    localStorage.setItem(
      "aitasker_ai_service_draft",
      JSON.stringify(values)
    );

    message.success(
      "Đã lưu bản nháp dịch vụ."
    );
  };


  const handleReset = () => {
    modal.confirm({
      title: "Làm mới biểu mẫu?",
      content: (
        "Toàn bộ nội dung đang nhập sẽ bị xóa."
      ),
      okText: "Làm mới",
      cancelText: "Hủy",
      onOk: () => {
        form.resetFields();

        form.setFieldsValue(
          DEFAULT_VALUES
        );

        localStorage.removeItem(
          "aitasker_ai_service_draft"
        );

        setError("");

        message.success(
          "Đã làm mới biểu mẫu."
        );
      },
    });
  };


  const handleSubmit = async () => {
    try {
      const values = (
        await form.validateFields()
      );

      modal.confirm({
        title: "Xác nhận tạo dịch vụ AI",
        icon: <RocketOutlined />,
        content: (
          <Space
            orientation="vertical"
            size={6}
          >
            <Text>
              Dịch vụ:{" "}
              <Text strong>
                {values.title}
              </Text>
            </Text>

            <Text>
              Chuyên gia:{" "}
              <Text strong>
                {selectedExpert?.full_name
                  || "Chưa xác định"}
              </Text>
            </Text>

            <Text>
              Giá:{" "}
              <Text strong>
                {formatCurrency(
                  values.price,
                  values.currency
                )}
              </Text>
            </Text>
          </Space>
        ),
        okText: "Tạo dịch vụ",
        cancelText: "Kiểm tra lại",
        onOk: async () => {
          setSubmitting(true);
          setError("");

          try {
            const payload = {
              expert_id: values.expert_id,
              category_id: values.category_id,

              title: values.title.trim(),

              short_description:
                values.short_description.trim(),

              description:
                values.description.trim(),

              price: Number(values.price),

              currency:
                values.currency || "VND",

              delivery_days: Number(
                values.delivery_days
              ),

              revision_count: Number(
                values.revision_count
              ),

              skills: cleanStringList(
                values.skills
              ),

              features: cleanStringList(
                values.features
              ),

              deliverables: cleanStringList(
                values.deliverables
              ),

              requirements: cleanStringList(
                values.requirements
              ),

              image_url: cleanOptionalUrl(
                values.image_url
              ),

              demo_url: cleanOptionalUrl(
                values.demo_url
              ),

              portfolio_url: cleanOptionalUrl(
                values.portfolio_url
              ),
            };

            const response = (
              await aiServiceApi.create(
                payload
              )
            );

            const createdService = (
              normalizeApiResponse(
                response
              )
            );

            if (!createdService?.id) {
              throw new Error(
                "Backend không trả về dịch vụ hợp lệ."
              );
            }

            localStorage.removeItem(
              "aitasker_ai_service_draft"
            );

            message.success(
              "Đã tạo dịch vụ AI thành công."
            );

            if (createdService.slug) {
              navigate(
                `/ai-services/${encodeURIComponent(
                  createdService.slug
                )}`
              );

              return;
            }

            navigate("/ai-services");
          } catch (requestError) {
            const errorMessage = (
              extractErrorMessage(
                requestError
              )
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
          "Vui lòng kiểm tra lại các trường bắt buộc."
        );
      }
    }
  };


  // ======================================================
  // LOADING
  // ======================================================

  if (loadingOptions) {
    return (
      <Card variant="outlined">
        <Flex
          vertical
          justify="center"
          align="center"
          gap={16}
          style={{
            minHeight: 420,
          }}
        >
          <Spin
            indicator={
              <LoadingOutlined
                spin
                style={{
                  fontSize: 52,
                }}
              />
            }
          />

          <Text type="secondary">
            Đang tải danh mục và chuyên gia...
          </Text>
        </Flex>
      </Card>
    );
  }


  // ======================================================
  // RENDER
  // ======================================================

  return (
    <div
      style={{
        paddingBottom: 32,
      }}
    >
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
                onClick={() => {
                  navigate("/dashboard");
                }}
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
            title: "Tạo dịch vụ",
          },
        ]}
      />


      {/* ==================================================
          HEADER
      ================================================== */}

      <Card
        variant="borderless"
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
                <RocketOutlined />
                {" "}
                Tạo dịch vụ AI
              </Title>

              <Paragraph
                style={{
                  margin: 0,
                  maxWidth: 800,
                  color: "#cbd5e1",
                  fontSize: 15,
                  lineHeight: 1.7,
                }}
              >
                Đăng dịch vụ của chuyên gia lên
                Marketplace để doanh nghiệp có thể tìm
                kiếm, xem chi tiết và tạo đơn đặt dịch vụ.
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
              Quay lại Marketplace
            </Button>
          </Col>
        </Row>
      </Card>


      {error && (
        <Alert
          type="error"
          showIcon
          closable
          title="Không thể xử lý dịch vụ"
          description={error}
          style={{
            marginBottom: 20,
          }}
          onClose={() => {
            setError("");
          }}
        />
      )}


      <Row gutter={[24, 24]}>
        {/* =================================================
            CREATE FORM
        ================================================= */}

        <Col
          xs={24}
          xl={16}
        >
          <Card
            variant="outlined"
            title={
              <Space>
                <FileDoneOutlined />
                <span>Thông tin dịch vụ</span>
              </Space>
            }
          >
            <Form
              form={form}
              layout="vertical"
              initialValues={DEFAULT_VALUES}
              disabled={submitting}
            >
              <Divider titlePlacement="left">
                Thông tin cơ bản
              </Divider>

              <Row gutter={16}>
                <Col
                  xs={24}
                  md={12}
                >
                  <Form.Item
                    name="expert_id"
                    label="Chuyên gia cung cấp"
                    rules={[
                      {
                        required: true,
                        message:
                          "Vui lòng chọn chuyên gia.",
                      },
                    ]}
                  >
                    <Select
                      showSearch
                      allowClear
                      optionFilterProp="label"
                      placeholder="Chọn chuyên gia"
                      suffixIcon={<UserOutlined />}
                      notFoundContent={
                        <Empty
                          image={
                            Empty.PRESENTED_IMAGE_SIMPLE
                          }
                          description={
                            "Chưa có chuyên gia."
                          }
                        />
                      }
                      options={experts.map(
                        (expert) => ({
                          value: expert.id,
                          label: (
                            expert.full_name
                            || expert.title
                            || expert.id
                          ),
                        })
                      )}
                    />
                  </Form.Item>
                </Col>

                <Col
                  xs={24}
                  md={12}
                >
                  <Form.Item
                    name="category_id"
                    label="Danh mục dịch vụ"
                    rules={[
                      {
                        required: true,
                        message:
                          "Vui lòng chọn danh mục.",
                      },
                    ]}
                  >
                    <Select
                      showSearch
                      allowClear
                      optionFilterProp="label"
                      placeholder="Chọn danh mục"
                      notFoundContent={
                        <Empty
                          image={
                            Empty.PRESENTED_IMAGE_SIMPLE
                          }
                          description={
                            "Chưa có danh mục."
                          }
                        />
                      }
                      options={categories.map(
                        (category) => ({
                          value: category.id,
                          label:
                            category.name
                            || category.id,
                        })
                      )}
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item
                name="title"
                label="Tên dịch vụ"
                rules={[
                  {
                    required: true,
                    whitespace: true,
                    message:
                      "Vui lòng nhập tên dịch vụ.",
                  },
                  {
                    min: 5,
                    message:
                      "Tên dịch vụ phải có ít nhất 5 ký tự.",
                  },
                  {
                    max: 255,
                    message:
                      "Tên dịch vụ tối đa 255 ký tự.",
                  },
                ]}
              >
                <Input
                  prefix={<RocketOutlined />}
                  placeholder={
                    "Ví dụ: Xây dựng Chatbot AI "
                    + "dùng Gemini và RAG"
                  }
                />
              </Form.Item>

              <Form.Item
                name="short_description"
                label="Mô tả ngắn"
                rules={[
                  {
                    required: true,
                    whitespace: true,
                    message:
                      "Vui lòng nhập mô tả ngắn.",
                  },
                  {
                    min: 10,
                    message:
                      "Mô tả ngắn phải có ít nhất 10 ký tự.",
                  },
                  {
                    max: 500,
                    message:
                      "Mô tả ngắn tối đa 500 ký tự.",
                  },
                ]}
              >
                <TextArea
                  rows={3}
                  showCount
                  maxLength={500}
                  placeholder={
                    "Tóm tắt giá trị chính của dịch vụ..."
                  }
                />
              </Form.Item>

              <Form.Item
                name="description"
                label="Mô tả chi tiết"
                rules={[
                  {
                    required: true,
                    whitespace: true,
                    message:
                      "Vui lòng nhập mô tả chi tiết.",
                  },
                  {
                    min: 20,
                    message:
                      "Mô tả chi tiết phải có ít nhất 20 ký tự.",
                  },
                  {
                    max: 10000,
                    message:
                      "Mô tả tối đa 10.000 ký tự.",
                  },
                ]}
              >
                <TextArea
                  rows={9}
                  showCount
                  maxLength={10000}
                  placeholder={
                    "Trình bày phạm vi công việc, "
                    + "quy trình triển khai, công nghệ sử dụng "
                    + "và kết quả doanh nghiệp nhận được..."
                  }
                />
              </Form.Item>


              <Divider titlePlacement="left">
                Giá và thời gian
              </Divider>

              <Row gutter={16}>
                <Col
                  xs={24}
                  md={8}
                >
                  <Form.Item
                    name="price"
                    label="Giá dịch vụ"
                    rules={[
                      {
                        required: true,
                        message:
                          "Vui lòng nhập giá dịch vụ.",
                      },
                      {
                        type: "number",
                        min: 0,
                        message:
                          "Giá không được âm.",
                      },
                    ]}
                  >
                    <InputNumber
                      min={0}
                      step={100000}
                      controls
                      style={{
                        width: "100%",
                      }}
                      placeholder="10.000.000"
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
                    />
                  </Form.Item>
                </Col>

                <Col
                  xs={24}
                  md={8}
                >
                  <Form.Item
                    name="currency"
                    label="Đơn vị tiền"
                    rules={[
                      {
                        required: true,
                      },
                    ]}
                  >
                    <Select
                      options={CURRENCY_OPTIONS}
                    />
                  </Form.Item>
                </Col>

                <Col
                  xs={24}
                  md={8}
                >
                  <Form.Item
                    name="delivery_days"
                    label="Thời gian bàn giao"
                    rules={[
                      {
                        required: true,
                        message:
                          "Vui lòng nhập thời gian.",
                      },
                      {
                        type: "number",
                        min: 1,
                        max: 365,
                        message:
                          "Thời gian từ 1 đến 365 ngày.",
                      },
                    ]}
                  >
                    <InputNumber
                      min={1}
                      max={365}
                      controls
                      style={{
                        width: "100%",
                      }}
                      prefix={
                        <CalendarOutlined />
                      }
                      placeholder="7"
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item
                name="revision_count"
                label="Số lần chỉnh sửa"
                rules={[
                  {
                    required: true,
                    message:
                      "Vui lòng nhập số lần chỉnh sửa.",
                  },
                  {
                    type: "number",
                    min: 0,
                    max: 100,
                    message:
                      "Số lần chỉnh sửa từ 0 đến 100.",
                  },
                ]}
              >
                <InputNumber
                  min={0}
                  max={100}
                  controls
                  style={{
                    width: "100%",
                  }}
                />
              </Form.Item>


              <Divider titlePlacement="left">
                Kỹ năng và phạm vi
              </Divider>

              <Form.Item
                name="skills"
                label="Kỹ năng"
                tooltip={
                  "Chọn gợi ý hoặc nhập kỹ năng mới "
                  + "rồi nhấn Enter."
                }
              >
                <Select
                  mode="tags"
                  showSearch
                  allowClear
                  optionFilterProp="label"
                  options={SKILL_OPTIONS}
                  tokenSeparators={[
                    ",",
                    ";",
                  ]}
                  suffixIcon={<CodeOutlined />}
                  placeholder={
                    "Chọn hoặc nhập Python, FastAPI, RAG..."
                  }
                  notFoundContent={
                    <Text type="secondary">
                      Nhập kỹ năng mới rồi nhấn Enter
                    </Text>
                  }
                />
              </Form.Item>

              <Form.Item
                name="features"
                label="Tính năng"
                tooltip={
                  "Chọn gợi ý hoặc nhập tính năng mới "
                  + "rồi nhấn Enter."
                }
              >
                <Select
                  mode="tags"
                  showSearch
                  allowClear
                  optionFilterProp="label"
                  options={FEATURE_OPTIONS}
                  tokenSeparators={[
                    ",",
                    ";",
                  ]}
                  suffixIcon={<ToolOutlined />}
                  placeholder={
                    "Chọn hoặc nhập các tính năng..."
                  }
                  notFoundContent={
                    <Text type="secondary">
                      Nhập tính năng mới rồi nhấn Enter
                    </Text>
                  }
                />
              </Form.Item>

              <Form.Item
                name="deliverables"
                label="Sản phẩm bàn giao"
                tooltip={
                  "Nhập từng sản phẩm rồi nhấn Enter."
                }
              >
                <Select
                  mode="tags"
                  showSearch
                  allowClear
                  optionFilterProp="label"
                  options={DELIVERABLE_OPTIONS}
                  tokenSeparators={[
                    ",",
                    ";",
                  ]}
                  suffixIcon={<FileDoneOutlined />}
                  placeholder={
                    "Mã nguồn, API, tài liệu..."
                  }
                  notFoundContent={
                    <Text type="secondary">
                      Nhập sản phẩm mới rồi nhấn Enter
                    </Text>
                  }
                />
              </Form.Item>

              <Form.Item
                name="requirements"
                label="Yêu cầu từ khách hàng"
                tooltip={
                  "Những thông tin doanh nghiệp cần "
                  + "cung cấp trước khi bắt đầu."
                }
              >
                <Select
                  mode="tags"
                  showSearch
                  allowClear
                  optionFilterProp="label"
                  options={REQUIREMENT_OPTIONS}
                  tokenSeparators={[
                    ",",
                    ";",
                  ]}
                  placeholder={
                    "Dữ liệu mẫu, tài liệu nghiệp vụ..."
                  }
                  notFoundContent={
                    <Text type="secondary">
                      Nhập yêu cầu mới rồi nhấn Enter
                    </Text>
                  }
                />
              </Form.Item>


              <Divider titlePlacement="left">
                Hình ảnh và liên kết
              </Divider>

              <Form.Item
                name="image_url"
                label="URL ảnh dịch vụ"
                rules={[
                  {
                    validator: async (
                      _,
                      value
                    ) => {
                      if (
                        value
                        && !isValidHttpUrl(value)
                      ) {
                        throw new Error(
                          "URL ảnh không hợp lệ."
                        );
                      }
                    },
                  },
                ]}
              >
                <Input
                  prefix={<GlobalOutlined />}
                  placeholder="https://example.com/image.jpg"
                />
              </Form.Item>

              <Form.Item
                name="demo_url"
                label="URL Demo"
                rules={[
                  {
                    validator: async (
                      _,
                      value
                    ) => {
                      if (
                        value
                        && !isValidHttpUrl(value)
                      ) {
                        throw new Error(
                          "URL Demo không hợp lệ."
                        );
                      }
                    },
                  },
                ]}
              >
                <Input
                  prefix={<LinkOutlined />}
                  placeholder="https://demo.example.com"
                />
              </Form.Item>

              <Form.Item
                name="portfolio_url"
                label="URL Portfolio"
                rules={[
                  {
                    validator: async (
                      _,
                      value
                    ) => {
                      if (
                        value
                        && !isValidHttpUrl(value)
                      ) {
                        throw new Error(
                          "URL Portfolio không hợp lệ."
                        );
                      }
                    },
                  },
                ]}
              >
                <Input
                  prefix={<LinkOutlined />}
                  placeholder="https://portfolio.example.com"
                />
              </Form.Item>


              <Divider />

              <Flex
                gap={12}
                wrap="wrap"
              >
                <Button
                  type="primary"
                  size="large"
                  icon={<RocketOutlined />}
                  loading={submitting}
                  onClick={handleSubmit}
                >
                  Tạo dịch vụ AI
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
                  disabled={submitting}
                  onClick={handleReset}
                >
                  Làm mới
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
            LIVE PREVIEW
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
              variant="outlined"
              title={
                <Space>
                  <RocketOutlined />
                  <span>Xem trước dịch vụ</span>
                </Space>
              }
            >
              <Space
                orientation="vertical"
                size={18}
                style={{
                  width: "100%",
                }}
              >
                {watchedValues.image_url
                  && isValidHttpUrl(
                    watchedValues.image_url
                  ) ? (
                  <Image
                    width="100%"
                    height={190}
                    src={
                      watchedValues.image_url
                    }
                    alt={
                      watchedValues.title
                      || "AI Service"
                    }
                    style={{
                      objectFit: "cover",
                      borderRadius: 10,
                    }}
                    fallback={
                      "data:image/svg+xml;charset=UTF-8,"
                      + encodeURIComponent(
                        `
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            width="800"
                            height="400"
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
                              font-size="28"
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
                    gap={12}
                    style={{
                      height: 190,
                      borderRadius: 10,
                      background:
                        "linear-gradient("
                        + "135deg, "
                        + "#1e1b4b, "
                        + "#312e81"
                        + ")",
                    }}
                  >
                    <RocketOutlined
                      style={{
                        color: "#a5b4fc",
                        fontSize: 54,
                      }}
                    />

                    <Text
                      style={{
                        color: "#c7d2fe",
                      }}
                    >
                      AITasker AI Marketplace
                    </Text>
                  </Flex>
                )}

                <div>
                  {selectedCategory?.name && (
                    <Tag
                      color="geekblue"
                      style={{
                        marginBottom: 10,
                      }}
                    >
                      {selectedCategory.name}
                    </Tag>
                  )}

                  <Title
                    level={4}
                    style={{
                      margin: 0,
                    }}
                  >
                    {watchedValues.title
                      || "Tên dịch vụ AI"}
                  </Title>

                  <Paragraph
                    type="secondary"
                    ellipsis={{
                      rows: 3,
                    }}
                    style={{
                      marginTop: 10,
                    }}
                  >
                    {watchedValues.short_description
                      || "Mô tả ngắn của dịch vụ sẽ hiển thị tại đây."}
                  </Paragraph>
                </div>

                <Flex
                  wrap="wrap"
                  gap={8}
                >
                  <Tag
                    icon={<CalendarOutlined />}
                    color="cyan"
                  >
                    {Number(
                      watchedValues.delivery_days
                      || 0
                    )} ngày
                  </Tag>

                  <Tag>
                    {Number(
                      watchedValues.revision_count
                      || 0
                    )} lần chỉnh sửa
                  </Tag>
                </Flex>

                <Title
                  level={3}
                  style={{
                    margin: 0,
                    color: "#52c41a",
                  }}
                >
                  <DollarOutlined />
                  {" "}
                  {formatCurrency(
                    watchedValues.price,
                    watchedValues.currency
                  )}
                </Title>

                <Divider
                  style={{
                    margin: 0,
                  }}
                />

                <div>
                  <Text
                    strong
                    style={{
                      display: "block",
                      marginBottom: 8,
                    }}
                  >
                    Chuyên gia
                  </Text>

                  <Text type="secondary">
                    {selectedExpert?.full_name
                      || "Chưa chọn chuyên gia"}
                  </Text>
                </div>

                <div>
                  <Text
                    strong
                    style={{
                      display: "block",
                      marginBottom: 8,
                    }}
                  >
                    Kỹ năng
                  </Text>

                  <Flex
                    gap={6}
                    wrap="wrap"
                  >
                    {cleanStringList(
                      watchedValues.skills
                    ).length > 0 ? (
                      cleanStringList(
                        watchedValues.skills
                      )
                        .slice(0, 8)
                        .map((skill) => (
                          <Tag
                            key={skill}
                            color="blue"
                            style={{
                              marginInlineEnd: 0,
                            }}
                          >
                            {skill}
                          </Tag>
                        ))
                    ) : (
                      <Text type="secondary">
                        Chưa chọn kỹ năng.
                      </Text>
                    )}
                  </Flex>
                </div>

                <Alert
                  type="info"
                  showIcon
                  title="Marketplace"
                  description={
                    "Sau khi tạo, dịch vụ cần ở trạng thái "
                    + "PUBLISHED để xuất hiện trong danh sách."
                  }
                />

                <Button
                  type="primary"
                  block
                  size="large"
                  icon={
                    submitting
                      ? <LoadingOutlined />
                      : <CheckCircleOutlined />
                  }
                  loading={submitting}
                  onClick={handleSubmit}
                >
                  Xác nhận tạo dịch vụ
                </Button>
              </Space>
            </Card>
          </div>
        </Col>
      </Row>
    </div>
  );
}


export default CreateAIService;