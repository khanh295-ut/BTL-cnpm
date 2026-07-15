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
  Descriptions,
  Empty,
  Flex,
  Form,
  Input,
  InputNumber,
  Modal,
  Popconfirm,
  Select,
  Space,
  Spin,
  Table,
  Tag,
  Typography,
} from "antd";

import {
  CloseCircleOutlined,
  DeleteOutlined,
  EditOutlined,
  EyeOutlined,
  PlusOutlined,
  ReloadOutlined,
  TeamOutlined,
} from "@ant-design/icons";

import expertApi from "../api/expertApi";

const { Title, Text } = Typography;
const { TextArea } = Input;


/* =========================================================
   CONSTANTS
========================================================= */

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


/* =========================================================
   HELPERS
========================================================= */

const extractArray = (response) => {
  if (!response) return [];

  if (Array.isArray(response)) {
    return response;
  }

  if (Array.isArray(response.data)) {
    return response.data;
  }

  if (Array.isArray(response.data?.data)) {
    return response.data.data;
  }

  if (Array.isArray(response.data?.results)) {
    return response.data.results;
  }

  return [];
};


const formatCurrency = (value) => {
  const amount = Number(value || 0);

  if (Number.isNaN(amount)) {
    return "0 VNĐ";
  }

  return `${amount.toLocaleString("vi-VN")} VNĐ`;
};


const formatDateTime = (value) => {
  if (!value) return "Chưa cập nhật";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return date.toLocaleString("vi-VN");
};


const normalizeSkillsForForm = (skills) => {
  if (!Array.isArray(skills)) {
    return [];
  }

  return skills
    .map((skill) => {
      if (typeof skill === "string") {
        return skill;
      }

      return (
        skill?.name ||
        skill?.title ||
        skill?.skill_name ||
        ""
      );
    })
    .filter(Boolean);
};


const normalizeSkillsForPayload = (skills) => {
  if (!Array.isArray(skills)) {
    return [];
  }

  return skills
    .map((skill) => {
      const name =
        typeof skill === "string"
          ? skill.trim()
          : String(
              skill?.name ||
              skill?.title ||
              ""
            ).trim();

      return name ? { name } : null;
    })
    .filter(Boolean);
};


const getErrorMessage = (
  error,
  fallback = "Đã xảy ra lỗi."
) => {
  const detail = error?.response?.data?.detail;
  const backendMessage =
    error?.response?.data?.message;

  if (typeof detail === "string") {
    return detail;
  }

  if (typeof backendMessage === "string") {
    return backendMessage;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const field = Array.isArray(item?.loc)
          ? item.loc
              .filter((part) => part !== "body")
              .join(".")
          : "Dữ liệu";

        return `${field}: ${
          item?.msg || "Không hợp lệ"
        }`;
      })
      .join("; ");
  }

  if (error?.code === "ERR_NETWORK") {
    return "Không thể kết nối tới Backend FastAPI.";
  }

  return fallback;
};


/* =========================================================
   MAIN COMPONENT
========================================================= */

