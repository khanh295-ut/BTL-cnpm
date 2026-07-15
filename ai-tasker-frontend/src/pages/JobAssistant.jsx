import React, {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  Alert,
  App,
  Badge,
  Button,
  Card,
  Checkbox,
  Col,
  Collapse,
  Descriptions,
  Divider,
  Empty,
  Flex,
  Form,
  Input,
  InputNumber,
  List,
  Progress,
  Result,
  Row,
  Select,
  Space,
  Spin,
  Statistic,
  Steps,
  Tag,
  Timeline,
  Tooltip,
  Typography,
} from "antd";

import {
  BulbOutlined,
  CheckCircleOutlined,
  ClearOutlined,
  ClockCircleOutlined,
  CodeOutlined,
  CopyOutlined,
  DollarOutlined,
  FileTextOutlined,
  InfoCircleOutlined,
  LoadingOutlined,
  QuestionCircleOutlined,
  ReloadOutlined,
  RocketOutlined,
  SaveOutlined,
  SafetyCertificateOutlined,
  ThunderboltOutlined,
  ToolOutlined,
  WarningOutlined,
} from "@ant-design/icons";

import jobAssistantApi from "../api/jobAssistantApi";


const {
  Title,
  Text,
  Paragraph,
} = Typography;

const {
  TextArea,
} = Input;


const DEFAULT_VALUES = {
  idea: "",
  category_hint: "",
  budget_hint: null,
  timeline_hint: null,
  preferred_skills: [],
  language: "vi",
  detail_level: "STANDARD",
  include_milestones: true,
  include_risks: true,
  include_acceptance_criteria: true,
};


const DETAIL_LEVEL_LABELS = {
  BASIC: "Cơ bản",
  STANDARD: "Tiêu chuẩn",
  DETAILED: "Chi tiết",
};


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
        (item) => item?.msg || "Dữ liệu không hợp lệ."
      )
      .join(", ");
  }

  return (
    error?.message
    || "AI Job Assistant không thể tạo gợi ý dự án."
  );
};


const formatCurrency = (
  value,
  currency = "VND"
) => {
  const number = Number(value || 0);

  if (!Number.isFinite(number)) {
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
    ).format(number);
  } catch {
    return `${number.toLocaleString("vi-VN")} ${currency}`;
  }
};


const buildProjectDescription = (suggestion) => {
  if (!suggestion) {
    return "";
  }

  const sections = [
    suggestion.description,
  ];

  if (suggestion.objectives?.length) {
    sections.push(
      `MỤC TIÊU\n- ${suggestion.objectives.join("\n- ")}`
    );
  }

  if (suggestion.scope_included?.length) {
    sections.push(
      `PHẠM VI THỰC HIỆN\n- ${suggestion.scope_included.join("\n- ")}`
    );
  }

  if (suggestion.scope_excluded?.length) {
    sections.push(
      `NGOÀI PHẠM VI\n- ${suggestion.scope_excluded.join("\n- ")}`
    );
  }

  if (suggestion.acceptance_criteria?.length) {
    sections.push(
      `TIÊU CHÍ NGHIỆM THU\n- ${suggestion.acceptance_criteria.join("\n- ")}`
    );
  }

  return sections.join("\n\n");
};


const StringList = ({
  items,
  emptyText = "Chưa có dữ liệu.",
  icon,
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
            <Text>{item}</Text>
          </Space>
        </List.Item>
      )}
    />
  );
};


const TagCollection = ({
  items,
  color = "blue",
}) => {
  if (!Array.isArray(items) || items.length === 0) {
    return (
      <Text type="secondary">
        Chưa có dữ liệu.
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
          color={color}
          key={`${item}-${index}`}
          style={{
            marginInlineEnd: 0,
            padding: "5px 10px",
            borderRadius: 999,
          }}
        >
          {item}
        </Tag>
      ))}
    </Flex>
  );
};


