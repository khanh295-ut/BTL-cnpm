import React, { useEffect, useState } from "react";
import {
  Card,
  Row,
  Col,
  Avatar,
  Typography,
  Form,
  Input,
  Button,
  Tabs,
  Divider,
  Spin,
  App,
} from "antd";

import {
  UserOutlined,
  MailOutlined,
  SaveOutlined,
  LockOutlined,
  ReloadOutlined,
} from "@ant-design/icons";

const { Title, Text } = Typography;

function ProfileContent() {
  const [profileForm] = Form.useForm();
  const [passwordForm] = Form.useForm();

  const { message } = App.useApp();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [user, setUser] = useState({
    name: "",
    email: "",
    role: "",
    avatar: null,
  });

  useEffect(() => {
    loadProfile();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  //------------------------------------
  // Load profile
  //------------------------------------
  const loadProfile = async () => {
    setLoading(true);
    try {
      const data = {
        name: "Admin Khanh",
        email: "admin@gmail.com",
        role: "Administrator",
        avatar: null,
      };

      setUser(data);

      profileForm.setFieldsValue({
        name: data.name,
        email: data.email,
      });
    } finally {
      setLoading(false);
    }
  };

  //------------------------------------
  // Update Profile
  //------------------------------------
  const updateProfile = async (values) => {
    setSaving(true);
    try {
      setUser({
        ...user,
        name: values.name,
      });
      message.success("Cập nhật hồ sơ thành công");
    } finally {
      setSaving(false);
    }
  };

  //------------------------------------
  // Change Password
  //------------------------------------
  const changePassword = async () => {
    setSaving(true);
    try {
      passwordForm.resetFields();
      message.success("Đổi mật khẩu thành công");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: "center", padding: 80, background: "#090d16", minHeight: "100vh" }}>
        <Spin size="large" tip={<span style={{ color: "#9ca3af", marginTop: 8, display: "block" }}>Đang tải cấu hình...</span>} />
      </div>
    );
  }

  return (
    <div style={{ padding: "24px", background: "#090d16", minHeight: "100vh" }}>
      
      {/* ĐÃ THÊM: Tiêm CSS Style nhuộm Dark UI tinh tế cho component Tabs và Form của Antd */}
      <style>{`
        /* Màu tiêu đề các tab chưa active */
        .ant-tabs-tab {
          color: #9ca3af !important;
        }
        /* Màu tiêu đề tab khi được chọn (Active) hoặc hover */
        .ant-tabs-tab-active .ant-tabs-tab-btn, .ant-tabs-tab:hover {
          color: #818cf8 !important;
        }
        /* Thanh line trượt phía dưới Tab đang active */
        .ant-tabs-ink-bar {
          background: #4f46e5 !important;
        }
        /* Fix màu ô Input khi bị Disabled (như ô Email) */
        .ant-input-disabled {
          background: #111827 !important;
          color: #6b7280 !important;
          border-color: #1f2937 !important;
        }
      `}</style>

      {/* ĐÃ SỬA: Card nền tối đồng bộ hệ thống */}
      <Card style={{ background: "#111827", border: "1px solid #1f2937", borderRadius: 12, padding: "12px" }}>
        <Row gutter={[32, 32]}>
          
          {/* CỘT TRÁI: AVATAR & THÔNG TIN TỔNG QUAN */}
          <Col xs={24} md={8}>
            <div style={{ textAlign: "center", padding: "10px 0" }}>
              <Avatar
                size={130}
                src={user.avatar || undefined}
                icon={<UserOutlined />}
                style={{ background: "#1f2937", color: "#9ca3af", border: "2px solid #374151" }}
              />

              {/* ĐÃ SỬA: Ép màu chữ trắng */}
              <Title level={3} style={{ marginTop: 20, marginBottom: 4, color: "#fff", fontWeight: 600 }}>
                {user.name}
              </Title>

              {/* ĐÃ SỬA: Chữ phụ màu xám sáng */}
              <Text style={{ color: "#9ca3af" }}>
                {user.role}
              </Text>

              {/* ĐÃ SỬA: Màu đường gạch ngang tối */}
              <Divider style={{ borderColor: "#1f2937", margin: "20px 0" }} />

              <Button
                icon={<ReloadOutlined />}
                onClick={loadProfile}
                ghost
                style={{ color: "#9ca3af", borderColor: "#374151" }}
              >
                Tải lại
              </Button>
            </div>
          </Col>

          {/* CỘT PHẢI: CONFIG TABS */}
          <Col xs={24} md={16}>
            <Tabs
              defaultActiveKey="1"
              items={[
                {
                  key: "1",
                  label: "Thông tin cá nhân",
                  children: (
                    <Form
                      form={profileForm}
                      layout="vertical"
                      onFinish={updateProfile}
                      style={{ marginTop: 16 }}
                    >
                      <Form.Item
                        label={<span style={{ color: "#9ca3af" }}>Họ và tên</span>}
                        name="name"
                        rules={[{ required: true, message: "Nhập họ tên" }]}
                      >
                        <Input
                          prefix={<UserOutlined style={{ color: "#6b7280" }} />}
                          style={{ background: "#1f2937", color: "#fff", border: "1px solid #374151" }}
                        />
                      </Form.Item>

                      <Form.Item
                        label={<span style={{ color: "#9ca3af" }}>Email hệ thống</span>}
                        name="email"
                      >
                        <Input
                          disabled
                          prefix={<MailOutlined style={{ color: "#4b5563" }} />}
                        />
                      </Form.Item>

                      <Button
                        type="primary"
                        htmlType="submit"
                        loading={saving}
                        icon={<SaveOutlined />}
                        style={{ background: "#4f46e5", border: "none", marginTop: 8 }}
                      >
                        Cập nhật hồ sơ
                      </Button>
                    </Form>
                  ),
                },

                {
                  key: "2",
                  label: "Đổi mật khẩu",
                  children: (
                    <Form
                      form={passwordForm}
                      layout="vertical"
                      onFinish={changePassword}
                      style={{ marginTop: 16 }}
                    >
                      <Form.Item
                        label={<span style={{ color: "#9ca3af" }}>Mật khẩu cũ</span>}
                        name="old_password"
                        rules={[{ required: true, message: "Nhập mật khẩu cũ" }]}
                      >
                        <Input.Password
                          prefix={<LockOutlined style={{ color: "#6b7280" }} />}
                          style={{ background: "#1f2937", color: "#fff", border: "1px solid #374151" }}
                        />
                      </Form.Item>

                      <Form.Item
                        label={<span style={{ color: "#9ca3af" }}>Mật khẩu mới</span>}
                        name="new_password"
                        rules={[
                          { required: true, message: "Nhập mật khẩu mới" },
                          { min: 6, message: "Ít nhất 6 ký tự" },
                        ]}
                      >
                        <Input.Password
                          prefix={<LockOutlined style={{ color: "#6b7280" }} />}
                          style={{ background: "#1f2937", color: "#fff", border: "1px solid #374151" }}
                        />
                      </Form.Item>

                      <Form.Item
                        label={<span style={{ color: "#9ca3af" }}>Xác nhận mật khẩu mới</span>}
                        name="confirm_password"
                        dependencies={["new_password"]}
                        rules={[
                          { required: true, message: "Xác nhận mật khẩu" },
                          ({ getFieldValue }) => ({
                            validator(_, value) {
                              if (!value || getFieldValue("new_password") === value) {
                                return Promise.resolve();
                              }
                              return Promise.reject(new Error("Mật khẩu không khớp"));
                            },
                          }),
                        ]}
                      >
                        <Input.Password
                          prefix={<LockOutlined style={{ color: "#6b7280" }} />}
                          style={{ background: "#1f2937", color: "#fff", border: "1px solid #374151" }}
                        />
                      </Form.Item>

                      <Button
                        type="primary"
                        htmlType="submit"
                        loading={saving}
                        style={{ background: "#4f46e5", border: "none", marginTop: 8 }}
                      >
                        Đổi mật khẩu
                      </Button>
                    </Form>
                  ),
                },
              ]}
            />
          </Col>
        </Row>
      </Card>
    </div>
  );
}

export default function Profile() {
  return (
    <App>
      <ProfileContent />
    </App>
  );
}