const ExpertList = () => {
  const { message } = App.useApp();

  const [form] = Form.useForm();

  const [loading, setLoading] =
    useState(true);

  const [submitting, setSubmitting] =
    useState(false);

  const [deletingId, setDeletingId] =
    useState(null);

  const [experts, setExperts] =
    useState([]);

  const [searchText, setSearchText] =
    useState("");

  const [modalOpen, setModalOpen] =
    useState(false);

  const [detailModalOpen, setDetailModalOpen] =
    useState(false);

  const [selectedExpert, setSelectedExpert] =
    useState(null);

  const [editingExpert, setEditingExpert] =
    useState(null);


  /* =======================================================
     LOAD EXPERTS
  ======================================================= */

  const fetchExperts = useCallback(async () => {
    try {
      setLoading(true);

      const response =
        await expertApi.getAll();

      setExperts(
        extractArray(response)
      );
    } catch (error) {
      console.error(
        "Lỗi tải chuyên gia:",
        error?.response?.data || error
      );

      message.error(
        getErrorMessage(
          error,
          "Không thể tải danh sách chuyên gia."
        )
      );
    } finally {
      setLoading(false);
    }
  }, [message]);


  useEffect(() => {
    fetchExperts();
  }, [fetchExperts]);


  /* =======================================================
     FILTER
  ======================================================= */

  const filteredExperts = useMemo(() => {
    const keyword = searchText
      .trim()
      .toLowerCase();

    if (!keyword) {
      return experts;
    }

    return experts.filter((expert) => {
      const skills = normalizeSkillsForForm(
        expert.skills
      ).join(" ");

      const source = [
        expert.full_name,
        expert.title,
        expert.location,
        skills,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      return source.includes(keyword);
    });
  }, [experts, searchText]);


  /* =======================================================
     OPEN CREATE MODAL
  ======================================================= */

  const openCreateModal = () => {
    setEditingExpert(null);

    form.resetFields();

    form.setFieldsValue({
      hourly_rate: 0,
      skills: [],
    });

    setModalOpen(true);
  };


  /* =======================================================
     OPEN EDIT MODAL
  ======================================================= */

  const openEditModal = (expert) => {
    setEditingExpert(expert);

    form.setFieldsValue({
      full_name: expert.full_name || "",
      title: expert.title || "",
      bio: expert.bio || "",
      hourly_rate: Number(
        expert.hourly_rate || 0
      ),
      location: expert.location || "",
      skills: normalizeSkillsForForm(
        expert.skills
      ),
    });

    setModalOpen(true);
  };


  /* =======================================================
     CLOSE FORM MODAL
  ======================================================= */

  const closeModal = () => {
    setModalOpen(false);
    setEditingExpert(null);
    form.resetFields();
  };


  /* =======================================================
     SUBMIT CREATE / UPDATE
  ======================================================= */

  const handleSubmit = async (values) => {
    try {
      setSubmitting(true);

      const payload = {
        full_name: values.full_name.trim(),
        title:
          values.title?.trim() || null,
        bio:
          values.bio?.trim() || null,
        hourly_rate: Number(
          values.hourly_rate || 0
        ),
        location:
          values.location?.trim() || null,
        skills: normalizeSkillsForPayload(
          values.skills
        ),
      };

      console.log(
        editingExpert
          ? "Payload cập nhật chuyên gia:"
          : "Payload thêm chuyên gia:",
        payload
      );

      if (editingExpert?.id) {
        await expertApi.update(
          editingExpert.id,
          payload
        );

        message.success(
          "Cập nhật chuyên gia thành công."
        );
      } else {
        await expertApi.create(payload);

        message.success(
          "Thêm chuyên gia AI thành công."
        );
      }

      closeModal();
      await fetchExperts();
    } catch (error) {
      console.error(
        editingExpert
          ? "Lỗi cập nhật chuyên gia:"
          : "Lỗi thêm chuyên gia:",
        error?.response?.data || error
      );

      message.error(
        getErrorMessage(
          error,
          editingExpert
            ? "Không thể cập nhật chuyên gia."
            : "Không thể thêm chuyên gia."
        )
      );
    } finally {
      setSubmitting(false);
    }
  };


  /* =======================================================
     VIEW DETAIL
  ======================================================= */

  const openDetailModal = (expert) => {
    setSelectedExpert(expert);
    setDetailModalOpen(true);
  };


  const closeDetailModal = () => {
    setSelectedExpert(null);
    setDetailModalOpen(false);
  };


  /* =======================================================
     DELETE
  ======================================================= */

  const handleDelete = async (expertId) => {
    try {
      setDeletingId(expertId);

      await expertApi.delete(expertId);

      message.success(
        "Xóa chuyên gia thành công."
      );

      await fetchExperts();
    } catch (error) {
      console.error(
        "Lỗi xóa chuyên gia:",
        error?.response?.data || error
      );

      message.error(
        getErrorMessage(
          error,
          "Không thể xóa chuyên gia."
        )
      );
    } finally {
      setDeletingId(null);
    }
  };


  /* =======================================================
     TABLE COLUMNS
  ======================================================= */

  const columns = [
    {
      title: "Mã chuyên gia",
      dataIndex: "id",
      key: "id",
      width: 180,
      render: (id) => {
        const value = String(id || "");

        return (
          <Text
            code
            style={{
              color: "#d1d5db",
              fontSize: 12,
              wordBreak: "break-all",
            }}
          >
            {value || "N/A"}
          </Text>
        );
      },
    },
    {
      title: "Họ và tên",
      dataIndex: "full_name",
      key: "full_name",
      width: 180,
      sorter: (a, b) =>
        String(a.full_name || "").localeCompare(
          String(b.full_name || "")
        ),
      render: (text) => (
        <Text
          strong
          style={{ color: "#f3f4f6" }}
        >
          {text || "Chưa cập nhật"}
        </Text>
      ),
    },
    {
      title: "Chức danh",
      dataIndex: "title",
      key: "title",
      width: 170,
      render: (text) => (
        <Text style={{ color: "#d1d5db" }}>
          {text || "Chưa cập nhật"}
        </Text>
      ),
    },
    {
      title: "Kỹ năng core",
      dataIndex: "skills",
      key: "skills",
      width: 240,
      render: (skills) => {
        const names =
          normalizeSkillsForForm(skills);

        if (names.length === 0) {
          return (
            <Tag color="default">
              Chưa có
            </Tag>
          );
        }

        return (
          <Flex
            wrap="wrap"
            gap={4}
          >
            {names.map((name) => (
              <Tag
                color="blue"
                key={name}
              >
                {name}
              </Tag>
            ))}
          </Flex>
        );
      },
    },
    {
      title: "Mức phí / giờ",
      dataIndex: "hourly_rate",
      key: "hourly_rate",
      width: 140,
      align: "right",
      sorter: (a, b) =>
        Number(a.hourly_rate || 0) -
        Number(b.hourly_rate || 0),
      render: (value) => (
        <Text
          strong
          style={{ color: "#10b981" }}
        >
          {formatCurrency(value)}
        </Text>
      ),
    },
    {
      title: "Địa điểm",
      dataIndex: "location",
      key: "location",
      width: 130,
      render: (text) => (
        <Text style={{ color: "#d1d5db" }}>
          {text || "-"}
        </Text>
      ),
    },
    {
      title: "Hành động",
      key: "actions",
      width: 170,
      fixed: "right",
      align: "center",
      render: (_, record) => (
        <Space size="small">
          <Button
            type="text"
            title="Xem chi tiết"
            icon={
              <EyeOutlined
                style={{
                  color: "#818cf8",
                }}
              />
            }
            onClick={() =>
              openDetailModal(record)
            }
          />

          <Button
            type="text"
            title="Chỉnh sửa"
            icon={
              <EditOutlined
                style={{
                  color: "#f59e0b",
                }}
              />
            }
            onClick={() =>
              openEditModal(record)
            }
          />

          <Popconfirm
            title="Xóa chuyên gia"
            description="Bạn có chắc chắn muốn xóa chuyên gia này?"
            okText="Xóa"
            cancelText="Hủy"
            okButtonProps={{
              danger: true,
            }}
            onConfirm={() =>
              handleDelete(record.id)
            }
          >
            <Button
              type="text"
              danger
              title="Xóa chuyên gia"
              loading={
                deletingId === record.id
              }
              icon={<DeleteOutlined />}
            />
          </Popconfirm>
        </Space>
      ),
    },
  ];


  /* =======================================================
     UI
  ======================================================= */

  return (
    <div
      style={{
        padding: 24,
        minHeight: "100vh",
        background: "#090d16",
      }}
    >
      <Card
        variant="none"
        style={{
          background: "#111827",
          border:
            "1px solid #1f2937",
          borderRadius: 14,
        }}
      >
        {/* HEADER */}

        <Flex
          justify="space-between"
          align="center"
          wrap="wrap"
          gap="middle"
          style={{
            marginBottom: 24,
          }}
        >
          <Space align="start">
            <TeamOutlined
              style={{
                color: "#f3f4f6",
                fontSize: 26,
                marginTop: 5,
              }}
            />

            <div>
              <Title
                level={3}
                style={{
                  margin: 0,
                  color: "#fff",
                }}
              >
                Quản lý mạng lưới
                Chuyên gia AI
              </Title>

              <Text
                style={{
                  color: "#9ca3af",
                }}
              >
                Quản lý hồ sơ, kỹ năng,
                mức phí và địa điểm làm việc
              </Text>
            </div>
          </Space>

          <Space wrap>
            <Button
              icon={
                <ReloadOutlined />
              }
              onClick={fetchExperts}
              loading={loading}
              style={{
                color: "#d1d5db",
                background: "#111827",
                borderColor: "#374151",
              }}
            >
              Làm mới
            </Button>

            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={openCreateModal}
              style={{
                background: "#4f46e5",
              }}
            >
              Thêm chuyên gia
            </Button>
          </Space>
        </Flex>


        {/* SEARCH */}

        <Input.Search
          allowClear
          placeholder="Tìm theo tên, chức danh, địa điểm hoặc kỹ năng..."
          value={searchText}
          onChange={(event) =>
            setSearchText(
              event.target.value
            )
          }
          style={{
            maxWidth: 480,
            marginBottom: 24,
          }}
        />


        {/* TABLE */}

        {loading ? (
          <Flex
            vertical
            justify="center"
            align="center"
            style={{
              minHeight: 300,
            }}
          >
            <Spin size="large" />

            <Text
              style={{
                color: "#9ca3af",
                marginTop: 16,
              }}
            >
              Đang tải danh sách chuyên gia...
            </Text>
          </Flex>
        ) : (
          <Table
            rowKey="id"
            columns={columns}
            dataSource={filteredExperts}
            className="expert-dark-table"
            scroll={{ x: 1250 }}
            pagination={{
              pageSize: 6,
              showSizeChanger: false,
              showTotal: (total) =>
                `Tổng ${total} chuyên gia`,
            }}
            locale={{
              emptyText: (
                <Empty
                  image={
                    Empty.PRESENTED_IMAGE_SIMPLE
                  }
                  description={
                    <span
                      style={{
                        color: "#9ca3af",
                      }}
                    >
                      Chưa có chuyên gia nào.
                    </span>
                  }
                >
                  <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={openCreateModal}
                  >
                    Thêm chuyên gia đầu tiên
                  </Button>
                </Empty>
              ),
            }}
          />
        )}
      </Card>


      {/* ===================================================
          CREATE / EDIT MODAL
      =================================================== */}

      <Modal
        title={
          <span>
            {editingExpert
              ? "Cập nhật chuyên gia AI"
              : "Thêm chuyên gia AI mới"}
          </span>
        }
        open={modalOpen}
        onCancel={closeModal}
        onOk={() => form.submit()}
        confirmLoading={submitting}
        okText={
          editingExpert
            ? "Cập nhật"
            : "Thêm chuyên gia"
        }
        cancelText="Hủy"
        destroyOnHidden
        width={680}
        styles={{
          content: {
            background: "#111827",
            border:
              "1px solid #1f2937",
          },
          header: {
            background: "#111827",
          },
          body: {
            background: "#111827",
          },
        }}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          requiredMark="optional"
          style={{
            marginTop: 20,
          }}
        >
          <Form.Item
            name="full_name"
            label={
              <Text
                style={{
                  color: "#d1d5db",
                }}
              >
                Họ và tên
              </Text>
            }
            rules={[
              {
                required: true,
                message:
                  "Vui lòng nhập họ tên.",
              },
              {
                max: 255,
                message:
                  "Họ tên không được vượt quá 255 ký tự.",
              },
            ]}
          >
            <Input
              placeholder="Ví dụ: Nguyễn Văn A"
            />
          </Form.Item>


          <Form.Item
            name="title"
            label={
              <Text
                style={{
                  color: "#d1d5db",
                }}
              >
                Chức danh
              </Text>
            }
            rules={[
              {
                max: 255,
                message:
                  "Chức danh không được vượt quá 255 ký tự.",
              },
            ]}
          >
            <Input
              placeholder="Ví dụ: Senior AI Engineer"
            />
          </Form.Item>


          <Form.Item
            name="bio"
            label={
              <Text
                style={{
                  color: "#d1d5db",
                }}
              >
                Giới thiệu
              </Text>
            }
            rules={[
              {
                max: 500,
                message:
                  "Giới thiệu không được vượt quá 500 ký tự.",
              },
            ]}
          >
            <TextArea
              rows={4}
              showCount
              maxLength={500}
              placeholder="Mô tả kinh nghiệm, thế mạnh và lĩnh vực chuyên môn..."
            />
          </Form.Item>


          <Form.Item
            name="hourly_rate"
            label={
              <Text
                style={{
                  color: "#d1d5db",
                }}
              >
                Mức phí theo giờ
              </Text>
            }
            rules={[
              {
                required: true,
                message:
                  "Vui lòng nhập mức phí.",
              },
              {
                validator: (_, value) => {
                  if (
                    value === undefined ||
                    value === null
                  ) {
                    return Promise.resolve();
                  }

                  if (Number(value) < 0) {
                    return Promise.reject(
                      new Error(
                        "Mức phí không được âm."
                      )
                    );
                  }

                  return Promise.resolve();
                },
              },
            ]}
          >
            <Space.Compact
              style={{
                width: "100%",
              }}
            >
              <InputNumber
                min={0}
                precision={2}
                placeholder="Ví dụ: 500000"
                style={{
                  width:
                    "calc(100% - 64px)",
                }}
                formatter={(value) =>
                  `${
                    value || ""
                  }`.replace(
                    /\B(?=(\d{3})+(?!\d))/g,
                    "."
                  )
                }
                parser={(value) =>
                  value
                    ?.replace(
                      /\./g,
                      ""
                    )
                    .replace(
                      /[^\d.]/g,
                      ""
                    ) || ""
                }
              />

              <Button
                disabled
                style={{
                  width: 64,
                  color: "#d1d5db",
                  background:
                    "#1f2937",
                }}
              >
                VNĐ
              </Button>
            </Space.Compact>
          </Form.Item>


          <Form.Item
            name="location"
            label={
              <Text
                style={{
                  color: "#d1d5db",
                }}
              >
                Địa điểm
              </Text>
            }
            rules={[
              {
                max: 255,
                message:
                  "Địa điểm không được vượt quá 255 ký tự.",
              },
            ]}
          >
            <Input
              placeholder="Ví dụ: Hà Nội"
            />
          </Form.Item>


          <Form.Item
            name="skills"
            label={
              <Text
                style={{
                  color: "#d1d5db",
                }}
              >
                Kỹ năng core
              </Text>
            }
          >
            <Select
              mode="tags"
              allowClear
              placeholder="Chọn hoặc tự nhập kỹ năng"
              maxTagCount="responsive"
              options={AVAILABLE_SKILLS.map(
                (skill) => ({
                  label: skill,
                  value: skill,
                })
              )}
              optionFilterProp="label"
              classNames={{
                popup: {
                  root:
                    "expert-dark-select",
                },
              }}
            />
          </Form.Item>
        </Form>
      </Modal>


      {/* ===================================================
          DETAIL MODAL
      =================================================== */}

      <Modal
        title="Chi tiết chuyên gia"
        open={detailModalOpen}
        onCancel={closeDetailModal}
        footer={[
          <Button
            key="close"
            onClick={closeDetailModal}
          >
            Đóng
          </Button>,
        ]}
        destroyOnHidden
        width={720}
        styles={{
          content: {
            background: "#111827",
            border:
              "1px solid #1f2937",
          },
          header: {
            background: "#111827",
          },
          body: {
            background: "#111827",
          },
        }}
      >
        {selectedExpert && (
          <Descriptions
            bordered
            column={1}
            size="middle"
            className="expert-descriptions"
          >
            <Descriptions.Item label="Mã chuyên gia">
              {selectedExpert.id || "N/A"}
            </Descriptions.Item>

            <Descriptions.Item label="Họ và tên">
              {selectedExpert.full_name ||
                "Chưa cập nhật"}
            </Descriptions.Item>

            <Descriptions.Item label="Chức danh">
              {selectedExpert.title ||
                "Chưa cập nhật"}
            </Descriptions.Item>

            <Descriptions.Item label="Giới thiệu">
              {selectedExpert.bio ||
                "Chưa cập nhật"}
            </Descriptions.Item>

            <Descriptions.Item label="Mức phí theo giờ">
              <Text
                strong
                style={{
                  color: "#10b981",
                }}
              >
                {formatCurrency(
                  selectedExpert.hourly_rate
                )}
              </Text>
            </Descriptions.Item>

            <Descriptions.Item label="Địa điểm">
              {selectedExpert.location ||
                "Chưa cập nhật"}
            </Descriptions.Item>

            <Descriptions.Item label="Kỹ năng">
              <Flex
                wrap="wrap"
                gap={4}
              >
                {normalizeSkillsForForm(
                  selectedExpert.skills
                ).length > 0 ? (
                  normalizeSkillsForForm(
                    selectedExpert.skills
                  ).map((skill) => (
                    <Tag
                      key={skill}
                      color="blue"
                    >
                      {skill}
                    </Tag>
                  ))
                ) : (
                  <Tag color="default">
                    Chưa có
                  </Tag>
                )}
              </Flex>
            </Descriptions.Item>

            <Descriptions.Item label="Ngày tạo">
              {formatDateTime(
                selectedExpert.created_at
              )}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>


      {/* ===================================================
          DARK MODE CSS
      =================================================== */}

      <style>{`
        .expert-dark-table .ant-table {
          background: #111827 !important;
          color: #f3f4f6 !important;
        }

        .expert-dark-table .ant-table-container {
          background: #111827 !important;
          border-color: #1f2937 !important;
        }

        .expert-dark-table .ant-table-thead > tr > th {
          background: #1f2937 !important;
          color: #f3f4f6 !important;
          border-bottom: 1px solid #374151 !important;
        }

        .expert-dark-table .ant-table-tbody > tr > td {
          background: #111827 !important;
          color: #f3f4f6 !important;
          border-bottom: 1px solid #1f2937 !important;
        }

        .expert-dark-table .ant-table-tbody > tr:hover > td {
          background: #1f2937 !important;
        }

        .expert-dark-table .ant-pagination-item {
          background: #111827 !important;
          border-color: #374151 !important;
        }

        .expert-dark-table .ant-pagination-item a,
        .expert-dark-table .ant-pagination-prev button,
        .expert-dark-table .ant-pagination-next button {
          color: #d1d5db !important;
        }

        .expert-dark-table .ant-pagination-item-active {
          background: #4f46e5 !important;
          border-color: #4f46e5 !important;
        }

        .expert-dark-table .ant-pagination-item-active a {
          color: #ffffff !important;
        }

        .expert-dark-select {
          background: #1f2937 !important;
        }

        .expert-dark-select .ant-select-item {
          color: #e5e7eb !important;
        }

        .expert-dark-select .ant-select-item-option-active,
        .expert-dark-select .ant-select-item-option-selected {
          background: #374151 !important;
        }

        .expert-descriptions .ant-descriptions-view {
          border-color: #374151 !important;
        }

        .expert-descriptions .ant-descriptions-item-label {
          background: #1f2937 !important;
          color: #9ca3af !important;
          border-color: #374151 !important;
        }

        .expert-descriptions .ant-descriptions-item-content {
          background: #111827 !important;
          color: #f3f4f6 !important;
          border-color: #374151 !important;
        }

        .ant-modal-title {
          color: #f3f4f6 !important;
        }

        .ant-form-item-explain-error {
          color: #f87171 !important;
        }
      `}</style>
    </div>
  );
};

export default ExpertList;