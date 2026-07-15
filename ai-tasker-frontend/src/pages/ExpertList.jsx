import React, {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  App,
  Button,
  Card,
  Form,
  Input,
  Modal,
  Select,
  Space,
  Table,
  Tag,
  Typography,
} from "antd";

import {
  CloseCircleOutlined,
  EyeOutlined,
  PlusOutlined,
  ReloadOutlined,
} from "@ant-design/icons";

import axiosClient from "../api/axiosClient";

const { Title, Text } = Typography;

const AVAILABLE_SKILLS = [
  "Python",
  "NLP",
  "PyTorch",
  "TensorFlow",
  "Generative AI",
  "LLM Fine-tuning",
  "LangChain",
  "Computer Vision",
  "OpenCV",
  "Prompt Engineering",
  "Docker",
  "FastAPI",
  "Data Science",
  "Scikit-Learn",
];

const ExpertList = () => {
  const { message } = App.useApp();

  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [experts, setExperts] = useState([]);
  const [searchText, setSearchText] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [form] = Form.useForm();

  // ==========================================================
  // LOAD EXPERTS
  // ==========================================================

  const fetchExperts = useCallback(async () => {
    try {
      setLoading(true);

      const response = await axiosClient.get("/experts");

      const data =
        response.data?.data ||
        response.data?.results ||
        response.data ||
        [];

      setExperts(
        Array.isArray(data)
          ? data
          : []
      );
    } catch (error) {
      console.error("Lỗi tải chuyên gia:", error);

      const detail =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        "Không thể tải danh sách chuyên gia từ Backend.";

      message.error(detail);
    } finally {
      setLoading(false);
    }
  }, [message]);

  useEffect(() => {
    fetchExperts();
  }, [fetchExperts]);

  // ==========================================================
  // FILTER
  // ==========================================================

  const filteredExperts = useMemo(() => {
    const keyword = searchText
      .trim()
      .toLowerCase();

    if (!keyword) {
      return experts;
    }

    return experts.filter((expert) => {
      const id = String(expert.id || "").toLowerCase();
      const fullName = String(
        expert.full_name ||
        expert.name ||
        ""
      ).toLowerCase();

      const email = String(
        expert.email || ""
      ).toLowerCase();

      return (
        id.includes(keyword) ||
        fullName.includes(keyword) ||
        email.includes(keyword)
      );
    });
  }, [experts, searchText]);

  // ==========================================================
  // CREATE EXPERT
  // ==========================================================

  const handleAddExpert = async (values) => {
    try {
      setSubmitting(true);

      const payload = {
        full_name: values.full_name,
        email: values.email,
        skills: values.skills || [],
        status: "Available",
      };

      await axiosClient.post(
        "/experts",
        payload
      );

      message.success(
        "Thêm chuyên gia AI thành công."
      );

      setIsModalOpen(false);
      form.resetFields();

      await fetchExperts();
    } catch (error) {
      console.error(
        "Lỗi thêm chuyên gia:",
        error
      );

      const detail =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        "Không thể thêm chuyên gia.";

      message.error(detail);
    } finally {
      setSubmitting(false);
    }
  };

  const closeModal = () => {
    setIsModalOpen(false);
    form.resetFields();
  };

  // ==========================================================
  // COLUMNS
  // ==========================================================

  const columns = [
    {
      title: "Mã chuyên gia",
      dataIndex: "id",
      key: "id",
      render: (id) => {
        const value = String(id || "");
        const shortId =
          value.length > 6
            ? `${value.slice(0, 6).toUpperCase()}...`
            : value.toUpperCase();

        return (
          <Text
            strong
            style={{
              color: "#fff",
            }}
          >
            EXP-{shortId || "N/A"}
          </Text>
        );
      },
    },
    {
      title: "Họ và tên",
      dataIndex: "full_name",
      key: "full_name",
      render: (text, record) => (
        <Text
          style={{
            color: "#fff",
          }}
        >
          {text ||
            record.name ||
            "Chưa cập nhật"}
        </Text>
      ),
    },
    {
      title: "Email liên hệ",
      dataIndex: "email",
      key: "email",
      render: (text) => (
        <Text
          style={{
            color: "#9ca3af",
          }}
        >
          {text || "N/A"}
        </Text>
      ),
    },
    {
      title: "Kỹ năng core",
      dataIndex: "skills",
      key: "skills",
      render: (skills) => {
        if (
          !Array.isArray(skills) ||
          skills.length === 0
        ) {
          return (
            <Tag color="default">
              Chưa có
            </Tag>
          );
        }

        return (
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: 4,
            }}
          >
            {skills.map((skill, index) => {
              const skillName =
                typeof skill === "object"
                  ? skill?.name
                  : skill;

              return skillName ? (
                <Tag
                  color="blue"
                  key={`${skillName}-${index}`}
                >
                  {skillName}
                </Tag>
              ) : null;
            })}
          </div>
        );
      },
    },
    {
      title: "Trạng thái",
      dataIndex: "status",
      key: "status",
      render: (status) => {
        const normalizedStatus = String(
          status || ""
        ).toLowerCase();

        const isAvailable =
          normalizedStatus === "available" ||
          normalizedStatus === "active" ||
          normalizedStatus === "hoạt động";

        return (
          <Tag
            color={
              isAvailable
                ? "green"
                : "gold"
            }
          >
            {status || "Chờ duyệt"}
          </Tag>
        );
      },
    },
    {
      title: "Hành động",
      key: "action",
      render: () => (
        <Space size="middle">
          <Button
            type="text"
            icon={
              <EyeOutlined
                style={{
                  color: "#9ca3af",
                }}
              />
            }
          />

          <Button
            type="text"
            icon={
              <CloseCircleOutlined
                style={{
                  color: "#ef4444",
                }}
              />
            }
          />
        </Space>
      ),
    },
  ];

  return (
    <div
      style={{
        padding: 24,
        background: "#090d16",
        minHeight: "100vh",
      }}
    >
      <style>{`
        .expert-search.ant-input-affix-wrapper,
        .expert-search .ant-input,
        .expert-search .ant-input-group-addon,
        .expert-search .ant-btn {
          background: #1f2937 !important;
          color: #ffffff !important;
          border-color: #374151 !important;
        }

        .expert-search .ant-input::placeholder {
          color: #6b7280 !important;
        }

        .ant-table-thead > tr > th {
          background: #1f2937 !important;
          color: #ffffff !important;
          border-bottom: 1px solid #374151 !important;
        }

        .ant-table-tbody > tr > td {
          background: #111827 !important;
          border-bottom: 1px solid #1f2937 !important;
        }

        .ant-table-tbody > tr:hover > td {
          background: #1f2937 !important;
        }

        .ant-pagination-item a,
        .ant-pagination-item-link {
          color: #ffffff !important;
        }

        .ant-pagination-item-active {
          background: #4f46e5 !important;
          border-color: #4f46e5 !important;
        }

        .ant-select-multiple .ant-select-selection-item {
          background: #374151 !important;
          color: #ffffff !important;
          border: 1px solid #4b5563 !important;
        }

        .ant-select-multiple .ant-select-selection-item-remove {
          color: #ef4444 !important;
        }
      `}</style>

      <Card
        style={{
          background: "#111827",
          border: "1px solid #1f2937",
          borderRadius: 12,
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: 16,
            flexWrap: "wrap",
            marginBottom: 24,
          }}
        >
          <div>
            <Title
              level={3}
              style={{
                color: "#fff",
                margin: 0,
              }}
            >
              Quản lý mạng lưới Chuyên gia AI
            </Title>

            <Text
              style={{
                color: "#6b7280",
              }}
            >
              Hệ thống kiểm duyệt thông tin, kỹ năng và điều phối
              phân tác việc làm tự động
            </Text>
          </div>

          <Space>
            <Button
              icon={<ReloadOutlined />}
              onClick={fetchExperts}
              loading={loading}
              ghost
              style={{
                color: "#9ca3af",
                borderColor: "#374151",
              }}
            >
              Làm mới
            </Button>

            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() =>
                setIsModalOpen(true)
              }
              style={{
                background: "#4f46e5",
              }}
            >
              Thêm chuyên gia
            </Button>
          </Space>
        </div>

        <Input.Search
          className="expert-search"
          allowClear
          value={searchText}
          placeholder="Tìm theo tên, email hoặc mã chuyên gia..."
          style={{
            marginBottom: 24,
          }}
          onChange={(event) =>
            setSearchText(
              event.target.value
            )
          }
        />

        <Table
          dataSource={filteredExperts}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 5,
            showSizeChanger: false,
          }}
        />
      </Card>

      <Modal
        title={
          <span
            style={{
              color: "#fff",
              fontSize: 18,
              fontWeight: 600,
            }}
          >
            Thêm chuyên gia AI mới
          </span>
        }
        open={isModalOpen}
        onCancel={closeModal}
        onOk={() => form.submit()}
        confirmLoading={submitting}
        destroyOnHidden
        okText="Xác nhận"
        cancelText="Hủy bỏ"
        styles={{
          body: {
            background: "#111827",
          },
          content: {
            background: "#111827",
            border: "1px solid #1f2937",
          },
          header: {
            background: "#111827",
          },
        }}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleAddExpert}
          preserve={false}
          style={{
            marginTop: 16,
          }}
        >
          <Form.Item
            name="full_name"
            label={
              <span
                style={{
                  color: "#9ca3af",
                }}
              >
                Họ và tên
              </span>
            }
            rules={[
              {
                required: true,
                whitespace: true,
                message:
                  "Vui lòng nhập họ tên chuyên gia.",
              },
            ]}
          >
            <Input
              placeholder="Ví dụ: Khánh Hoàng"
              style={{
                background: "#1f2937",
                color: "#fff",
                border: "1px solid #374151",
              }}
            />
          </Form.Item>

          <Form.Item
            name="email"
            label={
              <span
                style={{
                  color: "#9ca3af",
                }}
              >
                Email liên hệ
              </span>
            }
            rules={[
              {
                required: true,
                message:
                  "Vui lòng nhập email.",
              },
              {
                type: "email",
                message:
                  "Email không đúng định dạng.",
              },
            ]}
          >
            <Input
              placeholder="example@gmail.com"
              style={{
                background: "#1f2937",
                color: "#fff",
                border: "1px solid #374151",
              }}
            />
          </Form.Item>

          <Form.Item
            name="skills"
            label={
              <span
                style={{
                  color: "#9ca3af",
                }}
              >
                Kỹ năng core
              </span>
            }
            rules={[
              {
                required: true,
                type: "array",
                min: 1,
                message:
                  "Vui lòng chọn ít nhất một kỹ năng.",
              },
            ]}
          >
            <Select
              mode="tags"
              placeholder="Chọn hoặc nhập kỹ năng..."
              maxTagCount="responsive"
              styles={{
                popup: {
                  root: {
                    background: "#1f2937",
                  },
                },
              }}
              options={AVAILABLE_SKILLS.map(
                (skill) => ({
                  label: skill,
                  value: skill,
                })
              )}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ExpertList;