import React, {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  App,
  Card,
  Col,
  Empty,
  Flex,
  Row,
  Spin,
  Statistic,
  Table,
  Tag,
  Timeline,
  Typography,
} from "antd";

import {
  ArrowDownOutlined,
  ArrowUpOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  DollarOutlined,
  UserOutlined,
} from "@ant-design/icons";

import axiosClient from "../api/axiosClient";

const { Title, Text } = Typography;


/* =========================================================
   HELPERS
========================================================= */

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


const formatDateTime = (value) => {
  if (!value) return "Chưa cập nhật";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return date.toLocaleString("vi-VN");
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

  return "Không thể tải dữ liệu Analytics.";
};


/* =========================================================
   CONTENT
========================================================= */

const AnalyticsContent = () => {
  const { message } = App.useApp();

  const [loading, setLoading] = useState(true);

  const [stats, setStats] = useState({
    totalRevenue: 0,
    totalContractValue: 0,
    activeExperts: 0,
    completedProjects: 0,
    pendingProjects: 0,
    totalProjects: 0,
    totalExperts: 0,
    totalProposals: 0,
    totalContracts: 0,
    totalPayments: 0,
    recentActivities: [],
    topSkills: [],
  });


  /* =======================================================
     LOAD DATA
  ======================================================= */

  const loadAnalyticsData = useCallback(async () => {
    try {
      setLoading(true);

      const response = await axiosClient.get(
        "/statistics/overview"
      );

      const data = response.data || {};
      const summary = data.summary || {};
      const revenue = data.revenue || {};
      const contractValue = data.contract_value || {};

      setStats({
        totalRevenue:
          Number(
            summary.total_revenue ??
            revenue.revenue ??
            0
          ),

        totalContractValue:
          Number(
            contractValue.total_contract_value ??
            0
          ),

        activeExperts:
          Number(summary.active_experts || 0),

        completedProjects:
          Number(summary.completed_projects || 0),

        pendingProjects:
          Number(summary.pending_projects || 0),

        totalProjects:
          Number(summary.total_projects || 0),

        totalExperts:
          Number(summary.total_experts || 0),

        totalProposals:
          Number(summary.total_proposals || 0),

        totalContracts:
          Number(summary.total_contracts || 0),

        totalPayments:
          Number(summary.total_payments || 0),

        recentActivities:
          Array.isArray(data.recent_activities)
            ? data.recent_activities
            : [],

        topSkills:
          Array.isArray(data.popular_skills)
            ? data.popular_skills
            : [],
      });
    } catch (error) {
      console.error(
        "Lỗi tải Analytics:",
        error?.response?.data || error
      );

      message.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }, [message]);


  useEffect(() => {
    loadAnalyticsData();
  }, [loadAnalyticsData]);


  /* =======================================================
     SKILL TABLE
  ======================================================= */

  const skillColumns = [
    {
      title: "Kỹ năng AI",
      key: "name",
      render: (_, record) => (
        <Text strong>
          {record.name ||
            record.skill ||
            "Chưa cập nhật"}
        </Text>
      ),
    },
    {
      title: "Số chuyên gia",
      key: "total",
      align: "center",
      sorter: (a, b) =>
        Number(a.total || a.usage || 0) -
        Number(b.total || b.usage || 0),
      render: (_, record) => {
        const total = Number(
          record.total ??
          record.usage ??
          0
        );

        return `${total} chuyên gia`;
      },
    },
    {
      title: "Xu hướng",
      key: "trend",
      align: "center",
      render: (_, record) => {
        const trend = String(
          record.trend || "STABLE"
        ).toUpperCase();

        if (trend === "UP") {
          return (
            <span style={{ color: "#16a34a" }}>
              <ArrowUpOutlined /> Tăng
            </span>
          );
        }

        if (trend === "DOWN") {
          return (
            <span style={{ color: "#dc2626" }}>
              <ArrowDownOutlined /> Giảm
            </span>
          );
        }

        return <Tag color="default">Ổn định</Tag>;
      },
    },
  ];


  /* =======================================================
     TIMELINE
  ======================================================= */

  const timelineItems = useMemo(
    () =>
      stats.recentActivities.map(
        (item, index) => ({
          color:
            index === 0
              ? "green"
              : "blue",

          label: formatDateTime(
            item.created_at ||
            item.time
          ),

          children: (
            <div>
              <Text strong>
                {item.title ||
                  item.text ||
                  "Hoạt động hệ thống"}
              </Text>

              {item.status && (
                <div style={{ marginTop: 4 }}>
                  <Tag color="blue">
                    {String(item.status)}
                  </Tag>
                </div>
              )}
            </div>
          ),
        })
      ),
    [stats.recentActivities]
  );


  /* =======================================================
     LOADING
  ======================================================= */

  if (loading) {
    return (
      <Flex
        vertical
        justify="center"
        align="center"
        style={{
          minHeight: "100vh",
          background: "#0f172a",
        }}
      >
        <Spin size="large" />

        <Text
          style={{
            color: "#9ca3af",
            marginTop: 16,
          }}
        >
          Đang tải dữ liệu Analytics...
        </Text>
      </Flex>
    );
  }


  /* =======================================================
     UI
  ======================================================= */

  return (
    <div
      style={{
        padding: 24,
        minHeight: "100vh",
        background: "#0f172a",
      }}
    >
      <div
        style={{
          maxWidth: 1300,
          margin: "0 auto",
        }}
      >
        {/* HEADER */}

        <div style={{ marginBottom: 24 }}>
          <Title
            level={2}
            style={{
              marginBottom: 4,
              color: "#ffffff",
            }}
          >
            Trung tâm Phân tích & Báo cáo
          </Title>

          <Text style={{ color: "#9ca3af" }}>
            Theo dõi doanh thu, giá trị hợp đồng,
            tiến độ dự án và hoạt động chuyên gia.
          </Text>
        </div>


        {/* MAIN STATISTICS */}

        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} lg={6}>
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
                    Tổng doanh thu
                  </span>
                }
                value={stats.totalRevenue}
                precision={0}
                prefix={<DollarOutlined />}
                formatter={(value) =>
                  formatCurrency(value)
                }
                styles={{
                  content: {
                    color: "#10b981",
                  },
                }}
              />
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
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
                    Chuyên gia hoạt động
                  </span>
                }
                value={stats.activeExperts}
                prefix={<UserOutlined />}
                styles={{
                  content: {
                    color: "#a855f7",
                  },
                }}
              />
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
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
                    Dự án hoàn thành
                  </span>
                }
                value={stats.completedProjects}
                prefix={<CheckCircleOutlined />}
                styles={{
                  content: {
                    color: "#3b82f6",
                  },
                }}
              />
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
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
                    Dự án đang xử lý
                  </span>
                }
                value={stats.pendingProjects}
                prefix={<ClockCircleOutlined />}
                styles={{
                  content: {
                    color: "#f59e0b",
                  },
                }}
              />
            </Card>
          </Col>
        </Row>


        {/* SECONDARY STATISTICS */}

        <Row
          gutter={[16, 16]}
          style={{ marginTop: 16 }}
        >
          <Col xs={24} sm={12} lg={6}>
            <Card
              variant="none"
              style={{
                background: "#111827",
                border: "1px solid #1f2937",
              }}
            >
              <Statistic
                title={
                  <span style={{ color: "#9ca3af" }}>
                    Tổng dự án
                  </span>
                }
                value={stats.totalProjects}
                styles={{
                  content: {
                    color: "#f3f4f6",
                  },
                }}
              />
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Card
              variant="none"
              style={{
                background: "#111827",
                border: "1px solid #1f2937",
              }}
            >
              <Statistic
                title={
                  <span style={{ color: "#9ca3af" }}>
                    Tổng đề xuất
                  </span>
                }
                value={stats.totalProposals}
                styles={{
                  content: {
                    color: "#f3f4f6",
                  },
                }}
              />
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Card
              variant="none"
              style={{
                background: "#111827",
                border: "1px solid #1f2937",
              }}
            >
              <Statistic
                title={
                  <span style={{ color: "#9ca3af" }}>
                    Tổng hợp đồng
                  </span>
                }
                value={stats.totalContracts}
                styles={{
                  content: {
                    color: "#f3f4f6",
                  },
                }}
              />
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Card
              variant="none"
              style={{
                background: "#111827",
                border: "1px solid #1f2937",
              }}
            >
              <Statistic
                title={
                  <span style={{ color: "#9ca3af" }}>
                    Giá trị hợp đồng
                  </span>
                }
                value={stats.totalContractValue}
                formatter={(value) =>
                  formatCurrency(value)
                }
                styles={{
                  content: {
                    color: "#10b981",
                  },
                }}
              />
            </Card>
          </Col>
        </Row>


        {/* SKILLS + ACTIVITIES */}

        <Row
          gutter={[16, 16]}
          style={{ marginTop: 24 }}
        >
          <Col xs={24} lg={14}>
            <Card
              title={
                <span style={{ color: "#ffffff" }}>
                  Kỹ năng AI phổ biến
                </span>
              }
              variant="none"
              style={{
                background: "#111827",
                border: "1px solid #1f2937",
                borderRadius: 12,
              }}
            >
              <Table
                rowKey={(record) =>
                  record.id ||
                  record.name ||
                  record.skill
                }
                columns={skillColumns}
                dataSource={stats.topSkills}
                pagination={false}
                bordered
                className="analytics-dark-table"
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
                          Chưa có dữ liệu kỹ năng.
                        </span>
                      }
                    />
                  ),
                }}
              />
            </Card>
          </Col>

          <Col xs={24} lg={10}>
            <Card
              title={
                <span style={{ color: "#ffffff" }}>
                  Hoạt động gần đây
                </span>
              }
              variant="none"
              style={{
                background: "#111827",
                border: "1px solid #1f2937",
                borderRadius: 12,
                minHeight: 350,
              }}
            >
              {timelineItems.length > 0 ? (
                <Timeline
                  mode="start"
                  items={timelineItems}
                />
              ) : (
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
                      Chưa có hoạt động gần đây.
                    </span>
                  }
                />
              )}
            </Card>
          </Col>
        </Row>
      </div>


      <style>{`
        .analytics-dark-table .ant-table {
          background: #111827 !important;
          color: #f3f4f6 !important;
        }

        .analytics-dark-table .ant-table-thead > tr > th {
          background: #1f2937 !important;
          color: #f3f4f6 !important;
          border-color: #374151 !important;
        }

        .analytics-dark-table .ant-table-tbody > tr > td {
          background: #111827 !important;
          color: #f3f4f6 !important;
          border-color: #1f2937 !important;
        }

        .analytics-dark-table .ant-table-tbody > tr:hover > td {
          background: #1f2937 !important;
        }

        .ant-timeline-item-content {
          color: #d1d5db !important;
        }

        .ant-timeline-item-label {
          color: #9ca3af !important;
        }
      `}</style>
    </div>
  );
};


/* =========================================================
   EXPORT
========================================================= */

const Analytics = () => (
  <App>
    <AnalyticsContent />
  </App>
);

export default Analytics;