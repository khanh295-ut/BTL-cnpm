import React, { useState } from "react";
import {
  Card,
  Form,
  Input,
  Button,
  Typography,
  message,
} from "antd";
import {
  UserOutlined,
  MailOutlined,
  LockOutlined,
  IdcardOutlined,
  UserAddOutlined,
} from "@ant-design/icons";
import { Link, useNavigate } from "react-router-dom";
import authApi from "../api/authApi";

const { Title, Text } = Typography;

const Register = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values) => {
    try {
      setLoading(true);

      await authApi.register({
        username: values.username,
        full_name: values.full_name,
        email: values.email,
        password: values.password,
      });

      message.success("Đăng ký tài khoản thành công!");
      navigate("/login");
    } catch (err) {
      console.error(err);
      if (!err.response) {
        message.error("Không thể kết nối tới máy chủ.");
      } else {
        message.error(
          err.response.data?.detail || "Đăng ký thất bại."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        // ĐÃ SỬA: Thay thế gradient sáng bằng màu đen sâu huyền bí đồng bộ hệ thống
        background: "#090d16",
        padding: 20,
      }}
    >
      {/* ĐÃ THÊM: Tiêm CSS Style nhuộm Dark UI tinh tế cho Form Item Label và Input nội bộ */}
      <style>{`
        .dark-form .ant-form-item-label > label {
          color: #9ca3af !important;
        }
        .dark-input {
          background-color: #1f2937 !important;
          border-color: #374151 !important;
          color: #fff !important;
        }
        .dark-input .ant-input {
          background-color: transparent !important;
          color: #fff !important;
        }
        .dark-input .ant-input-prefix {
          color: #6b7280 !important;
        }
      `}</style>

      {/* ĐÃ SỬA: Đổi màu nền Card sang màu tối đậm đà #111827 */}
      <Card
        bordered={false}
        style={{
          width: 500,
          borderRadius: 16,
          background: "#111827",
          border: "1px solid #1f2937",
          boxShadow: "0 20px 50px rgba(0,0,0,.4)",
        }}
      >
        <div style={{ textAlign: "center", marginBottom: 30 }}>
          {/* ĐÃ SỬA: Ép tiêu đề sang màu trắng */}
          <Title level={2} style={{ color: "#fff", margin: 0, fontWeight: 700, letterSpacing: "0.5px" }}>
            AI TASKER
          </Title>
          <Text style={{ color: "#9ca3af", marginTop: 4, display: "block" }}>
            Tạo tài khoản mới
          </Text>
        </div>

        <Form
          layout="vertical"
          onFinish={onFinish}
          autoComplete="on"
          className="dark-form"
        >
          <Form.Item
            label="Họ và tên"
            name="full_name"
            rules={[{ required: true, message: "Nhập họ và tên." }]}
          >
            <Input
              size="large"
              className="dark-input"
              prefix={<IdcardOutlined />}
              autoComplete="name"
            />
          </Form.Item>

          <Form.Item
            label="Tên đăng nhập"
            name="username"
            rules={[
              { required: true, message: "Nhập tên đăng nhập." },
              { min: 3, message: "Ít nhất 3 ký tự." },
            ]}
          >
            <Input
              size="large"
              className="dark-input"
              prefix={<UserOutlined />}
              autoComplete="username"
            />
          </Form.Item>

          <Form.Item
            label="Email"
            name="email"
            rules={[
              { required: true, message: "Nhập email." },
              { type: "email", message: "Email không hợp lệ." },
            ]}
          >
            <Input
              size="large"
              className="dark-input"
              prefix={<MailOutlined />}
              autoComplete="email"
            />
          </Form.Item>

          <Form.Item
            label="Mật khẩu"
            name="password"
            rules={[
              { required: true, message: "Nhập mật khẩu." },
              { min: 6, message: "Mật khẩu tối thiểu 6 ký tự." },
            ]}
          >
            <Input.Password
              size="large"
              className="dark-input"
              prefix={<LockOutlined />}
              autoComplete="new-password"
            />
          </Form.Item>

          <Form.Item
            label="Xác nhận mật khẩu"
            name="confirm_password"
            dependencies={["password"]}
            rules={[
              { required: true, message: "Xác nhận mật khẩu." },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || value === getFieldValue("password")) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error("Mật khẩu xác nhận không khớp."));
                },
              }),
            ]}
          >
            <Input.Password
              size="large"
              className="dark-input"
              prefix={<LockOutlined />}
              autoComplete="new-password"
            />
          </Form.Item>

          <Button
            type="primary"
            htmlType="submit"
            block
            size="large"
            loading={loading}
            icon={<UserAddOutlined />}
            style={{ background: "#4f46e5", border: "none", height: 45, marginTop: 10 }}
          >
            Đăng ký
          </Button>
        </Form>

        <div style={{ textAlign: "center", marginTop: 24 }}>
          <Text style={{ color: "#9ca3af" }}>
            Đã có tài khoản?
          </Text>
          <br />
          {/* ĐÃ SỬA: Đổi màu đường dẫn Link sang mã màu Indigo sáng nhẹ */}
          <Link to="/login" style={{ color: "#818cf8", fontWeight: 500, display: "inline-block", marginTop: 4 }}>
            Đăng nhập ngay
          </Link>
        </div>
      </Card>
    </div>
  );
};

export default Register;