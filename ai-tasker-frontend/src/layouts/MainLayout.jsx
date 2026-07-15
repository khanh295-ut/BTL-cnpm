import React, { useMemo, useState } from "react";

import {
  App,
  Avatar,
  Badge,
  Button,
  ConfigProvider,
  Dropdown,
  Layout,
  List,
  Menu,
  Popover,
  Space,
  Tag,
  Tooltip,
  Typography,
  theme,
} from "antd";

import {
  AppstoreOutlined,
  BarChartOutlined,
  BellOutlined,
  CreditCardOutlined,
  FileTextOutlined,
  InfoCircleOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  ProjectOutlined,
  RobotOutlined,
  RocketOutlined,
  SettingOutlined,
  ShopOutlined,
  UserOutlined,
  WalletOutlined,
} from "@ant-design/icons";

import {
  useLocation,
  useNavigate,
} from "react-router-dom";


const {
  Content,
  Header,
  Sider,
} = Layout;

const {
  Text,
} = Typography;


/**
 * Chiều rộng sidebar khi mở.
 */
const SIDER_WIDTH = 260;

/**
 * Chiều rộng sidebar khi thu gọn.
 */
const COLLAPSED_WIDTH = 82;


/**
 * Lấy key menu phù hợp với URL hiện tại.
 *
 * Hàm này giúp menu vẫn được chọn đúng khi URL có dạng:
 *
 * /projects/uuid
 * /experts/uuid
 * /job-assistant
 */
const resolveSelectedMenuKey = (
  pathname,
  menuItems
) => {
  const validKeys = menuItems
    .filter(
      (item) => (
        item
        && item.key
        && typeof item.key === "string"
      )
    )
    .map((item) => item.key);

  const exactMatch = validKeys.find(
    (key) => pathname === key
  );

  if (exactMatch) {
    return exactMatch;
  }

  const nestedMatch = validKeys
    .filter((key) => key !== "/")
    .sort(
      (first, second) => (
        second.length - first.length
      )
    )
    .find(
      (key) => pathname.startsWith(
        `${key}/`
      )
    );

  return nestedMatch || "/dashboard";
};


