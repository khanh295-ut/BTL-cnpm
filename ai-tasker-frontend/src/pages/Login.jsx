import React, { useState } from "react";
import {
  Form,
  Input,
  Button,
  Card,
  Checkbox,
  Typography,
  Divider,
  message,
} from "antd";
import {
  MailOutlined,
  LockOutlined,
  LoginOutlined,
} from "@ant-design/icons";
import { Link, useNavigate } from "react-router-dom";
import authApi from "../api/authApi";

const { Title, Text } = Typography;

const Login = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values) => {
    try {
      setLoading(true);

      const response = await authApi.login({
        email: values.email,
        password: values.password,
      });

      const token = response.data?.access_token;

      if (!token) {
        message.error("Máy chủ không trả về Access Token.");
        return;
      }

      localStorage.setItem("token", token);

      if (response.data.user) {
        localStorage.setItem(
          "user",
          JSON.stringify(response.data.user)
        );
      }

      message.success("Đăng nhập thành công!");
      navigate("/dashboard");
    } catch (err) {
      console.error(err);

      if (!err.response) {
        message.error("Không thể kết nối tới máy chủ.");
      } else {
        message.error(
          err.response.data?.detail ||
            "Email hoặc mật khẩu không đúng."
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
        background: "#090d16", // ĐÃ SỬA: Đồng bộ với nền tối sâu của hệ thống
        padding: 20,
      }}
    >
      <Card
        bordered={false}
        style={{
          width: 420,
          borderRadius: 16,
          background: "#111827", // ĐÃ SỬA: Nền Card tối giống ExpertList
          border: "1px solid #1f2937", // ĐÃ THÊM: Viền nhẹ cho Card bớt đơn điệu
          boxShadow: "0 20px 50px rgba(0,0,0,.4)",
        }}
      >
        <div
          style={{
            textAlign: "center",
            marginBottom: 30,
          }}
        >
          {/* ĐÃ SỬA: Màu chữ trắng cho Tên hệ thống */}
          <Title level={2} style={{ marginBottom: 5, color: "#fff", fontWeight: 700, letterSpacing: "1px" }}>
            AI TASKER
          </Title>

          {/* ĐÃ SỬA: Màu xám nhẹ cho phụ đề */}
          <Text style={{ color: "#9ca3af" }}>
            Đăng nhập hệ thống quản lý
          </Text>
        </div>

        <Form
          layout="vertical"
          onFinish={onFinish}
          autoComplete="on"
          requiredMark={false}
        >
          <Form.Item
            label={<span style={{ color: "#9ca3af" }}>Email</span>} // ĐÃ SỬA: Màu Label xám sáng
            name="email"
            rules={[
              {
                required: true,
                message: "Nhập email.",
              },
              {
                type: "email",
                message: "Email không hợp lệ.",
              },
            ]}
          >
            <Input
              size="large"
              prefix={<MailOutlined style={{ color: "#6b7280" }} />}
              placeholder="example@gmail.com"
              autoComplete="email"
              // ĐÃ SỬA: Thiết kế input tối màu
              style={{ background: "#1f2937", color: "#fff", border: "1px solid #374151" }}
            />
          </Form.Item>

          <Form.Item
            label={<span style={{ color: "#9ca3af" }}>Mật khẩu</span>} // ĐÃ SỬA: Màu Label xám sáng
            name="password"
            rules={[
              {
                required: true,
                message: "Nhập mật khẩu.",
              },
            ]}
          >
            <Input.Password
              size="large"
              prefix={<LockOutlined style={{ color: "#6b7280" }} />}
              placeholder="••••••••"
              autoComplete="current-password"
              // ĐÃ SỬA: Thiết kế input tối màu
              style={{ background: "#1f2937", color: "#fff", border: "1px solid #374151" }}
            />
          </Form.Item>

          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 24,
            }}
          >
            {/* ĐÃ SỬA: Màu text Checkbox thành màu xám sáng để không bị nuốt chữ */}
            <Checkbox style={{ color: "#9ca3af" }}>
              Ghi nhớ
            </Checkbox>

            <Link to="/forgot-password" style={{ color: "#6366f1" }}>
              Quên mật khẩu?
            </Link>
          </div>

          <Button
            type="primary"
            htmlType="submit"
            block
            size="large"
            loading={loading}
            icon={<LoginOutlined />}
            style={{ background: "#4f46e5", border: "none", height: 45 }} // ĐÃ SỬA: Tông tím Indigo đồng bộ
          >
            Đăng nhập
          </Button>
        </Form>

        {/* ĐÃ SỬA: Thay đổi màu đường kẻ gạch ngang sang màu tối */}
        <Divider style={{ borderColor: "#1f2937" }} />

        <div style={{ textAlign: "center" }}>
          <Text style={{ color: "#6b7280" }}>
            Chưa có tài khoản?
          </Text>
          {" "}
          <Link to="/register" style={{ color: "#6366f1", fontWeight: 500 }}>
            Đăng ký ngay
          </Link>
        </div>
      </Card>
    </div>
  );
};

export default Login;