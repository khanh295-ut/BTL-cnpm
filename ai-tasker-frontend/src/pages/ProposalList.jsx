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
  DeleteOutlined,
  EditOutlined,
  EyeOutlined,
  FileAddOutlined,
  FileTextOutlined,
  PlusOutlined,
  ReloadOutlined,
} from "@ant-design/icons";

import proposalApi from "../api/proposalApi";
import projectApi from "../api/projectApi";
import expertApi from "../api/expertApi";

const { Title, Text } = Typography;
const { TextArea } = Input;


/* ==========================================================
   CONSTANTS
========================================================== */

const PROPOSAL_STATUS_OPTIONS = [
  {
    value: "PENDING",
    label: "Chờ duyệt",
  },
  {
    value: "ACCEPTED",
    label: "Đã chấp nhận",
  },
  {
    value: "REJECTED",
    label: "Đã từ chối",
  },
  {
    value: "CANCELLED",
    label: "Đã hủy",
  },
];


/* ==========================================================
   HELPERS
========================================================== */

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
  if (!value) {
    return "Chưa cập nhật";
  }

  const parsed = new Date(value);

  if (Number.isNaN(parsed.getTime())) {
    return String(value);
  }

  return parsed.toLocaleString("vi-VN");
};


const getStatusConfig = (value) => {
  const status = String(
    value || "PENDING"
  ).toUpperCase();

  const mapping = {
    PENDING: {
      color: "gold",
      label: "Chờ duyệt",
    },
    ACCEPTED: {
      color: "green",
      label: "Đã chấp nhận",
    },
    APPROVED: {
      color: "green",
      label: "Đã phê duyệt",
    },
    REJECTED: {
      color: "red",
      label: "Đã từ chối",
    },
    CANCELLED: {
      color: "default",
      label: "Đã hủy",
    },
    WITHDRAWN: {
      color: "default",
      label: "Đã rút",
    },
  };

  return (
    mapping[status] || {
      color: "blue",
      label: status,
    }
  );
};


const getErrorMessage = (
  error,
  fallback = "Đã xảy ra lỗi."
) => {
  const detail =
    error?.response?.data?.detail;

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
        const field = Array.isArray(
          item?.loc
        )
          ? item.loc
              .filter(
                (part) => part !== "body"
              )
              .join(".")
          : "Dữ liệu";

        return `${field}: ${
          item?.msg ||
          "Không hợp lệ"
        }`;
      })
      .join("; ");
  }

  return fallback;
};


/* ==========================================================
   MAIN COMPONENT
========================================================== */

