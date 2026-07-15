import React, {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  App as AntdApp,
  Button,
  Card,
  Col,
  Empty,
  Flex,
  Row,
  Spin,
  Statistic,
  Table,
  Tag,
  Typography,
} from "antd";

import {
  CheckCircleOutlined,
  DollarCircleOutlined,
  FileProtectOutlined,
  LockOutlined,
  ReloadOutlined,
} from "@ant-design/icons";

import axiosClient from "../api/axiosClient";

const { Title, Text } = Typography;


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
    return "0 ₫";
  }

  return amount.toLocaleString("vi-VN", {
    style: "currency",
    currency: "VND",
    maximumFractionDigits: 0,
  });
};


const formatDate = (value) => {
  if (!value) return "-";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "-";
  }

  return date.toLocaleDateString("vi-VN");
};


const getErrorMessage = (error) => {
  const detail = error?.response?.data?.detail;

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => item?.msg || "Dữ liệu không hợp lệ")
      .join("; ");
  }

  if (error?.code === "ERR_NETWORK") {
    return "Không thể kết nối tới Backend FastAPI.";
  }

  return "Không thể tải dữ liệu hợp đồng.";
};


/* =========================================================
   CONTENT COMPONENT
========================================================= */

const ContractsEscrowContent = () => {
  const { message } = AntdApp.useApp();

  const [contracts, setContracts] = useState([]);
  const [projects, setProjects] = useState([]);
  const [experts, setExperts] = useState([]);
  const [enterprises, setEnterprises] = useState([]);

  const [loading, setLoading] = useState(true);


  /* =======================================================
     LOAD DATA
  ======================================================= */

  const loadContracts = useCallback(async () => {
    try {
      setLoading(true);

      const [
        contractsResult,
        projectsResult,
        expertsResult,
        enterprisesResult,
      ] = await Promise.allSettled([
        axiosClient.get("/contracts"),
        axiosClient.get("/projects"),
        axiosClient.get("/experts"),
        axiosClient.get("/enterprises"),
      ]);

      if (contractsResult.status === "rejected") {
        throw contractsResult.reason;
      }

      const contractList = extractArray(
        contractsResult.value
      );

      setContracts(contractList);

      setProjects(
        projectsResult.status === "fulfilled"
          ? extractArray(projectsResult.value)
          : []
      );

      setExperts(
        expertsResult.status === "fulfilled"
          ? extractArray(expertsResult.value)
          : []
      );

      setEnterprises(
        enterprisesResult.status === "fulfilled"
          ? extractArray(enterprisesResult.value)
          : []
      );

      if (
        projectsResult.status === "rejected" ||
        expertsResult.status === "rejected" ||
        enterprisesResult.status === "rejected"
      ) {
        message.warning(
          "Đã tải hợp đồng nhưng một số thông tin liên kết chưa tải được."
        );
      }
    } catch (error) {
      console.error(
        "[Contracts API Error]:",
        error?.response?.data || error
      );

      setContracts([]);
      setProjects([]);
      setExperts([]);
      setEnterprises([]);

      message.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }, [message]);


  useEffect(() => {
    loadContracts();
  }, [loadContracts]);


  /* =======================================================
     LOOKUP MAPS
  ======================================================= */

  const projectMap = useMemo(() => {
    const map = new Map();

    projects.forEach((project) => {
      map.set(String(project.id), project);
    });

    return map;
  }, [projects]);


  const expertMap = useMemo(() => {
    const map = new Map();

    experts.forEach((expert) => {
      map.set(String(expert.id), expert);
    });

    return map;
  }, [experts]);


  const enterpriseMap = useMemo(() => {
    const map = new Map();

    enterprises.forEach((enterprise) => {
      map.set(String(enterprise.id), enterprise);
    });

    return map;
  }, [enterprises]);


  /* =======================================================
     SUMMARY
  ======================================================= */

  const summary = useMemo(() => {
    return contracts.reduce(
      (result, contract) => {
        const amount = Number(
          contract.total_amount ??
          contract.escrow_amount ??
          contract.amount ??
          0
        );

        const status = String(
          contract.status || ""
        ).toUpperCase();

        result.totalFunds += amount;

        if (
          status === "RELEASED" ||
          status === "COMPLETED"
        ) {
          result.releasedFunds += amount;
        } else if (
          status === "PENDING" ||
          status === "ACTIVE" ||
          status === "IN_PROGRESS" ||
          status === "HELD" ||
          status === "LOCKED" ||
          status === "HOLDING"
        ) {
          result.lockedFunds += amount;
        }

        return result;
      },
      {
        totalFunds: 0,
        lockedFunds: 0,
        releasedFunds: 0,
      }
    );
  }, [contracts]);


  /* =======================================================
     TABLE COLUMNS
  ======================================================= */

  const columns = [
    {
      title: "Mã hợp đồng",
      dataIndex: "id",
      key: "id",
      width: 145,
      render: (id) => {
        if (!id) {
          return (
            <Text type="secondary">
              N/A
            </Text>
          );
        }

        const text = String(id);

        return (
          <Text
            strong
            style={{
              color: "#818cf8",
              fontFamily: "monospace",
            }}
            title={text}
          >
            #
            {text.length > 8
              ? `${text.slice(0, 8)}...`
              : text}
          </Text>
        );
      },
    },
    {
      title: "Tên dự án / Hợp đồng",
      key: "title",
      width: 210,
      ellipsis: true,
      render: (_, record) => {
        const project = projectMap.get(
          String(record.project_id)
        );

        return (
          <Text
            strong
            style={{ color: "#f3f4f6" }}
          >
            {record.title ||
              project?.title ||
              "Chưa cập nhật"}
          </Text>
        );
      },
    },
    {
      title: "Bên thuê",
      key: "client",
      width: 175,
      render: (_, record) => {
        const project = projectMap.get(
          String(record.project_id)
        );

        const enterprise = enterpriseMap.get(
          String(project?.enterprise_id)
        );

        return (
          <Text style={{ color: "#d1d5db" }}>
            {record.client_name ||
              enterprise?.name ||
              enterprise?.company_name ||
              "Chưa cập nhật"}
          </Text>
        );
      },
    },
    {
      title: "Chuyên gia AI",
      key: "expert",
      width: 175,
      render: (_, record) => {
        const expert = expertMap.get(
          String(record.expert_id)
        );

        return (
          <Text style={{ color: "#d1d5db" }}>
            {record.expert_name ||
              expert?.full_name ||
              expert?.name ||
              expert?.email ||
              "Chưa cập nhật"}
          </Text>
        );
      },
    },
    {
      title: "Giá trị hợp đồng",
      key: "total_amount",
      width: 165,
      align: "right",
      sorter: (a, b) =>
        Number(
          a.total_amount ??
          a.escrow_amount ??
          a.amount ??
          0
        ) -
        Number(
          b.total_amount ??
          b.escrow_amount ??
          b.amount ??
          0
        ),
      render: (_, record) => (
        <Text
          strong
          style={{ color: "#10b981" }}
        >
          {formatCurrency(
            record.total_amount ??
            record.escrow_amount ??
            record.amount
          )}
        </Text>
      ),
    },
    {
      title: "Trạng thái Escrow",
      dataIndex: "status",
      key: "status",
      width: 155,
      align: "center",
      render: (value) => {
        const status = String(
          value || "PENDING"
        ).toUpperCase();

        if (
          status === "RELEASED" ||
          status === "COMPLETED"
        ) {
          return (
            <Tag color="green">
              Đã giải ngân
            </Tag>
          );
        }

        if (
          status === "ACTIVE" ||
          status === "IN_PROGRESS" ||
          status === "HELD" ||
          status === "LOCKED" ||
          status === "HOLDING"
        ) {
          return (
            <Tag color="blue">
              Đang ký quỹ
            </Tag>
          );
        }

        if (status === "REFUNDED") {
          return (
            <Tag color="magenta">
              Đã hoàn tiền
            </Tag>
          );
        }

        if (status === "CANCELLED") {
          return (
            <Tag color="default">
              Đã hủy
            </Tag>
          );
        }

        return (
          <Tag color="gold">
            Chờ ký quỹ
          </Tag>
        );
      },
    },
    {
      title: "Cập nhật cuối",
      key: "updated_at",
      width: 125,
      render: (_, record) =>
        formatDate(
          record.updated_at ||
          record.created_at
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
      <Flex
        justify="space-between"
        align="center"
        wrap="wrap"
        gap="middle"
        style={{ marginBottom: 24 }}
      >
        <div>
          <Title
            level={2}
            style={{
              margin: 0,
              color: "#ffffff",
            }}
          >
            <FileProtectOutlined />
            {" "}
            Hợp đồng & Ký quỹ an toàn
          </Title>

          <Text style={{ color: "#9ca3af" }}>
            Theo dõi giá trị hợp đồng và trạng thái
            giải ngân giữa doanh nghiệp và chuyên gia AI
          </Text>
        </div>

        <Button
          type="primary"
          ghost
          icon={<ReloadOutlined />}
          onClick={loadContracts}
          loading={loading}
        >
          Làm mới
        </Button>
      </Flex>


      {/* SUMMARY */}

      <Row
        gutter={[16, 16]}
        style={{ marginBottom: 24 }}
      >
        <Col xs={24} sm={8}>
          <Card
            variant="none"
            style={{
              background: "#111827",
              border: "1px solid #1f2937",
              borderRadius: 12,
            }}
          >
            <Statistic
              title={
                <span style={{ color: "#9ca3af" }}>
                  Tổng giá trị hợp đồng
                </span>
              }
              value={summary.totalFunds}
              precision={0}
              suffix="₫"
              prefix={<DollarCircleOutlined />}
              styles={{
                content: {
                  color: "#f3f4f6",
                },
              }}
            />
          </Card>
        </Col>

        <Col xs={24} sm={8}>
          <Card
            variant="none"
            style={{
              background: "#111827",
              border: "1px solid #1f2937",
              borderRadius: 12,
            }}
          >
            <Statistic
              title={
                <span style={{ color: "#9ca3af" }}>
                  Tiền đang ký quỹ
                </span>
              }
              value={summary.lockedFunds}
              precision={0}
              suffix="₫"
              prefix={<LockOutlined />}
              styles={{
                content: {
                  color: "#3b82f6",
                },
              }}
            />
          </Card>
        </Col>

        <Col xs={24} sm={8}>
          <Card
            variant="none"
            style={{
              background: "#111827",
              border: "1px solid #1f2937",
              borderRadius: 12,
            }}
          >
            <Statistic
              title={
                <span style={{ color: "#9ca3af" }}>
                  Tiền đã giải ngân
                </span>
              }
              value={summary.releasedFunds}
              precision={0}
              suffix="₫"
              prefix={<CheckCircleOutlined />}
              styles={{
                content: {
                  color: "#10b981",
                },
              }}
            />
          </Card>
        </Col>
      </Row>


      {/* TABLE */}

      <Card
        variant="none"
        style={{
          background: "#111827",
          border: "1px solid #1f2937",
          borderRadius: 12,
        }}
      >
        {loading ? (
          <Flex
            vertical
            justify="center"
            align="center"
            style={{ minHeight: 300 }}
          >
            <Spin size="large" />

            <Text
              style={{
                marginTop: 16,
                color: "#9ca3af",
              }}
            >
              Đang tải dữ liệu hợp đồng...
            </Text>
          </Flex>
        ) : (
          <Table
            bordered
            rowKey="id"
            columns={columns}
            dataSource={contracts}
            className="contracts-dark-table"
            scroll={{ x: 1150 }}
            pagination={{
              pageSize: 6,
              showSizeChanger: false,
              showTotal: (total) =>
                `Tổng ${total} hợp đồng`,
            }}
            locale={{
              emptyText: (
                <Empty
                  image={Empty.PRESENTED_IMAGE_SIMPLE}
                  description={
                    <span style={{ color: "#9ca3af" }}>
                      Chưa có hợp đồng nào. Hãy chấp nhận
                      một đề xuất để hệ thống tạo hợp đồng.
                    </span>
                  }
                />
              ),
            }}
          />
        )}
      </Card>


      <style>{`
        .contracts-dark-table .ant-table {
          background: #111827 !important;
          color: #f3f4f6 !important;
        }

        .contracts-dark-table .ant-table-thead > tr > th {
          background: #1f2937 !important;
          color: #f3f4f6 !important;
          border-color: #374151 !important;
        }

        .contracts-dark-table .ant-table-tbody > tr > td {
          background: #111827 !important;
          color: #f3f4f6 !important;
          border-color: #1f2937 !important;
        }

        .contracts-dark-table .ant-table-tbody > tr:hover > td {
          background: #1f2937 !important;
        }

        .contracts-dark-table .ant-pagination-item {
          background: #111827 !important;
          border-color: #374151 !important;
        }

        .contracts-dark-table .ant-pagination-item a,
        .contracts-dark-table .ant-pagination-prev button,
        .contracts-dark-table .ant-pagination-next button {
          color: #d1d5db !important;
        }

        .contracts-dark-table .ant-pagination-item-active {
          background: #4f46e5 !important;
          border-color: #4f46e5 !important;
        }

        .contracts-dark-table .ant-pagination-item-active a {
          color: #ffffff !important;
        }
      `}</style>
    </div>
  );
};


/* =========================================================
   EXPORT COMPONENT
========================================================= */

const ContractsEscrow = () => (
  <AntdApp>
    <ContractsEscrowContent />
  </AntdApp>
);

export default ContractsEscrow;