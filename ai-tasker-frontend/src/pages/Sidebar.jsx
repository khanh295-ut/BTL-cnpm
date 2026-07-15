import React from 'react';
import { Layout, Menu, Typography } from 'antd';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  DashboardOutlined,
  ProjectOutlined,
  UserOutlined,
  FileTextOutlined,
  WalletOutlined,
  RobotOutlined
} from '@ant-design/icons';

const { Sider } = Layout;
const { Title } = Typography;

const Sidebar = () => {
  const location = useLocation();
  const navigate = useNavigate();

  // Định nghĩa danh mục Menu đồng bộ 100% với các Route hệ thống
  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined style={{ fontSize: '16px' }} />,
      label: 'Tổng quan',
    },
    {
      key: '/projects',
      icon: <ProjectOutlined style={{ fontSize: '16px' }} />,
      label: 'Quản lý Dự án',
    },
    {
      key: '/experts',
      icon: <UserOutlined style={{ fontSize: '16px' }} />,
      label: 'Tìm Chuyên gia AI',
    },
    {
      key: '/proposals',
      icon: <FileTextOutlined style={{ fontSize: '16px' }} />,
      label: 'Đề xuất / Báo giá',
    },
    {
      key: '/contracts',
      icon: <WalletOutlined style={{ fontSize: '16px', color: '#fbbf24' }} />, // Đã sửa: Chuyển màu vàng sang tông sáng của Dark UI
      label: 'Hợp đồng & Ký quỹ',
    },
  ];

  const handleMenuClick = (e) => {
    navigate(e.key);
  };

  return (
    <Sider
      breakpoint="lg"
      collapsedWidth="0"
      width={260}
      style={{
        height: '100vh',
        position: 'sticky',
        top: 0,
        left: 0,
        // ĐÃ SỬA: Thay thế #000000 bằng màu tối sâu hệ thống #111827
        background: '#111827',
        borderRight: '1px solid #1f2937',
        zIndex: 100,
      }}
    >
      {/* ĐÃ THÊM: Tiêm CSS để ép trạng thái Hover & Active của Menu sang Indigo cao cấp */}
      <style>{`
        .custom-admin-sidebar-menu .ant-menu-item {
          color: #9ca3af !important;
          border-radius: 8px !important;
          margin-bottom: 4px !important;
        }
        .custom-admin-sidebar-menu .ant-menu-item:hover {
          color: #fff !important;
          background-color: #1f2937 !important;
        }
        .custom-admin-sidebar-menu .ant-menu-item-selected {
          background-color: #4f46e5 !important;
          color: #fff !important;
        }
        .custom-admin-sidebar-menu .ant-menu-item-selected .anticon {
          color: #fff !important;
        }
      `}</style>

      {/* Brand Logo */}
      <div
        style={{
          height: '64px',
          display: 'flex',
          alignItems: 'center',
          padding: '0 24px',
          borderBottom: '1px solid #1f2937',
          gap: '12px'
        }}
      >
        <RobotOutlined style={{ fontSize: '24px', color: '#818cf8' }} />
        <Title
          level={4}
          style={{
            color: '#ffffff',
            margin: 0,
            fontFamily: 'Segoe UI, sans-serif',
            fontWeight: 'bold',
            letterSpacing: '0.5px'
          }}
        >
          AI TASKER
        </Title>
      </div>

      {/* Menu Antd */}
      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={[location.pathname]}
        onClick={handleMenuClick}
        items={menuItems}
        style={{
          background: 'transparent',
          padding: '16px 12px',
        }}
        className="custom-admin-sidebar-menu"
      />
    </Sider>
  );
};

export default Sidebar;