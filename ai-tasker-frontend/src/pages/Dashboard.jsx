import React, { useEffect, useState } from "react";
import {
  App,
  Row,
  Col,
  Card,
  Statistic,
  Spin,
  Typography,
  Alert,
  Table,
  Progress,
  Tag,
  Avatar,
  Button,
  Flex,
  Empty,
} from "antd";

import {
  ProjectOutlined,
  UserOutlined,
  FileTextOutlined,
  DollarOutlined,
  ThunderboltOutlined,
  ClockCircleOutlined,
  RightOutlined,
} from "@ant-design/icons";

import axiosClient from "../api/axiosClient";

const { Title, Text } = Typography;

const Dashboard = () => {
  const { message } = App.useApp();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [stats, setStats] = useState({
    total_projects: 0,
    total_experts: 0,
    total_proposals: 0,
    total_revenue: 0,
  });

  const [recentProjects, setRecentProjects] = useState([]);
  const [skillsDistribution, setSkillsDistribution] = useState([]);

  const safeExtractArray = (res) => {
    if (!res) return [];
    if (Array.isArray(res)) return res;
    if (Array.isArray(res.data)) return res.data;
    if (Array.isArray(res.data?.data)) return res.data.data;
    return [];
  };

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError("");

      const [
        projectsRes,
        dashboardRes,
        proposalsRes,
      ] = await Promise.allSettled([
        axiosClient.get("/analytics/recent-projects"),
        axiosClient.get("/analytics/dashboard"),
        axiosClient.get("/analytics/recent-proposals"),
      ]);

      let hasError = false;

      if (projectsRes.status === "rejected") {
        console.error(
          "Lỗi tải recent projects:",
          projectsRes.reason
        );
        hasError = true;
      }

      if (dashboardRes.status === "rejected") {
        console.error(
          "Lỗi tải dashboard:",
          dashboardRes.reason
        );
        hasError = true;
      }

      if (proposalsRes.status === "rejected") {
        console.error(
          "Lỗi tải recent proposals:",
          proposalsRes.reason
        );
        hasError = true;
      }

      if (hasError) {
        setError(
          "Một hoặc nhiều dịch vụ dữ liệu không thể phản hồi. " +
          "Vui lòng kiểm tra Backend, Database hoặc Swagger."
        );
      }

      const projectsData =
        projectsRes.status === "fulfilled"
          ? safeExtractArray(projectsRes.value)
          : [];

      const dashboardData =
        dashboardRes.status === "fulfilled"
          ? dashboardRes.value.data
          : null;

      const proposalsData =
        proposalsRes.status === "fulfilled"
          ? safeExtractArray(proposalsRes.value)
          : [];

      setStats({
        total_projects:
          dashboardData?.total_projects ??
          dashboardData?.projects ??
          projectsData.length ??
          0,

        total_experts:
          dashboardData?.total_experts ??
          dashboardData?.experts ??
          0,

        total_proposals:
          dashboardData?.total_proposals ??
          dashboardData?.proposals ??
          proposalsData.length ??
          0,

        total_revenue:
          dashboardData?.total_revenue ??
          projectsData.reduce(
            (sum, project) =>
              sum + Number(project.budget || 0),
            0
          ),
      });

      setRecentProjects(
        projectsData.slice(0, 3)
      );

      const expertsData = Array.isArray(
        dashboardData?.experts
      )
        ? dashboardData.experts
        : [];

      const skillCounts = {};

      expertsData.forEach((expert) => {
        const skillsArray = Array.isArray(expert.skills)
          ? expert.skills.map((skill) =>
              typeof skill === "object"
                ? skill.name
                : skill
            )
          : String(expert.skills || "")
              .split(",")
              .map((skill) => skill.trim())
              .filter(Boolean);

        skillsArray.forEach((skill) => {
          if (!skill) return;

          skillCounts[skill] =
            (skillCounts[skill] || 0) + 1;
        });
      });

      const sortedSkills = Object.keys(skillCounts)
        .map((name) => ({
          name,
          count: skillCounts[name],
        }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 4);

      setSkillsDistribution(sortedSkills);

      if (!hasError) {
        message.success(
          "Đồng bộ dữ liệu hệ thống hoàn tất!"
        );
      }
    } catch (err) {
      console.error(err);

      setError(
        "Không thể kết nối hoặc đồng bộ dữ liệu hệ thống."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const navigateTo = (path) => {
    window.location.pathname = path;
  };

  const projectColumns = [
    {
      title: "Mã dự án",
      dataIndex: "id",
      key: "id",
      render: (text) => (
        <Text
          style={{
            color: "#9ca3af",
            fontFamily: "monospace",
          }}
        >
          {text || "N/A"}
        </Text>
      ),
    },
    {
      title: "Tên dự án AI",
      dataIndex: "title",
      key: "title",
      render: (text) => (
        <Text
          strong
          style={{
            color: "#f3f4f6",
          }}
        >
          {text || "Chưa cập nhật"}
        </Text>
      ),
    },
    {
      title: "Ngân sách phân phối",
      dataIndex: "budget",
      key: "budget",
      align: "right",
      render: (budget) => (
        <Text
          style={{
            color: "#10b981",
            fontWeight: 600,
          }}
        >
          {Number(budget || 0).toLocaleString(
            "vi-VN"
          )}{" "}
          đ
        </Text>
      ),
    },
    {
      title: "Tiến độ",
      key: "status",
      align: "center",
      render: (_, record) => {
        const status = String(
          record.status || ""
        ).toUpperCase();

        const statusConfig = {
          OPEN: {
            color: "green",
            label: "Đang mở",
          },
          PENDING: {
            color: "gold",
            label: "Chờ duyệt",
          },
          IN_PROGRESS: {
            color: "blue",
            label: "Đang thực thi",
          },
          COMPLETED: {
            color: "cyan",
            label: "Hoàn thành",
          },
          CANCELLED: {
            color: "red",
            label: "Đã hủy",
          },
        };

        const config =
          statusConfig[status] || {
            color: "default",
            label: status || "Chưa cập nhật",
          };

        return (
          <Tag color={config.color}>
            {config.label}
          </Tag>
        );
      },
    },
  ];

  if (loading) {
    return (
      <Flex
        justify="center"
        align="center"
        vertical
        style={{
          minHeight: "100vh",
          background: "#0f172a",
        }}
      >
        <Spin size="large" />

        <Text
          style={{
            color: "#818cf8",
            marginTop: 16,
          }}
        >
          Đang kết nối hệ thống dữ liệu...
        </Text>
      </Flex>
    );
  }

  return (
    <div
      style={{
        padding: 32,
        background: "#0f172a",
        minHeight: "100vh",
        color: "#fff",
      }}
    >
      <Flex
        justify="space-between"
        align="center"
        wrap="wrap"
        gap="middle"
        style={{
          marginBottom: 32,
        }}
      >
        <div>
          <Title
            level={2}
            style={{
              color: "#fff",
              margin: 0,
              fontWeight: 700,
            }}
          >
            Dashboard Hệ Thống
          </Title>

          <Text
            style={{
              color: "#9ca3af",
              fontSize: 14,
            }}
          >
            Chào mừng trở lại, hệ thống mạng lưới
            phân tác AI đang vận hành ổn định
          </Text>
        </div>

        <Button
          type="primary"
          icon={<ThunderboltOutlined />}
          loading={loading}
          onClick={loadDashboardData}
          style={{
            backgroundColor: "#4f46e5",
            borderRadius: 8,
            height: 40,
            fontWeight: 600,
          }}
        >
          Làm mới dữ liệu
        </Button>
      </Flex>

      {error && (
        <Alert
          type="error"
          message={error}
          showIcon
          closable
          onClose={() => setError("")}
          style={{
            marginBottom: 24,
            borderRadius: 8,
          }}
        />
      )}

      <Row gutter={[20, 20]}>
        <Col xs={24} sm={12} lg={6}>
          <Card
            hoverable
            variant="none"
            onClick={() =>
              navigateTo("/projects")
            }
            style={{
              background: "#111827",
              border: "1px solid #1f2937",
              borderRadius: 14,
              cursor: "pointer",
              padding: 4,
            }}
          >
            <Statistic
              title={
                <span
                  style={{
                    color: "#9ca3af",
                    fontSize: 14,
                    fontWeight: 500,
                  }}
                >
                  Tổng Dự Án
                </span>
              }
              value={stats.total_projects}
              styles={{
                content: {
                  color: "#fff",
                  fontWeight: 700,
                  fontSize: 32,
                  marginTop: 8,
                },
              }}
              prefix={
                <Avatar
                  size={44}
                  icon={
                    <ProjectOutlined
                      style={{
                        color: "#3b82f6",
                        fontSize: 20,
                      }}
                    />
                  }
                  style={{
                    backgroundColor:
                      "rgba(59, 130, 246, 0.12)",
                    marginRight: 8,
                  }}
                />
              }
            />

            <Flex
              align="center"
              gap={4}
              style={{ marginTop: 12 }}
            >
              <Tag color="blue">
                Xem chi tiết
              </Tag>

              <Text
                style={{
                  fontSize: 12,
                  color: "#6b7280",
                }}
              >
                Nhấp để quản lý
              </Text>
            </Flex>
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card
            hoverable
            variant="none"
            onClick={() =>
              navigateTo("/experts")
            }
            style={{
              background: "#111827",
              border: "1px solid #1f2937",
              borderRadius: 14,
              cursor: "pointer",
              padding: 4,
            }}
          >
            <Statistic
              title={
                <span
                  style={{
                    color: "#9ca3af",
                    fontSize: 14,
                    fontWeight: 500,
                  }}
                >
                  Chuyên Gia AI
                </span>
              }
              value={stats.total_experts}
              styles={{
                content: {
                  color: "#fff",
                  fontWeight: 700,
                  fontSize: 32,
                  marginTop: 8,
                },
              }}
              prefix={
                <Avatar
                  size={44}
                  icon={
                    <UserOutlined
                      style={{
                        color: "#a855f7",
                        fontSize: 20,
                      }}
                    />
                  }
                  style={{
                    backgroundColor:
                      "rgba(168, 85, 247, 0.12)",
                    marginRight: 8,
                  }}
                />
              }
            />

            <Flex
              align="center"
              gap={4}
              style={{ marginTop: 12 }}
            >
              <Tag color="purple">
                Hồ sơ xác thực
              </Tag>

              <Text
                style={{
                  fontSize: 12,
                  color: "#6b7280",
                }}
              >
                Kiểm duyệt chuyên gia
              </Text>
            </Flex>
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card
            hoverable
            variant="none"
            onClick={() =>
              navigateTo("/proposals")
            }
            style={{
              background: "#111827",
              border: "1px solid #1f2937",
              borderRadius: 14,
              cursor: "pointer",
              padding: 4,
            }}
          >
            <Statistic
              title={
                <span
                  style={{
                    color: "#9ca3af",
                    fontSize: 14,
                    fontWeight: 500,
                  }}
                >
                  Đề Xuất / Báo Giá
                </span>
              }
              value={stats.total_proposals}
              styles={{
                content: {
                  color: "#fff",
                  fontWeight: 700,
                  fontSize: 32,
                  marginTop: 8,
                },
              }}
              prefix={
                <Avatar
                  size={44}
                  icon={
                    <FileTextOutlined
                      style={{
                        color: "#eab308",
                        fontSize: 20,
                      }}
                    />
                  }
                  style={{
                    backgroundColor:
                      "rgba(234, 179, 8, 0.12)",
                    marginRight: 8,
                  }}
                />
              }
            />

            <Flex
              align="center"
              gap={4}
              style={{ marginTop: 12 }}
            >
              <Tag color="gold">
                Đồng bộ tự động
              </Tag>

              <Text
                style={{
                  fontSize: 12,
                  color: "#6b7280",
                }}
              >
                Smart Matching
              </Text>
            </Flex>
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card
            variant="none"
            style={{
              background: "#111827",
              border: "1px solid #1f2937",
              borderRadius: 14,
              padding: 4,
            }}
          >
            <Statistic
              title={
                <span
                  style={{
                    color: "#9ca3af",
                    fontSize: 14,
                    fontWeight: 500,
                  }}
                >
                  Tổng Hạn Mức Cam Kết
                </span>
              }
              value={stats.total_revenue}
              precision={0}
              styles={{
                content: {
                  color: "#10b981",
                  fontWeight: 700,
                  fontSize: 26,
                  marginTop: 8,
                },
              }}
              prefix={
                <Avatar
                  size={44}
                  icon={
                    <DollarOutlined
                      style={{
                        color: "#10b981",
                        fontSize: 20,
                      }}
                    />
                  }
                  style={{
                    backgroundColor:
                      "rgba(16, 185, 129, 0.12)",
                    marginRight: 8,
                  }}
                />
              }
              suffix={
                <span
                  style={{
                    fontSize: 14,
                    color: "#10b981",
                    marginLeft: 4,
                  }}
                >
                  VND
                </span>
              }
            />

            <div style={{ marginTop: 16 }}>
              <Progress
                percent={100}
                size="small"
                status="active"
                strokeColor="#10b981"
                showInfo={false}
              />
            </div>
          </Card>
        </Col>
      </Row>

      <Row
        gutter={[20, 20]}
        style={{
          marginTop: 28,
        }}
      >
        <Col xs={24} lg={16}>
          <Card
            title={
              <span
                style={{
                  color: "#fff",
                  fontWeight: 600,
                }}
              >
                <ClockCircleOutlined
                  style={{
                    marginRight: 8,
                    color: "#818cf8",
                  }}
                />
                Lịch Sử Cập Nhật Dự Án Mới Nhất
              </span>
            }
            variant="none"
            style={{
              background: "#111827",
              border: "1px solid #1f2937",
              borderRadius: 14,
            }}
            extra={
              <Button
                type="link"
                onClick={() =>
                  navigateTo("/projects")
                }
                style={{
                  color: "#818cf8",
                  fontWeight: 500,
                }}
              >
                Xem toàn bộ
                <RightOutlined
                  style={{
                    fontSize: 10,
                  }}
                />
              </Button>
            }
          >
            <Table
              columns={projectColumns}
              dataSource={recentProjects}
              pagination={false}
              rowKey="id"
              className="dark-table"
              locale={{
                emptyText: (
                  <Empty
                    image={
                      Empty.PRESENTED_IMAGE_SIMPLE
                    }
                    description={
                      <span
                        style={{
                          color: "#6b7280",
                        }}
                      >
                        Chưa có dữ liệu dự án
                      </span>
                    }
                  />
                ),
              }}
            />
          </Card>
        </Col>

        <Col xs={24} lg={8}>
          <Card
            title={
              <span
                style={{
                  color: "#fff",
                  fontWeight: 600,
                }}
              >
                Cơ Cấu Kỹ Năng Hệ Thống
              </span>
            }
            variant="none"
            style={{
              background: "#111827",
              border: "1px solid #1f2937",
              borderRadius: 14,
              height: "100%",
            }}
          >
            {skillsDistribution.length === 0 ? (
              <Flex
                justify="center"
                align="center"
                style={{
                  height: 180,
                }}
              >
                <Text
                  style={{
                    color: "#6b7280",
                  }}
                >
                  Chưa có dữ liệu kỹ năng
                </Text>
              </Flex>
            ) : (
              skillsDistribution.map(
                (item, index) => {
                  const colors = [
                    "#4f46e5",
                    "#a855f7",
                    "#ec4899",
                    "#3b82f6",
                  ];

                  const percent =
                    stats.total_experts > 0
                      ? Math.min(
                          100,
                          Math.round(
                            (item.count /
                              stats.total_experts) *
                              100
                          )
                        )
                      : 0;

                  return (
                    <div
                      key={item.name}
                      style={{
                        marginBottom: 20,
                      }}
                    >
                      <Flex
                        justify="space-between"
                        align="center"
                        style={{
                          marginBottom: 6,
                        }}
                      >
                        <Text
                          strong
                          style={{
                            color: "#e5e7eb",
                          }}
                        >
                          {item.name}
                        </Text>

                        <Tag
                          style={{
                            border: "none",
                            background: "#1f2937",
                            color: "#9ca3af",
                          }}
                        >
                          {item.count} nhân sự
                        </Tag>
                      </Flex>

                      <Progress
                        percent={percent}
                        strokeColor={
                          colors[
                            index % colors.length
                          ]
                        }
                        trailColor="#1f2937"
                        showInfo={false}
                        size={8}
                      />
                    </div>
                  );
                }
              )
            )}
          </Card>
        </Col>
      </Row>

      <style>{`
        .dark-table .ant-table {
          background: #111827 !important;
          color: #f3f4f6 !important;
        }

        .dark-table .ant-table-container {
          background: #111827 !important;
        }

        .dark-table .ant-table-thead > tr > th {
          background: #1f2937 !important;
          color: #9ca3af !important;
          border-bottom: 1px solid #374151 !important;
        }

        .dark-table .ant-table-tbody > tr > td {
          background: #111827 !important;
          border-bottom: 1px solid #1f2937 !important;
        }

        .dark-table .ant-table-tbody > tr:hover > td {
          background: #1f2937 !important;
        }

        .dark-table .ant-empty-description {
          color: #6b7280 !important;
        }
      `}</style>
    </div>
  );
};

export default Dashboard;