function JobAssistant() {
  const [form] = Form.useForm();

  const {
    message,
    modal,
  } = App.useApp();

  const [health, setHealth] = useState(null);
  const [languages, setLanguages] = useState([
    {
      code: "vi",
      name: "Tiếng Việt",
    },
    {
      code: "en",
      name: "English",
    },
  ]);

  const [detailLevels, setDetailLevels] = useState([
    "BASIC",
    "STANDARD",
    "DETAILED",
  ]);

  const [loadingConfig, setLoadingConfig] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const suggestion = result?.suggestion ?? null;
  const projectPayload = result?.project_payload ?? null;


  // ======================================================
  // LOAD INITIAL CONFIG
  // ======================================================

  useEffect(() => {
    const loadConfig = async () => {
      setLoadingConfig(true);

      const responses = await Promise.allSettled([
        jobAssistantApi.getHealth(),
        jobAssistantApi.getLanguages(),
        jobAssistantApi.getDetailLevels(),
        jobAssistantApi.getTemplate(),
      ]);

      const [
        healthResponse,
        languagesResponse,
        levelsResponse,
        templateResponse,
      ] = responses;

      if (healthResponse.status === "fulfilled") {
        setHealth(
          normalizeApiResponse(
            healthResponse.value
          )
        );
      }

      if (languagesResponse.status === "fulfilled") {
        const data = normalizeApiResponse(
          languagesResponse.value
        );

        if (
          Array.isArray(data?.languages)
          && data.languages.length > 0
        ) {
          setLanguages(data.languages);
        }
      }

      if (levelsResponse.status === "fulfilled") {
        const data = normalizeApiResponse(
          levelsResponse.value
        );

        if (
          Array.isArray(data?.levels)
          && data.levels.length > 0
        ) {
          setDetailLevels(data.levels);
        }
      }

      if (templateResponse.status === "fulfilled") {
        const data = normalizeApiResponse(
          templateResponse.value
        );

        if (data && typeof data === "object") {
          form.setFieldsValue({
            ...DEFAULT_VALUES,
            ...data,
            preferred_skills: Array.isArray(
              data.preferred_skills
            )
              ? data.preferred_skills
              : [],
          });
        }
      } else {
        form.setFieldsValue(
          DEFAULT_VALUES
        );
      }

      setLoadingConfig(false);
    };

    loadConfig();
  }, [form]);


  // ======================================================
  // DERIVED VALUES
  // ======================================================

  const milestonePercentage = useMemo(() => {
    if (!Array.isArray(suggestion?.milestones)) {
      return 0;
    }

    return suggestion.milestones.reduce(
      (total, item) => (
        total + Number(item?.percentage || 0)
      ),
      0
    );
  }, [suggestion]);


  const timelineItems = useMemo(() => {
    if (!Array.isArray(suggestion?.milestones)) {
      return [];
    }

    return suggestion.milestones.map(
      (milestone, index) => ({
        color: index === 0
          ? "blue"
          : index === suggestion.milestones.length - 1
            ? "green"
            : "gray",

        children: (
          <Card
            size="small"
            bordered
            style={{
              marginBottom: 8,
            }}
          >
            <Flex
              justify="space-between"
              align="flex-start"
              gap={16}
              wrap="wrap"
            >
              <div>
                <Text strong>
                  {index + 1}. {milestone.title}
                </Text>

                {milestone.description && (
                  <Paragraph
                    type="secondary"
                    style={{
                      marginTop: 6,
                      marginBottom: 8,
                    }}
                  >
                    {milestone.description}
                  </Paragraph>
                )}
              </div>

              <Space wrap>
                <Tag
                  icon={<ClockCircleOutlined />}
                  color="blue"
                >
                  {milestone.duration_days} ngày
                </Tag>

                <Tag color="purple">
                  {milestone.percentage}%
                </Tag>
              </Space>
            </Flex>

            {milestone.deliverables?.length > 0 && (
              <>
                <Divider
                  style={{
                    margin: "12px 0",
                  }}
                />

                <Text strong>
                  Sản phẩm bàn giao
                </Text>

                <StringList
                  items={milestone.deliverables}
                  icon={
                    <CheckCircleOutlined
                      style={{
                        color: "#52c41a",
                        marginTop: 4,
                      }}
                    />
                  }
                />
              </>
            )}

            <Progress
              percent={
                Math.min(
                  Number(
                    milestone.percentage || 0
                  ),
                  100
                )
              }
              showInfo={false}
              strokeColor={{
                "0%": "#4f46e5",
                "100%": "#06b6d4",
              }}
            />
          </Card>
        ),
      })
    );
  }, [suggestion]);


  // ======================================================
  // API HANDLERS
  // ======================================================

  const generateSuggestion = async (
    values,
    quick = false
  ) => {
    setGenerating(true);
    setError("");

    try {
      let response;

      if (quick) {
        response = await jobAssistantApi.quickGenerate(
          values.idea.trim()
        );
      } else {
        const payload = {
          idea: values.idea.trim(),

          category_hint: values.category_hint?.trim()
            || null,

          budget_hint: values.budget_hint
            ?? null,

          timeline_hint: values.timeline_hint
            ?? null,

          preferred_skills: Array.isArray(
            values.preferred_skills
          )
            ? values.preferred_skills
            : [],

          language: values.language,

          detail_level: values.detail_level,

          include_milestones: Boolean(
            values.include_milestones
          ),

          include_risks: Boolean(
            values.include_risks
          ),

          include_acceptance_criteria: Boolean(
            values.include_acceptance_criteria
          ),
        };

        response = await jobAssistantApi.generate(
          payload
        );
      }

      const data = normalizeApiResponse(
        response
      );

      if (!data?.suggestion) {
        throw new Error(
          "Backend không trả về dữ liệu gợi ý hợp lệ."
        );
      }

      setResult(data);

      message.success(
        quick
          ? "Đã sinh nhanh yêu cầu dự án."
          : "AI đã hoàn tất phân tích dự án."
      );

      window.setTimeout(() => {
        document
          .getElementById("job-assistant-result")
          ?.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });
      }, 150);
    } catch (requestError) {
      const errorMessage = extractErrorMessage(
        requestError
      );

      setError(errorMessage);
      message.error(errorMessage);
    } finally {
      setGenerating(false);
    }
  };


  const handleGenerate = async () => {
    try {
      const values = await form.validateFields();

      await generateSuggestion(
        values,
        false
      );
    } catch (validationError) {
      if (validationError?.errorFields) {
        message.warning(
          "Vui lòng kiểm tra lại các trường dữ liệu."
        );
      }
    }
  };


  const handleQuickGenerate = async () => {
    try {
      const idea = form.getFieldValue(
        "idea"
      );

      if (
        !idea
        || idea.trim().length < 10
      ) {
        form.setFields([
          {
            name: "idea",
            errors: [
              "Ý tưởng phải có ít nhất 10 ký tự.",
            ],
          },
        ]);

        return;
      }

      await generateSuggestion(
        {
          idea,
        },
        true
      );
    } catch {
      message.error(
        "Không thể sinh nhanh dự án."
      );
    }
  };


  const handleReset = () => {
    modal.confirm({
      title: "Làm mới biểu mẫu?",
      content:
        "Nội dung hiện tại và kết quả AI sẽ bị xóa.",
      okText: "Làm mới",
      cancelText: "Hủy",
      onOk: () => {
        form.resetFields();
        form.setFieldsValue(
          DEFAULT_VALUES
        );

        setResult(null);
        setError("");

        message.success(
          "Đã làm mới biểu mẫu."
        );
      },
    });
  };


  // ======================================================
  // COPY / SAVE
  // ======================================================

  const copyToClipboard = async (
    value,
    successText
  ) => {
    try {
      const text = typeof value === "string"
        ? value
        : JSON.stringify(value, null, 2);

      await navigator.clipboard.writeText(
        text
      );

      message.success(successText);
    } catch {
      message.error(
        "Không thể sao chép nội dung."
      );
    }
  };


  const handleSaveProjectPayload = () => {
    if (!projectPayload) {
      return;
    }

    localStorage.setItem(
      "aitasker_job_assistant_project",
      JSON.stringify(projectPayload)
    );

    message.success(
      "Đã lưu payload dự án vào trình duyệt."
    );
  };


  // ======================================================
  // RENDER
  // ======================================================

  return (
    <div
      style={{
        paddingBottom: 32,
      }}
    >
      <Card
        bordered={false}
        style={{
          marginBottom: 24,
          background:
            "linear-gradient(135deg, #111827 0%, #1e1b4b 55%, #312e81 100%)",
          overflow: "hidden",
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
              <Badge
                color="#22d3ee"
                text={
                  <Text
                    style={{
                      color: "#c7d2fe",
                      fontWeight: 600,
                    }}
                  >
                    AI-powered project planning
                  </Text>
                }
              />

              <Title
                level={2}
                style={{
                  color: "#ffffff",
                  margin: 0,
                }}
              >
                <RocketOutlined />
                {" "}AI Job Assistant
              </Title>

              <Paragraph
                style={{
                  color: "#cbd5e1",
                  maxWidth: 820,
                  margin: 0,
                  fontSize: 15,
                  lineHeight: 1.7,
                }}
              >
                Chuyển một ý tưởng ngắn thành bản mô tả
                dự án hoàn chỉnh gồm ngân sách, tiến độ,
                kỹ năng, công nghệ, milestones, tiêu chí
                nghiệm thu và rủi ro.
              </Paragraph>
            </Space>
          </Col>

          <Col
            xs={24}
            lg="auto"
          >
            <Card
              size="small"
              bordered={false}
              style={{
                minWidth: 230,
                background: "rgba(255, 255, 255, 0.08)",
              }}
            >
              {loadingConfig ? (
                <Space>
                  <Spin size="small" />
                  <Text
                    style={{
                      color: "#ffffff",
                    }}
                  >
                    Đang kiểm tra AI...
                  </Text>
                </Space>
              ) : (
                <Space direction="vertical">
                  <Space>
                    {health?.ai_available ? (
                      <CheckCircleOutlined
                        style={{
                          color: "#4ade80",
                        }}
                      />
                    ) : (
                      <WarningOutlined
                        style={{
                          color: "#fbbf24",
                        }}
                      />
                    )}

                    <Text
                      strong
                      style={{
                        color: "#ffffff",
                      }}
                    >
                      {health?.ai_available
                        ? "Gemini đang hoạt động"
                        : "Fallback đang hoạt động"}
                    </Text>
                  </Space>

                  <Text
                    style={{
                      color: "#cbd5e1",
                      fontSize: 12,
                    }}
                  >
                    Model: {health?.model || "Không xác định"}
                  </Text>
                </Space>
              )}
            </Card>
          </Col>
        </Row>
      </Card>

      <Row
        gutter={[24, 24]}
      >
        <Col
          xs={24}
          xl={9}
        >
          <Card
            title={
              <Space>
                <BulbOutlined />
                <span>Thông tin dự án</span>
              </Space>
            }
            extra={
              <Tooltip title="AI sử dụng dữ liệu này để xây dựng đề xuất">
                <InfoCircleOutlined />
              </Tooltip>
            }
          >
            {error && (
              <Alert
                type="error"
                showIcon
                closable
                message="Không thể tạo gợi ý"
                description={error}
                style={{
                  marginBottom: 20,
                }}
                onClose={() => setError("")}
              />
            )}

            <Form
              form={form}
              layout="vertical"
              initialValues={DEFAULT_VALUES}
              disabled={generating}
            >
              <Form.Item
                name="idea"
                label="Ý tưởng dự án"
                rules={[
                  {
                    required: true,
                    message:
                      "Vui lòng nhập ý tưởng dự án.",
                  },
                  {
                    min: 10,
                    message:
                      "Ý tưởng phải có ít nhất 10 ký tự.",
                  },
                  {
                    max: 10000,
                    message:
                      "Ý tưởng không được vượt quá 10.000 ký tự.",
                  },
                ]}
              >
                <TextArea
                  rows={7}
                  showCount
                  maxLength={10000}
                  placeholder={
                    "Ví dụ: Tôi muốn xây dựng chatbot AI "
                    + "tư vấn tuyển sinh, hỗ trợ trả lời "
                    + "câu hỏi về ngành học, học phí và hồ sơ..."
                  }
                />
              </Form.Item>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    name="category_hint"
                    label="Danh mục gợi ý"
                  >
                    <Input
                      placeholder="Chatbot, NLP..."
                      prefix={<ToolOutlined />}
                    />
                  </Form.Item>
                </Col>

                <Col span={12}>
                  <Form.Item
                    name="language"
                    label="Ngôn ngữ"
                  >
                    <Select
                      options={languages.map(
                        (item) => ({
                          value: item.code,
                          label: item.name,
                        })
                      )}
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    name="budget_hint"
                    label="Ngân sách dự kiến"
                    rules={[
                      {
                        type: "number",
                        min: 0,
                        message:
                          "Ngân sách không được âm.",
                      },
                    ]}
                  >
                    <InputNumber
                      min={0}
                      step={100000}
                      style={{
                        width: "100%",
                      }}
                      placeholder="20.000.000"
                      addonAfter="VND"
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

                <Col span={12}>
                  <Form.Item
                    name="timeline_hint"
                    label="Thời gian dự kiến"
                    rules={[
                      {
                        type: "number",
                        min: 1,
                        max: 365,
                        message:
                          "Thời gian phải từ 1 đến 365 ngày.",
                      },
                    ]}
                  >
                    <InputNumber
                      min={1}
                      max={365}
                      style={{
                        width: "100%",
                      }}
                      placeholder="30"
                      addonAfter="ngày"
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item
                name="preferred_skills"
                label="Kỹ năng ưu tiên"
                tooltip="Nhập kỹ năng rồi nhấn Enter"
              >
                <Select
                  mode="tags"
                  tokenSeparators={[
                    ",",
                    ";",
                  ]}
                  placeholder="Python, FastAPI, LLM, RAG..."
                  suffixIcon={<CodeOutlined />}
                />
              </Form.Item>

              <Form.Item
                name="detail_level"
                label="Mức độ chi tiết"
              >
                <Select
                  options={detailLevels.map(
                    (level) => ({
                      value: level,
                      label:
                        DETAIL_LEVEL_LABELS[level]
                        || level,
                    })
                  )}
                />
              </Form.Item>

              <Divider orientation="left">
                Nội dung cần tạo
              </Divider>

              <Space
                direction="vertical"
                size={12}
              >
                <Form.Item
                  name="include_milestones"
                  valuePropName="checked"
                  noStyle
                >
                  <Checkbox>
                    Sinh milestones
                  </Checkbox>
                </Form.Item>

                <Form.Item
                  name="include_risks"
                  valuePropName="checked"
                  noStyle
                >
                  <Checkbox>
                    Phân tích rủi ro
                  </Checkbox>
                </Form.Item>

                <Form.Item
                  name="include_acceptance_criteria"
                  valuePropName="checked"
                  noStyle
                >
                  <Checkbox>
                    Sinh tiêu chí nghiệm thu
                  </Checkbox>
                </Form.Item>
              </Space>

              <Divider />

              <Flex
                gap={10}
                wrap="wrap"
              >
                <Button
                  type="primary"
                  size="large"
                  icon={
                    generating
                      ? <LoadingOutlined />
                      : <ThunderboltOutlined />
                  }
                  loading={generating}
                  onClick={handleGenerate}
                >
                  Phân tích bằng AI
                </Button>

                <Button
                  size="large"
                  icon={<RocketOutlined />}
                  disabled={generating}
                  onClick={handleQuickGenerate}
                >
                  Sinh nhanh
                </Button>

                <Button
                  size="large"
                  danger
                  ghost
                  icon={<ClearOutlined />}
                  disabled={generating}
                  onClick={handleReset}
                >
                  Làm mới
                </Button>
              </Flex>
            </Form>
          </Card>
        </Col>

        <Col
          xs={24}
          xl={15}
        >
          {!suggestion ? (
            <Card
              style={{
                minHeight: 630,
              }}
            >
              <Result
                icon={
                  generating ? (
                    <Spin
                      indicator={
                        <LoadingOutlined
                          style={{
                            fontSize: 64,
                          }}
                          spin
                        />
                      }
                    />
                  ) : (
                    <RocketOutlined
                      style={{
                        color: "#4f46e5",
                      }}
                    />
                  )
                }
                title={
                  generating
                    ? "AI đang phân tích yêu cầu"
                    : "Chưa có kết quả phân tích"
                }
                subTitle={
                  generating
                    ? "Quá trình này có thể mất vài giây. Vui lòng không đóng trang."
                    : "Nhập ý tưởng dự án và chọn Phân tích bằng AI để bắt đầu."
                }
                extra={
                  !generating && (
                    <Steps
                      responsive
                      current={0}
                      items={[
                        {
                          title: "Nhập ý tưởng",
                          icon: <BulbOutlined />,
                        },
                        {
                          title: "AI phân tích",
                          icon: <ThunderboltOutlined />,
                        },
                        {
                          title: "Nhận kế hoạch",
                          icon: <FileTextOutlined />,
                        },
                      ]}
                    />
                  )
                }
              />
            </Card>
          ) : (
            <div
              id="job-assistant-result"
              style={{
                scrollMarginTop: 24,
              }}
            >
              <Card
                title={
                  <Space>
                    <CheckCircleOutlined
                      style={{
                        color: "#52c41a",
                      }}
                    />
                    <span>Kết quả AI đề xuất</span>
                  </Space>
                }
                extra={
                  <Space wrap>
                    <Tag color="geekblue">
                      {suggestion.category || "AI Project"}
                    </Tag>

                    <Tag color="cyan">
                      {suggestion.generated_by}
                    </Tag>
                  </Space>
                }
              >
                <Title level={3}>
                  {suggestion.title}
                </Title>

                <Paragraph
                  type="secondary"
                  style={{
                    fontSize: 15,
                  }}
                >
                  {suggestion.short_description}
                </Paragraph>

                <Divider />

                <Descriptions
                  bordered
                  column={{
                    xs: 1,
                    sm: 2,
                  }}
                  size="middle"
                >
                  <Descriptions.Item
                    label="Danh mục"
                  >
                    {suggestion.category || "Chưa xác định"}
                  </Descriptions.Item>

                  <Descriptions.Item
                    label="Ngôn ngữ"
                  >
                    {suggestion.language === "en"
                      ? "English"
                      : "Tiếng Việt"}
                  </Descriptions.Item>

                  <Descriptions.Item
                    label="Ngân sách đề xuất"
                  >
                    <Text strong>
                      {formatCurrency(
                        suggestion.budget?.recommended,
                        suggestion.budget?.currency
                      )}
                    </Text>
                  </Descriptions.Item>

                  <Descriptions.Item
                    label="Thời gian đề xuất"
                  >
                    <Text strong>
                      {
                        suggestion.timeline
                          ?.recommended_days
                      } ngày
                    </Text>
                  </Descriptions.Item>
                </Descriptions>
              </Card>

              <Row
                gutter={[16, 16]}
                style={{
                  marginTop: 16,
                }}
              >
                <Col
                  xs={24}
                  md={12}
                >
                  <Card>
                    <Statistic
                      title="Ngân sách khuyến nghị"
                      value={
                        Number(
                          suggestion.budget?.recommended
                          || 0
                        )
                      }
                      precision={0}
                      prefix={<DollarOutlined />}
                      suffix={
                        suggestion.budget?.currency
                        || "VND"
                      }
                      formatter={(value) => (
                        Number(value).toLocaleString(
                          "vi-VN"
                        )
                      )}
                    />

                    <Paragraph
                      type="secondary"
                      style={{
                        marginTop: 12,
                      }}
                    >
                      Khoảng từ{" "}
                      <Text strong>
                        {formatCurrency(
                          suggestion.budget?.minimum,
                          suggestion.budget?.currency
                        )}
                      </Text>
                      {" "}đến{" "}
                      <Text strong>
                        {formatCurrency(
                          suggestion.budget?.maximum,
                          suggestion.budget?.currency
                        )}
                      </Text>
                    </Paragraph>

                    <Text type="secondary">
                      {suggestion.budget?.explanation}
                    </Text>
                  </Card>
                </Col>

                <Col
                  xs={24}
                  md={12}
                >
                  <Card>
                    <Statistic
                      title="Tiến độ khuyến nghị"
                      value={
                        suggestion.timeline
                          ?.recommended_days
                        || 0
                      }
                      prefix={<ClockCircleOutlined />}
                      suffix="ngày"
                    />

                    <Paragraph
                      type="secondary"
                      style={{
                        marginTop: 12,
                      }}
                    >
                      Khoảng từ{" "}
                      <Text strong>
                        {
                          suggestion.timeline
                            ?.minimum_days
                        } ngày
                      </Text>
                      {" "}đến{" "}
                      <Text strong>
                        {
                          suggestion.timeline
                            ?.maximum_days
                        } ngày
                      </Text>
                    </Paragraph>

                    <Text type="secondary">
                      {suggestion.timeline?.explanation}
                    </Text>
                  </Card>
                </Col>
              </Row>

              <Collapse
                defaultActiveKey={[
                  "description",
                  "skills",
                  "milestones",
                ]}
                style={{
                  marginTop: 16,
                }}
                items={[
                  {
                    key: "description",
                    label: (
                      <Space>
                        <FileTextOutlined />
                        Mô tả dự án
                      </Space>
                    ),
                    children: (
                      <Paragraph
                        style={{
                          whiteSpace: "pre-line",
                          lineHeight: 1.8,
                        }}
                      >
                        {suggestion.description}
                      </Paragraph>
                    ),
                  },
                  {
                    key: "skills",
                    label: (
                      <Space>
                        <CodeOutlined />
                        Kỹ năng và công nghệ
                      </Space>
                    ),
                    children: (
                      <Row gutter={[24, 20]}>
                        <Col
                          xs={24}
                          md={12}
                        >
                          <Title level={5}>
                            Kỹ năng yêu cầu
                          </Title>

                          <TagCollection
                            items={
                              suggestion.required_skills
                            }
                            color="blue"
                          />
                        </Col>

                        <Col
                          xs={24}
                          md={12}
                        >
                          <Title level={5}>
                            Công nghệ đề xuất
                          </Title>

                          <TagCollection
                            items={
                              suggestion
                                .recommended_technologies
                            }
                            color="purple"
                          />
                        </Col>
                      </Row>
                    ),
                  },
                  {
                    key: "scope",
                    label: (
                      <Space>
                        <ToolOutlined />
                        Mục tiêu và phạm vi
                      </Space>
                    ),
                    children: (
                      <Row gutter={[24, 24]}>
                        <Col
                          xs={24}
                          lg={8}
                        >
                          <Title level={5}>
                            Mục tiêu
                          </Title>

                          <StringList
                            items={
                              suggestion.objectives
                            }
                            icon={
                              <CheckCircleOutlined
                                style={{
                                  color: "#52c41a",
                                  marginTop: 4,
                                }}
                              />
                            }
                          />
                        </Col>

                        <Col
                          xs={24}
                          lg={8}
                        >
                          <Title level={5}>
                            Trong phạm vi
                          </Title>

                          <StringList
                            items={
                              suggestion.scope_included
                            }
                            icon={
                              <CheckCircleOutlined
                                style={{
                                  color: "#1677ff",
                                  marginTop: 4,
                                }}
                              />
                            }
                          />
                        </Col>

                        <Col
                          xs={24}
                          lg={8}
                        >
                          <Title level={5}>
                            Ngoài phạm vi
                          </Title>

                          <StringList
                            items={
                              suggestion.scope_excluded
                            }
                            icon={
                              <WarningOutlined
                                style={{
                                  color: "#faad14",
                                  marginTop: 4,
                                }}
                              />
                            }
                          />
                        </Col>
                      </Row>
                    ),
                  },
                  {
                    key: "milestones",
                    label: (
                      <Space>
                        <ClockCircleOutlined />
                        Milestones
                        <Tag color="purple">
                          {milestonePercentage.toFixed(2)}%
                        </Tag>
                      </Space>
                    ),
                    children: timelineItems.length > 0
                      ? (
                        <Timeline
                          items={timelineItems}
                        />
                      )
                      : (
                        <Empty
                          description="Không tạo milestones."
                        />
                      ),
                  },
                  {
                    key: "acceptance",
                    label: (
                      <Space>
                        <SafetyCertificateOutlined />
                        Tiêu chí nghiệm thu
                      </Space>
                    ),
                    children: (
                      <StringList
                        items={
                          suggestion
                            .acceptance_criteria
                        }
                        icon={
                          <CheckCircleOutlined
                            style={{
                              color: "#52c41a",
                              marginTop: 4,
                            }}
                          />
                        }
                      />
                    ),
                  },
                  {
                    key: "risks",
                    label: (
                      <Space>
                        <WarningOutlined />
                        Rủi ro và giả định
                      </Space>
                    ),
                    children: (
                      <Row gutter={[24, 24]}>
                        <Col
                          xs={24}
                          md={12}
                        >
                          <Alert
                            type="warning"
                            showIcon
                            message="Rủi ro"
                            description={
                              <StringList
                                items={suggestion.risks}
                                icon={
                                  <WarningOutlined
                                    style={{
                                      color: "#faad14",
                                      marginTop: 4,
                                    }}
                                  />
                                }
                              />
                            }
                          />
                        </Col>

                        <Col
                          xs={24}
                          md={12}
                        >
                          <Alert
                            type="info"
                            showIcon
                            message="Giả định"
                            description={
                              <StringList
                                items={
                                  suggestion.assumptions
                                }
                                icon={
                                  <InfoCircleOutlined
                                    style={{
                                      color: "#1677ff",
                                      marginTop: 4,
                                    }}
                                  />
                                }
                              />
                            }
                          />
                        </Col>
                      </Row>
                    ),
                  },
                  {
                    key: "questions",
                    label: (
                      <Space>
                        <QuestionCircleOutlined />
                        Câu hỏi dành cho chuyên gia
                      </Space>
                    ),
                    children: (
                      <StringList
                        items={
                          suggestion
                            .suggested_questions_for_expert
                        }
                        icon={
                          <QuestionCircleOutlined
                            style={{
                              color: "#722ed1",
                              marginTop: 4,
                            }}
                          />
                        }
                      />
                    ),
                  },
                  {
                    key: "payload",
                    label: (
                      <Space>
                        <CodeOutlined />
                        Payload tạo Project
                      </Space>
                    ),
                    children: projectPayload ? (
                      <pre
                        style={{
                          background: "#020617",
                          color: "#dbeafe",
                          padding: 18,
                          borderRadius: 10,
                          overflow: "auto",
                          maxHeight: 430,
                          fontSize: 13,
                          lineHeight: 1.6,
                        }}
                      >
                        {JSON.stringify(
                          projectPayload,
                          null,
                          2
                        )}
                      </pre>
                    ) : (
                      <Empty />
                    ),
                  },
                ]}
              />

              <Card
                style={{
                  marginTop: 16,
                }}
              >
                <Flex
                  gap={12}
                  wrap="wrap"
                >
                  <Button
                    icon={<CopyOutlined />}
                    onClick={() => copyToClipboard(
                      buildProjectDescription(
                        suggestion
                      ),
                      "Đã sao chép mô tả dự án."
                    )}
                  >
                    Sao chép mô tả
                  </Button>

                  <Button
                    icon={<CodeOutlined />}
                    onClick={() => copyToClipboard(
                      result,
                      "Đã sao chép toàn bộ JSON."
                    )}
                  >
                    Sao chép JSON
                  </Button>

                  <Button
                    type="primary"
                    icon={<SaveOutlined />}
                    onClick={
                      handleSaveProjectPayload
                    }
                  >
                    Lưu để tạo Project
                  </Button>

                  <Button
                    icon={<ReloadOutlined />}
                    onClick={handleGenerate}
                    loading={generating}
                  >
                    Sinh lại
                  </Button>
                </Flex>
              </Card>
            </div>
          )}
        </Col>
      </Row>
    </div>
  );
}


export default JobAssistant;