function MainLayout({ children }) {
  const navigate = useNavigate();
  const location = useLocation();

  const {
    message,
  } = App.useApp();

  const [collapsed, setCollapsed] = useState(false);

  /*
   * Hiện đang dùng dữ liệu mẫu.
   * Sau này có thể thay bằng notificationApi.
   */
  const [notifications] = useState([
    {
      id: 1,
      title: "Dự án mới",
      description:
        "Có một đề xuất mới cho dự án AI Chatbot.",
      type: "PROJECT",
      isRead: false,
    },
    {
      id: 2,
      title: "Hệ thống",
      description:
        "AITasker đã đồng bộ thành công với Swagger.",
      type: "SYSTEM",
      isRead: false,
    },
  ]);


  // ======================================================
  // MENU ITEMS
  // ======================================================

  const menuItems = useMemo(
    () => [
      {
        key: "/dashboard",
        icon: <AppstoreOutlined />,
        label: "Tổng quan",
      },

      {
        type: "divider",
      },

      {
        key: "/projects",
        icon: <ProjectOutlined />,
        label: "Quản lý dự án",
      },
      {
        key: "/experts",
        icon: <UserOutlined />,
        label: "Chuyên gia AI",
      },
      {
        key: "/proposals",
        icon: <FileTextOutlined />,
        label: "Đề xuất / Báo giá",
      },
      {
        key: "/contracts",
        icon: <WalletOutlined />,
        label: "Hợp đồng & Ký quỹ",
      },

      {
        type: "divider",
      },

      {
        key: "/job-assistant",
        icon: <RobotOutlined />,
        label: "AI Job Assistant",
      },

      {
        type: "divider",
      },

      {
        key: "/enterprises",
        icon: <ShopOutlined />,
        label: "Doanh nghiệp",
      },
      {
        key: "/payments",
        icon: <CreditCardOutlined />,
        label: "Thanh toán",
      },
      {
        key: "/analytics",
        icon: <BarChartOutlined />,
        label: "Phân tích & Thống kê",
      },

      {
        type: "divider",
      },

      {
        key: "/settings",
        icon: <SettingOutlined />,
        label: "Cài đặt hệ thống",
      },
      {
        key: "/ai-services",
        icon: <AppstoreOutlined />,
        label: "Dịch vụ AI",
      },
    ],
    []
  );


  // ======================================================
  // HEADER TITLE
  // ======================================================

  const headerTitles = useMemo(
    () => ({
      "/dashboard": "Tổng quan hệ thống",
      "/projects": "Quản lý dự án",
      "/experts": "Tìm chuyên gia AI",
      "/proposals": "Đề xuất và báo giá",
      "/contracts": "Hợp đồng và ký quỹ",
      "/job-assistant": "AI Job Assistant",
      "/enterprises": "Quản lý doanh nghiệp",
      "/payments": "Lịch sử thanh toán",
      "/analytics": "Phân tích và thống kê",
      "/profile": "Thông tin cá nhân",
      "/settings": "Cài đặt hệ thống",
    }),
    []
  );


  const selectedMenuKey = resolveSelectedMenuKey(
    location.pathname,
    menuItems
  );


  const currentHeaderTitle = (
    headerTitles[selectedMenuKey]
    || "Bảng điều khiển"
  );


  // ======================================================
  // LOGOUT
  // ======================================================

  const handleLogout = () => {
    message.loading({
      content: "Đang đăng xuất...",
      key: "logout",
    });

    window.setTimeout(() => {
      localStorage.clear();

      message.success({
        content: "Đăng xuất thành công. Hẹn gặp lại!",
        key: "logout",
      });

      navigate(
        "/login",
        {
          replace: true,
        }
      );
    }, 600);
  };


  // ======================================================
  // AVATAR DROPDOWN
  // ======================================================

  const avatarMenu = {
    items: [
      {
        key: "/profile",
        label: "Thông tin cá nhân",
        icon: <UserOutlined />,
      },
      {
        key: "/settings",
        label: "Cài đặt tài khoản",
        icon: <SettingOutlined />,
      },
      {
        type: "divider",
      },
      {
        key: "logout",
        label: "Đăng xuất",
        icon: <LogoutOutlined />,
        danger: true,
      },
    ],

    onClick: ({ key }) => {
      if (key === "logout") {
        handleLogout();
        return;
      }

      navigate(key);
    },
  };


  // ======================================================
  // NOTIFICATIONS
  // ======================================================

  const unreadNotificationCount = notifications.filter(
    (notification) => !notification.isRead
  ).length;


  const notificationContent = (
    <div className="main-layout-notification">
      <div className="main-layout-notification-header">
        <Text strong>
          Thông báo
        </Text>

        <Tag color="blue">
          {unreadNotificationCount} chưa đọc
        </Tag>
      </div>

      <List
        size="small"
        dataSource={notifications}
        locale={{
          emptyText: "Không có thông báo.",
        }}
        renderItem={(item) => (
          <List.Item
            className="main-layout-notification-item"
          >
            <List.Item.Meta
              avatar={
                <Avatar
                  size="small"
                  icon={<InfoCircleOutlined />}
                  style={{
                    background:
                      item.type === "PROJECT"
                        ? "#4f46e5"
                        : "#0891b2",
                  }}
                />
              }
              title={
                <Text
                  strong
                  style={{
                    fontSize: 13,
                  }}
                >
                  {item.title}
                </Text>
              }
              description={
                <Text
                  type="secondary"
                  style={{
                    fontSize: 12,
                    lineHeight: 1.5,
                  }}
                >
                  {item.description}
                </Text>
              }
            />
          </List.Item>
        )}
      />

      <Button
        type="link"
        block
        style={{
          marginTop: 4,
        }}
        onClick={() => {
          message.info(
            "Trang quản lý thông báo sẽ được bổ sung sau."
          );
        }}
      >
        Xem tất cả thông báo
      </Button>
    </div>
  );


  // ======================================================
  // RENDER
  // ======================================================

  return (
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,

        token: {
          colorPrimary: "#4f46e5",
          colorInfo: "#4f46e5",

          colorBgBase: "#090d16",
          colorBgContainer: "#111827",
          colorBgElevated: "#111827",

          borderRadius: 10,

          fontFamily:
            "Inter, -apple-system, BlinkMacSystemFont, "
            + '"Segoe UI", sans-serif',
        },

        components: {
          Layout: {
            bodyBg: "#090d16",
            headerBg: "#0b0f19",
            siderBg: "#0b0f19",
          },

          Menu: {
            darkItemBg: "transparent",
            darkItemSelectedBg: "#4f46e5",
            darkItemHoverBg:
              "rgba(79, 70, 229, 0.25)",
            itemBorderRadius: 9,
            itemMarginBlock: 4,
          },
        },
      }}
    >
      <Layout
        className="main-layout-root"
      >
        {/* =================================================
            SIDEBAR
        ================================================= */}

        <Sider
          collapsible
          trigger={null}
          collapsed={collapsed}
          collapsedWidth={COLLAPSED_WIDTH}
          width={SIDER_WIDTH}
          theme="dark"
          className="main-layout-sider"
        >
          <div
            className={
              collapsed
                ? "main-layout-logo collapsed"
                : "main-layout-logo"
            }
            onClick={() => navigate("/dashboard")}
          >
            <div className="main-layout-logo-icon">
              <RocketOutlined />
            </div>

            {!collapsed && (
              <div className="main-layout-logo-content">
                <div className="main-layout-logo-title">
                  AITasker
                </div>

                <div className="main-layout-logo-subtitle">
                  AI Marketplace Platform
                </div>
              </div>
            )}
          </div>

          <div className="main-layout-menu-wrapper">
            <Menu
              mode="inline"
              theme="dark"
              selectedKeys={[
                selectedMenuKey,
              ]}
              items={menuItems}
              onClick={({ key }) => {
                if (
                  typeof key === "string"
                  && key.startsWith("/")
                ) {
                  navigate(key);
                }
              }}
            />
          </div>

          {!collapsed && (
            <div className="main-layout-version">
              <Text type="secondary">
                AITasker Backend
              </Text>

              <Tag
                color="green"
                style={{
                  marginInlineEnd: 0,
                }}
              >
                Online
              </Tag>
            </div>
          )}
        </Sider>


        {/* =================================================
            MAIN CONTENT
        ================================================= */}

        <Layout
          className="main-layout-body"
          style={{
            paddingLeft: collapsed
              ? COLLAPSED_WIDTH
              : SIDER_WIDTH,
          }}
        >
          {/* ===============================================
              HEADER
          =============================================== */}

          <Header
            className="main-layout-header"
          >
            <div className="main-layout-header-left">
              <Tooltip
                title={
                  collapsed
                    ? "Mở rộng menu"
                    : "Thu gọn menu"
                }
              >
                <Button
                  type="text"
                  className="main-layout-collapse-button"
                  icon={
                    collapsed
                      ? <MenuUnfoldOutlined />
                      : <MenuFoldOutlined />
                  }
                  onClick={() => {
                    setCollapsed(
                      (previous) => !previous
                    );
                  }}
                />
              </Tooltip>

              <div>
                <div className="main-layout-breadcrumb">
                  Hệ thống /{" "}
                  <span>
                    {currentHeaderTitle}
                  </span>
                </div>

                <div className="main-layout-mobile-title">
                  {currentHeaderTitle}
                </div>
              </div>
            </div>

            <div className="main-layout-header-actions">
              <Popover
                content={notificationContent}
                trigger="click"
                placement="bottomRight"
                overlayClassName="main-layout-popover"
              >
                <Badge
                  count={unreadNotificationCount}
                  size="small"
                  overflowCount={99}
                >
                  <Button
                    type="text"
                    shape="circle"
                    className="main-layout-header-icon"
                    icon={<BellOutlined />}
                  />
                </Badge>
              </Popover>

              <Dropdown
                menu={avatarMenu}
                trigger={["click"]}
                placement="bottomRight"
              >
                <div className="main-layout-user">
                  <Avatar
                    src={
                      "https://api.dicebear.com/"
                      + "7.x/miniavs/svg?seed=1"
                    }
                    style={{
                      background: "#4f46e5",
                    }}
                  />

                  <div className="main-layout-user-info">
                    <Text
                      strong
                      className="main-layout-user-name"
                    >
                      Admin Khanh
                    </Text>

                    <Text
                      type="secondary"
                      className="main-layout-user-role"
                    >
                      Quản trị viên
                    </Text>
                  </div>
                </div>
              </Dropdown>
            </div>
          </Header>


          {/* ===============================================
              PAGE CONTENT
          =============================================== */}

          <Content
            className="main-layout-content"
          >
            {children}
          </Content>
        </Layout>


        {/* =================================================
            GLOBAL STYLES
        ================================================= */}

        <style>
          {`
            html,
            body,
            #root {
              min-height: 100%;
              margin: 0;
              background: #090d16;
            }

            body {
              -webkit-font-smoothing: antialiased;
              text-rendering: optimizeLegibility;
            }

            * {
              box-sizing: border-box;
            }

            .main-layout-root {
              min-height: 100vh;
              background: #090d16;
            }

            /* =============================================
               SIDEBAR
            ============================================= */

            .main-layout-sider {
              position: fixed !important;
              top: 0;
              bottom: 0;
              left: 0;
              z-index: 100;
              height: 100vh;
              overflow: hidden;
              border-right:
                1px solid rgba(255, 255, 255, 0.06);
              background: #0b0f19 !important;
              box-shadow:
                8px 0 30px rgba(0, 0, 0, 0.12);
            }

            .main-layout-logo {
              height: 70px;
              display: flex;
              align-items: center;
              gap: 12px;
              padding: 0 20px;
              cursor: pointer;
              border-bottom:
                1px solid rgba(255, 255, 255, 0.06);
              transition: all 0.25s ease;
            }

            .main-layout-logo.collapsed {
              justify-content: center;
              padding: 0;
            }

            .main-layout-logo-icon {
              flex: 0 0 auto;
              width: 36px;
              height: 36px;
              display: flex;
              align-items: center;
              justify-content: center;
              border-radius: 10px;
              color: #ffffff;
              font-size: 18px;
              background:
                linear-gradient(
                  135deg,
                  #4f46e5 0%,
                  #7c3aed 100%
                );
              box-shadow:
                0 8px 20px rgba(79, 70, 229, 0.3);
            }

            .main-layout-logo-content {
              min-width: 0;
            }

            .main-layout-logo-title {
              color: #ffffff;
              font-size: 18px;
              font-weight: 800;
              line-height: 1.2;
              letter-spacing: 0.3px;
            }

            .main-layout-logo-subtitle {
              margin-top: 3px;
              color: #64748b;
              font-size: 10px;
              white-space: nowrap;
            }

            .main-layout-menu-wrapper {
              height: calc(100vh - 126px);
              padding: 14px 10px;
              overflow-y: auto;
              overflow-x: hidden;
            }

            .main-layout-menu-wrapper::-webkit-scrollbar {
              width: 5px;
            }

            .main-layout-menu-wrapper::-webkit-scrollbar-thumb {
              border-radius: 999px;
              background:
                rgba(148, 163, 184, 0.22);
            }

            .main-layout-menu-wrapper
            .ant-menu {
              border-inline-end: 0 !important;
              background: transparent !important;
            }

            .main-layout-menu-wrapper
            .ant-menu-item {
              height: 43px;
              line-height: 43px;
            }

            .main-layout-menu-wrapper
            .ant-menu-item-selected {
              color: #ffffff !important;
              background: #4f46e5 !important;
              box-shadow:
                0 8px 20px rgba(79, 70, 229, 0.24);
            }

            .main-layout-menu-wrapper
            .ant-menu-item-selected::after {
              display: none;
            }

            .main-layout-menu-wrapper
            .ant-menu-item:hover {
              color: #ffffff !important;
            }

            .main-layout-menu-wrapper
            .ant-menu-item-divider {
              margin: 13px 10px;
              border-color:
                rgba(255, 255, 255, 0.055);
            }

            .main-layout-version {
              position: absolute;
              right: 16px;
              bottom: 14px;
              left: 16px;
              display: flex;
              align-items: center;
              justify-content: space-between;
              padding: 9px 11px;
              border:
                1px solid rgba(255, 255, 255, 0.06);
              border-radius: 10px;
              background:
                rgba(255, 255, 255, 0.025);
              font-size: 11px;
            }

            /* =============================================
               MAIN BODY
            ============================================= */

            .main-layout-body {
              min-height: 100vh;
              background: #090d16 !important;
              transition: padding-left 0.2s ease;
            }

            /* =============================================
               HEADER
            ============================================= */

            .main-layout-header {
              position: sticky;
              top: 0;
              z-index: 99;
              height: 70px;
              display: flex;
              align-items: center;
              justify-content: space-between;
              gap: 20px;
              padding: 0 28px;
              border-bottom:
                1px solid rgba(255, 255, 255, 0.06);
              background:
                rgba(11, 15, 25, 0.86) !important;
              backdrop-filter: blur(14px);
              box-shadow:
                0 8px 28px rgba(0, 0, 0, 0.08);
            }

            .main-layout-header-left {
              min-width: 0;
              display: flex;
              align-items: center;
              gap: 14px;
            }

            .main-layout-collapse-button {
              flex: 0 0 auto;
              color: #94a3b8 !important;
              font-size: 18px;
            }

            .main-layout-collapse-button:hover {
              color: #ffffff !important;
              background:
                rgba(255, 255, 255, 0.07) !important;
            }

            .main-layout-breadcrumb {
              overflow: hidden;
              color: #64748b;
              font-size: 13px;
              text-overflow: ellipsis;
              white-space: nowrap;
            }

            .main-layout-breadcrumb span {
              color: #f8fafc;
              font-weight: 650;
            }

            .main-layout-mobile-title {
              display: none;
              color: #ffffff;
              font-weight: 700;
            }

            .main-layout-header-actions {
              flex: 0 0 auto;
              display: flex;
              align-items: center;
              gap: 18px;
            }

            .main-layout-header-icon {
              color: #94a3b8 !important;
              font-size: 18px;
            }

            .main-layout-header-icon:hover {
              color: #ffffff !important;
              background:
                rgba(255, 255, 255, 0.07) !important;
            }

            .main-layout-user {
              display: flex;
              align-items: center;
              gap: 10px;
              padding: 5px 8px;
              border-radius: 10px;
              cursor: pointer;
              transition: background 0.2s ease;
            }

            .main-layout-user:hover {
              background:
                rgba(255, 255, 255, 0.06);
            }

            .main-layout-user-info {
              display: flex;
              flex-direction: column;
              line-height: 1.2;
            }

            .main-layout-user-name {
              color: #e2e8f0 !important;
              font-size: 13px;
            }

            .main-layout-user-role {
              margin-top: 3px;
              font-size: 11px;
            }

            /* =============================================
               CONTENT
            ============================================= */

            .main-layout-content {
              width: 100%;
              max-width: 1500px;
              min-height: calc(100vh - 70px);
              margin: 0 auto;
              padding: 28px 30px 40px;
              overflow-x: hidden;
            }

            /* =============================================
               POPOVER
            ============================================= */

            .main-layout-notification {
              width: 320px;
              max-width: calc(100vw - 40px);
            }

            .main-layout-notification-header {
              display: flex;
              align-items: center;
              justify-content: space-between;
              gap: 12px;
              padding-bottom: 10px;
              border-bottom:
                1px solid rgba(255, 255, 255, 0.08);
            }

            .main-layout-notification-item {
              padding: 12px 2px !important;
            }

            .main-layout-popover
            .ant-popover-inner {
              border:
                1px solid rgba(255, 255, 255, 0.08);
              background: #111827 !important;
              box-shadow:
                0 20px 50px rgba(0, 0, 0, 0.35);
            }

            /* =============================================
               GLOBAL ANT DESIGN FIXES
            ============================================= */

            .main-layout-root
            .ant-card {
              border-color:
                rgba(255, 255, 255, 0.075);
            }

            .main-layout-root
            .ant-table-wrapper
            .ant-table {
              background: #111827;
            }

            .main-layout-root
            .ant-typography {
              overflow-wrap: anywhere;
            }

            /* =============================================
               RESPONSIVE
            ============================================= */

            @media (max-width: 900px) {
              .main-layout-user-info {
                display: none;
              }

              .main-layout-content {
                padding: 22px 20px 32px;
              }
            }

            @media (max-width: 700px) {
              .main-layout-sider {
                display: none;
              }

              .main-layout-body {
                padding-left: 0 !important;
              }

              .main-layout-collapse-button {
                display: none;
              }

              .main-layout-header {
                height: 62px;
                padding: 0 16px;
              }

              .main-layout-breadcrumb {
                display: none;
              }

              .main-layout-mobile-title {
                display: block;
              }

              .main-layout-content {
                min-height: calc(100vh - 62px);
                padding: 18px 14px 28px;
              }

              .main-layout-header-actions {
                gap: 10px;
              }
            }
          `}
        </style>
      </Layout>
    </ConfigProvider>
  );
}


export default MainLayout;