const ProposalList = () => {
  const { message } = App.useApp();

  const [form] = Form.useForm();
  const [statusForm] = Form.useForm();

  const [loading, setLoading] =
    useState(true);

  const [
    referenceLoading,
    setReferenceLoading,
  ] = useState(false);

  const [
    submitting,
    setSubmitting,
  ] = useState(false);

  const [
    statusSubmitting,
    setStatusSubmitting,
  ] = useState(false);

  const [
    deletingId,
    setDeletingId,
  ] = useState(null);

  const [proposals, setProposals] =
    useState([]);

  const [projects, setProjects] =
    useState([]);

  const [experts, setExperts] =
    useState([]);

  const [
    createModalOpen,
    setCreateModalOpen,
  ] = useState(false);

  const [
    detailModalOpen,
    setDetailModalOpen,
  ] = useState(false);

  const [
    statusModalOpen,
    setStatusModalOpen,
  ] = useState(false);

  const [
    selectedProposal,
    setSelectedProposal,
  ] = useState(null);


  /* ========================================================
     LOAD PROPOSALS
  ======================================================== */

  const loadProposals =
    useCallback(async () => {
      try {
        setLoading(true);

        const response =
          await proposalApi.getAll();

        setProposals(
          extractArray(response)
        );
      } catch (error) {
        console.error(
          "Không thể tải danh sách đề xuất:",
          error
        );

        message.error(
          getErrorMessage(
            error,
            "Không thể tải danh sách đề xuất."
          )
        );
      } finally {
        setLoading(false);
      }
    }, [message]);


  /* ========================================================
     LOAD PROJECTS AND EXPERTS
  ======================================================== */

  const loadReferenceData =
    useCallback(async () => {
      try {
        setReferenceLoading(true);

        const [
          projectResult,
          expertResult,
        ] = await Promise.allSettled([
          projectApi.getAll(),
          expertApi.getAll(),
        ]);

        if (
          projectResult.status ===
          "fulfilled"
        ) {
          setProjects(
            extractArray(
              projectResult.value
            )
          );
        } else {
          console.error(
            "Không thể tải dự án:",
            projectResult.reason
          );

          setProjects([]);
        }

        if (
          expertResult.status ===
          "fulfilled"
        ) {
          setExperts(
            extractArray(
              expertResult.value
            )
          );
        } else {
          console.error(
            "Không thể tải chuyên gia:",
            expertResult.reason
          );

          setExperts([]);
        }

        if (
          projectResult.status ===
            "rejected" ||
          expertResult.status ===
            "rejected"
        ) {
          message.warning(
            "Một phần dữ liệu dự án hoặc chuyên gia chưa tải được."
          );
        }
      } catch (error) {
        console.error(
          "Không thể tải dữ liệu tham chiếu:",
          error
        );

        message.error(
          "Không thể tải danh sách dự án và chuyên gia."
        );
      } finally {
        setReferenceLoading(false);
      }
    }, [message]);


  useEffect(() => {
    loadProposals();
    loadReferenceData();
  }, [
    loadProposals,
    loadReferenceData,
  ]);


  /* ========================================================
     LOOKUP MAPS
  ======================================================== */

  const projectMap = useMemo(() => {
    const map = new Map();

    projects.forEach((project) => {
      map.set(
        String(project.id),
        project.title ||
          project.name ||
          String(project.id)
      );
    });

    return map;
  }, [projects]);


  const expertMap = useMemo(() => {
    const map = new Map();

    experts.forEach((expert) => {
      map.set(
        String(expert.id),
        expert.full_name ||
          expert.name ||
          expert.email ||
          String(expert.id)
      );
    });

    return map;
  }, [experts]);


  const projectOptions = useMemo(
    () =>
      projects.map((project) => ({
        value: project.id,
        label:
          project.title ||
          project.name ||
          String(project.id),
      })),
    [projects]
  );


  const expertOptions = useMemo(
    () =>
      experts.map((expert) => ({
        value: expert.id,
        label:
          expert.full_name ||
          expert.name ||
          expert.email ||
          String(expert.id),
      })),
    [experts]
  );


  /* ========================================================
     CREATE MODAL
  ======================================================== */

  const openCreateModal = async () => {
    setCreateModalOpen(true);

    if (
      projects.length === 0 ||
      experts.length === 0
    ) {
      await loadReferenceData();
    }
  };


  const closeCreateModal = () => {
    setCreateModalOpen(false);
    form.resetFields();
  };


  /* ========================================================
     CREATE PROPOSAL
  ======================================================== */

  const handleCreateProposal = async (
    values
  ) => {
    try {
      setSubmitting(true);

      const payload = {
        project_id: values.project_id,
        expert_id: values.expert_id,
        bid_amount: Number(
          values.bid_amount
        ),
        cover_letter:
          values.cover_letter?.trim() ||
          null,
        estimated_days: Number(
          values.estimated_days
        ),
      };

      console.log(
        "Payload tạo proposal:",
        payload
      );

      await proposalApi.create(payload);

      message.success(
        "Tạo đề xuất thành công."
      );

      closeCreateModal();
      await loadProposals();
    } catch (error) {
      console.error(
        "Không thể tạo đề xuất:",
        error?.response?.data || error
      );

      message.error(
        getErrorMessage(
          error,
          "Không thể tạo đề xuất. Vui lòng kiểm tra dữ liệu."
        )
      );
    } finally {
      setSubmitting(false);
    }
  };


  /* ========================================================
     VIEW DETAIL
  ======================================================== */

  const openDetailModal = (
    proposal
  ) => {
    setSelectedProposal(proposal);
    setDetailModalOpen(true);
  };


  const closeDetailModal = () => {
    setDetailModalOpen(false);
    setSelectedProposal(null);
  };


  /* ========================================================
     UPDATE STATUS
  ======================================================== */

  const openStatusModal = (
    proposal
  ) => {
    setSelectedProposal(proposal);

    statusForm.setFieldsValue({
      status:
        proposal.status ||
        "PENDING",
    });

    setStatusModalOpen(true);
  };


  const closeStatusModal = () => {
    setStatusModalOpen(false);
    setSelectedProposal(null);
    statusForm.resetFields();
  };


  const handleUpdateStatus = async (
    values
  ) => {
    if (!selectedProposal?.id) {
      return;
    }

    try {
      setStatusSubmitting(true);

      await proposalApi.updateStatus(
        selectedProposal.id,
        values.status
      );

      message.success(
        "Cập nhật trạng thái thành công."
      );

      closeStatusModal();
      await loadProposals();
    } catch (error) {
      console.error(
        "Không thể cập nhật trạng thái:",
        error
      );

      message.error(
        getErrorMessage(
          error,
          "Không thể cập nhật trạng thái."
        )
      );
    } finally {
      setStatusSubmitting(false);
    }
  };


  /* ========================================================
     DELETE PROPOSAL
  ======================================================== */

  const handleDelete = async (
    proposalId
  ) => {
    try {
      setDeletingId(proposalId);

      await proposalApi.delete(
        proposalId
      );

      message.success(
        "Xóa đề xuất thành công."
      );

      await loadProposals();
    } catch (error) {
      console.error(
        "Không thể xóa đề xuất:",
        error
      );

      message.error(
        getErrorMessage(
          error,
          "Không thể xóa đề xuất."
        )
      );
    } finally {
      setDeletingId(null);
    }
  };


  /* ========================================================
     TABLE COLUMNS
  ======================================================== */

  const columns = [
    {
      title: "Mã đề xuất",
      dataIndex: "id",
      key: "id",
      width: 190,
      render: (value) => {
        const id = String(
          value || ""
        );

        return (
          <Text
            code
            style={{
              color: "#d1d5db",
              fontSize: 12,
              wordBreak: "break-all",
            }}
          >
            {id || "N/A"}
          </Text>
        );
      },
    },
    {
      title: "Dự án",
      dataIndex: "project_id",
      key: "project_id",
      width: 190,
      render: (
        projectId,
        record
      ) => {
        const projectName =
          record.project?.title ||
          record.project_title ||
          projectMap.get(
            String(projectId)
          ) ||
          "Chưa cập nhật";

        return (
          <Text
            strong
            style={{
              color: "#f3f4f6",
            }}
          >
            {projectName}
          </Text>
        );
      },
    },
    {
      title: "Chuyên gia",
      dataIndex: "expert_id",
      key: "expert_id",
      width: 170,
      render: (
        expertId,
        record
      ) => {
        const expertName =
          record.expert?.full_name ||
          record.expert?.name ||
          record.expert_name ||
          expertMap.get(
            String(expertId)
          ) ||
          "Chưa cập nhật";

        return (
          <Text
            style={{
              color: "#e5e7eb",
            }}
          >
            {expertName}
          </Text>
        );
      },
    },
    {
      title: "Giá chào thầu",
      key: "bid_amount",
      width: 150,
      align: "right",
      render: (_, record) => {
        const amount =
          record.bid_amount ??
          record.price ??
          record.amount ??
          0;

        return (
          <Text
            strong
            style={{
              color: "#10b981",
            }}
          >
            {formatCurrency(amount)}
          </Text>
        );
      },
    },
    {
      title: "Số ngày",
      key: "estimated_days",
      width: 100,
      align: "center",
      render: (_, record) => (
        <Text
          style={{
            color: "#d1d5db",
          }}
        >
          {record.estimated_days ??
            record.duration_days ??
            "-"}
        </Text>
      ),
    },
    {
      title: "Trạng thái",
      dataIndex: "status",
      key: "status",
      width: 125,
      align: "center",
      render: (status) => {
        const config =
          getStatusConfig(status);

        return (
          <Tag color={config.color}>
            {config.label}
          </Tag>
        );
      },
    },
    {
      title: "Hành động",
      key: "actions",
      width: 210,
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
            title="Đổi trạng thái"
            icon={
              <EditOutlined
                style={{
                  color: "#f59e0b",
                }}
              />
            }
            onClick={() =>
              openStatusModal(record)
            }
          />

          <Popconfirm
            title="Xóa đề xuất"
            description="Bạn có chắc chắn muốn xóa đề xuất này?"
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
              loading={
                deletingId ===
                record.id
              }
              title="Xóa đề xuất"
              icon={<DeleteOutlined />}
            />
          </Popconfirm>
        </Space>
      ),
    },
  ];


  /* ========================================================
     UI
  ======================================================== */

  return (
    <div
      style={{
        padding: 32,
        minHeight: "100vh",
        background: "#090d16",
      }}
    >
      <Card
        variant="none"
        style={{
          maxWidth: 1180,
          margin: "0 auto",
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
            <FileTextOutlined
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
                Danh sách Đề xuất
              </Title>

              <Text
                style={{
                  color: "#9ca3af",
                }}
              >
                Quản lý đề xuất và báo
                giá của các chuyên gia
              </Text>
            </div>
          </Space>

          <Space wrap>
            <Button
              icon={
                <ReloadOutlined />
              }
              onClick={() => {
                loadProposals();
                loadReferenceData();
              }}
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
              Thêm đề xuất
            </Button>
          </Space>
        </Flex>


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
              Đang tải danh sách đề
              xuất...
            </Text>
          </Flex>
        ) : (
          <Table
            rowKey="id"
            columns={columns}
            dataSource={proposals}
            className="proposal-dark-table"
            scroll={{
              x: 1150,
            }}
            pagination={{
              pageSize: 6,
              showSizeChanger: false,
              showTotal: (total) =>
                `Tổng ${total} đề xuất`,
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
                      Chưa có đề xuất
                      nào.
                    </span>
                  }
                >
                  <Button
                    type="primary"
                    icon={
                      <FileAddOutlined />
                    }
                    onClick={
                      openCreateModal
                    }
                  >
                    Tạo đề xuất đầu tiên
                  </Button>
                </Empty>
              ),
            }}
          />
        )}
      </Card>


      {/* ====================================================
          CREATE MODAL
      ==================================================== */}

      <Modal
        title={
          <Space>
            <FileAddOutlined />
            <span>
              Tạo đề xuất mới
            </span>
          </Space>
        }
        open={createModalOpen}
        onCancel={closeCreateModal}
        onOk={() => form.submit()}
        confirmLoading={submitting}
        okText="Tạo đề xuất"
        cancelText="Hủy"
        destroyOnHidden
        width={660}
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
        <Spin
          spinning={referenceLoading}
          description="Đang tải dữ liệu dự án và chuyên gia..."
        >
          <Form
            form={form}
            layout="vertical"
            onFinish={
              handleCreateProposal
            }
            requiredMark="optional"
            style={{
              marginTop: 20,
            }}
          >
            <Form.Item
              name="project_id"
              label={
                <Text
                  style={{
                    color: "#d1d5db",
                  }}
                >
                  Dự án
                </Text>
              }
              rules={[
                {
                  required: true,
                  message:
                    "Vui lòng chọn dự án.",
                },
              ]}
            >
              <Select
                showSearch
                allowClear
                optionFilterProp="label"
                placeholder="Chọn dự án"
                options={projectOptions}
                notFoundContent="Không có dự án"
                classNames={{
                  popup: {
                    root:
                      "proposal-dark-select",
                  },
                }}
              />
            </Form.Item>


            <Form.Item
              name="expert_id"
              label={
                <Text
                  style={{
                    color: "#d1d5db",
                  }}
                >
                  Chuyên gia
                </Text>
              }
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
                options={expertOptions}
                notFoundContent="Không có chuyên gia"
                classNames={{
                  popup: {
                    root:
                      "proposal-dark-select",
                  },
                }}
              />
            </Form.Item>


            <Form.Item
              name="bid_amount"
              label={
                <Text
                  style={{
                    color: "#d1d5db",
                  }}
                >
                  Giá chào thầu
                </Text>
              }
              rules={[
                {
                  required: true,
                  message:
                    "Vui lòng nhập giá chào thầu.",
                },
                {
                  validator: (
                    _,
                    value
                  ) => {
                    if (
                      value === undefined ||
                      value === null
                    ) {
                      return Promise.resolve();
                    }

                    if (Number(value) <= 0) {
                      return Promise.reject(
                        new Error(
                          "Giá chào thầu phải lớn hơn 0."
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
                  min={1}
                  precision={0}
                  placeholder="Nhập số tiền"
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
                        /[^\d]/g,
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
              name="estimated_days"
              label={
                <Text
                  style={{
                    color: "#d1d5db",
                  }}
                >
                  Số ngày dự kiến
                </Text>
              }
              rules={[
                {
                  required: true,
                  message:
                    "Vui lòng nhập số ngày dự kiến.",
                },
                {
                  validator: (
                    _,
                    value
                  ) => {
                    if (
                      value === undefined ||
                      value === null
                    ) {
                      return Promise.resolve();
                    }

                    if (Number(value) < 1) {
                      return Promise.reject(
                        new Error(
                          "Số ngày dự kiến phải lớn hơn 0."
                        )
                      );
                    }

                    return Promise.resolve();
                  },
                },
              ]}
            >
              <InputNumber
                min={1}
                precision={0}
                placeholder="Ví dụ: 30"
                style={{
                  width: "100%",
                }}
              />
            </Form.Item>


            <Form.Item
              name="cover_letter"
              label={
                <Text
                  style={{
                    color: "#d1d5db",
                  }}
                >
                  Nội dung đề xuất
                </Text>
              }
              rules={[
                {
                  required: true,
                  message:
                    "Vui lòng nhập nội dung đề xuất.",
                },
                {
                  max: 3000,
                  message:
                    "Nội dung không được vượt quá 3000 ký tự.",
                },
              ]}
            >
              <TextArea
                rows={5}
                showCount
                maxLength={3000}
                placeholder="Mô tả phương án thực hiện, kinh nghiệm và cam kết..."
              />
            </Form.Item>
          </Form>
        </Spin>
      </Modal>


      {/* ====================================================
          DETAIL MODAL
      ==================================================== */}

      <Modal
        title="Chi tiết đề xuất"
        open={detailModalOpen}
        onCancel={closeDetailModal}
        footer={[
          <Button
            key="close"
            onClick={
              closeDetailModal
            }
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
        {selectedProposal && (
          <Descriptions
            bordered
            column={1}
            size="middle"
            className="proposal-descriptions"
          >
            <Descriptions.Item label="Mã đề xuất">
              {selectedProposal.id ||
                "N/A"}
            </Descriptions.Item>

            <Descriptions.Item label="Dự án">
              {selectedProposal.project
                ?.title ||
                selectedProposal.project_title ||
                projectMap.get(
                  String(
                    selectedProposal.project_id
                  )
                ) ||
                "Chưa cập nhật"}
            </Descriptions.Item>

            <Descriptions.Item label="Chuyên gia">
              {selectedProposal.expert
                ?.full_name ||
                selectedProposal.expert
                  ?.name ||
                selectedProposal.expert_name ||
                expertMap.get(
                  String(
                    selectedProposal.expert_id
                  )
                ) ||
                "Chưa cập nhật"}
            </Descriptions.Item>

            <Descriptions.Item label="Giá chào thầu">
              <Text
                strong
                style={{
                  color: "#10b981",
                }}
              >
                {formatCurrency(
                  selectedProposal.bid_amount ??
                    selectedProposal.price ??
                    selectedProposal.amount
                )}
              </Text>
            </Descriptions.Item>

            <Descriptions.Item label="Số ngày dự kiến">
              {selectedProposal.estimated_days ??
                selectedProposal.duration_days ??
                "Chưa cập nhật"}
            </Descriptions.Item>

            <Descriptions.Item label="Trạng thái">
              {(() => {
                const config =
                  getStatusConfig(
                    selectedProposal.status
                  );

                return (
                  <Tag
                    color={config.color}
                  >
                    {config.label}
                  </Tag>
                );
              })()}
            </Descriptions.Item>

            <Descriptions.Item label="Ngày tạo">
              {formatDateTime(
                selectedProposal.created_at
              )}
            </Descriptions.Item>

            <Descriptions.Item label="Nội dung đề xuất">
              {selectedProposal.cover_letter ||
                selectedProposal.description ||
                "Chưa cập nhật"}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>


      {/* ====================================================
          STATUS MODAL
      ==================================================== */}

      <Modal
        title="Cập nhật trạng thái đề xuất"
        open={statusModalOpen}
        onCancel={closeStatusModal}
        onOk={() =>
          statusForm.submit()
        }
        confirmLoading={
          statusSubmitting
        }
        okText="Cập nhật"
        cancelText="Hủy"
        destroyOnHidden
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
          form={statusForm}
          layout="vertical"
          onFinish={
            handleUpdateStatus
          }
          style={{
            marginTop: 20,
          }}
        >
          <Form.Item
            name="status"
            label={
              <Text
                style={{
                  color: "#d1d5db",
                }}
              >
                Trạng thái mới
              </Text>
            }
            rules={[
              {
                required: true,
                message:
                  "Vui lòng chọn trạng thái.",
              },
            ]}
          >
            <Select
              options={
                PROPOSAL_STATUS_OPTIONS
              }
              classNames={{
                popup: {
                  root:
                    "proposal-dark-select",
                },
              }}
            />
          </Form.Item>
        </Form>
      </Modal>


      {/* ====================================================
          DARK MODE CSS
      ==================================================== */}

      <style>{`
        .proposal-dark-table .ant-table {
          background: #111827 !important;
          color: #f3f4f6 !important;
        }

        .proposal-dark-table .ant-table-container {
          background: #111827 !important;
          border-color: #1f2937 !important;
        }

        .proposal-dark-table .ant-table-thead > tr > th {
          background: #1f2937 !important;
          color: #f3f4f6 !important;
          border-bottom: 1px solid #374151 !important;
        }

        .proposal-dark-table .ant-table-tbody > tr > td {
          background: #111827 !important;
          color: #f3f4f6 !important;
          border-bottom: 1px solid #1f2937 !important;
        }

        .proposal-dark-table .ant-table-tbody > tr:hover > td {
          background: #1f2937 !important;
        }

        .proposal-dark-table .ant-pagination-item {
          background: #111827 !important;
          border-color: #374151 !important;
        }

        .proposal-dark-table .ant-pagination-item a,
        .proposal-dark-table .ant-pagination-prev button,
        .proposal-dark-table .ant-pagination-next button {
          color: #d1d5db !important;
        }

        .proposal-dark-table .ant-pagination-item-active {
          background: #4f46e5 !important;
          border-color: #4f46e5 !important;
        }

        .proposal-dark-table .ant-pagination-item-active a {
          color: #ffffff !important;
        }

        .proposal-dark-select {
          background: #1f2937 !important;
        }

        .proposal-dark-select .ant-select-item {
          color: #e5e7eb !important;
        }

        .proposal-dark-select .ant-select-item-option-active,
        .proposal-dark-select .ant-select-item-option-selected {
          background: #374151 !important;
        }

        .proposal-descriptions .ant-descriptions-view {
          border-color: #374151 !important;
        }

        .proposal-descriptions .ant-descriptions-item-label {
          background: #1f2937 !important;
          color: #9ca3af !important;
          border-color: #374151 !important;
        }

        .proposal-descriptions .ant-descriptions-item-content {
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

export default ProposalList;