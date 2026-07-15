import React, {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
} from "react";

import {
  BrowserRouter,
  Link,
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from "react-router-dom";

import {
  App as AntdApp,
  Button,
  Card,
  Checkbox,
  ConfigProvider,
  Divider,
  Form,
  Input,
  Select,
  Typography,
  theme,
} from "antd";

import {
  ArrowLeftOutlined,
  LockOutlined,
  MailOutlined,
  SafetyCertificateOutlined,
  UserAddOutlined,
  UserOutlined,
} from "@ant-design/icons";

import axiosClient from "./api/axiosClient";

import MainLayout from "./layouts/MainLayout";

import AIServiceDetail from "./pages/AIServiceDetail";
import AIServiceList from "./pages/AIServiceList";
import Analytics from "./pages/Analytics";
import ContractsEscrow from "./pages/ContractsEscrow";
import CreateAIService from "./pages/CreateAIService";
import CreateServiceOrder from "./pages/CreateServiceOrder";
import Dashboard from "./pages/Dashboard";
import EnterpriseChatbot from "./pages/EnterpriseChatbot";
import EnterpriseList from "./pages/EnterpriseList";
import ExpertList from "./pages/ExpertList";
import JobAssistant from "./pages/JobAssistant";
import PaymentList from "./pages/PaymentList";
import Profile from "./pages/Profile";
import ProjectList from "./pages/ProjectList";
import ProposalList from "./pages/ProposalList";
import ServiceOrderDetail from "./pages/ServiceOrderDetail";
import Settings from "./pages/Settings";

const { Title, Text, Paragraph } = Typography;

// ==========================================================
// STORAGE KEYS
// ==========================================================

const ACCESS_TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";
const USER_KEY = "auth_user";

// ==========================================================
// AUTH STORAGE HELPERS
// ==========================================================

const readStoredUser = () => {
  try {
    const rawUser = localStorage.getItem(USER_KEY);

    if (!rawUser) {
      return null;
    }

    return JSON.parse(rawUser);
  } catch {
    localStorage.removeItem(USER_KEY);
    return null;
  }
};

const getStoredAccessToken = () =>
  localStorage.getItem(ACCESS_TOKEN_KEY);

const saveAuthentication = ({
  accessToken,
  refreshToken,
  user,
}) => {
  if (accessToken) {
    localStorage.setItem(
      ACCESS_TOKEN_KEY,
      accessToken
    );
  }

  if (refreshToken) {
    localStorage.setItem(
      REFRESH_TOKEN_KEY,
      refreshToken
    );
  }

  if (user) {
    localStorage.setItem(
      USER_KEY,
      JSON.stringify(user)
    );
  }
};

const clearAuthentication = () => {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USER_KEY);

  // Dữ liệu cũ của bản đăng nhập giả lập.
  localStorage.removeItem("token");
  localStorage.removeItem("isAdmin");
  localStorage.removeItem("username");
};

// ==========================================================
// API RESPONSE HELPERS
// ==========================================================

const normalizeLoginResponse = (responseData) => {
  const payload =
    responseData?.data ??
    responseData ??
    {};

  const accessToken =
    payload.access_token ??
    payload.accessToken ??
    payload.token ??
    null;

  const refreshToken =
    payload.refresh_token ??
    payload.refreshToken ??
    null;

  const user =
    payload.user ??
    payload.account ??
    payload.profile ??
    null;

  return {
    accessToken,
    refreshToken,
    user,
  };
};

const getErrorMessage = (
  error,
  fallbackMessage = "Đã xảy ra lỗi."
) => {
  const backendMessage =
    error?.response?.data?.message;

  const detail =
    error?.response?.data?.detail;

  if (typeof backendMessage === "string") {
    return backendMessage;
  }

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        if (typeof item === "string") {
          return item;
        }

        if (item && typeof item.msg === "string") {
          const location = Array.isArray(item.loc)
            ? item.loc
                .filter((part) => part !== "body")
                .join(".")
            : "";

          return location
            ? `${location}: ${item.msg}`
            : item.msg;
        }

        return null;
      })
      .filter(Boolean);

    if (messages.length > 0) {
      return messages.join(", ");
    }
  }

  if (typeof error?.message === "string") {
    return error.message;
  }

  return fallbackMessage;
};

// ==========================================================
// AUTH CONTEXT
// ==========================================================

const AuthContext = createContext(null);

const useAuth = () => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth phải được sử dụng bên trong AuthProvider."
    );
  }

  return context;
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(
    readStoredUser
  );

  const [token, setToken] = useState(
    getStoredAccessToken
  );

  const login = useCallback(
    ({
      accessToken,
      refreshToken,
      user: authenticatedUser,
    }) => {
      saveAuthentication({
        accessToken,
        refreshToken,
        user: authenticatedUser,
      });

      setToken(accessToken);
      setUser(authenticatedUser);
    },
    []
  );

  const logout = useCallback(() => {
    clearAuthentication();
    setToken(null);
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({
      user,
      token,
      isAuthenticated: Boolean(token),
      login,
      logout,
      setUser,
    }),
    [
      user,
      token,
      login,
      logout,
    ]
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// ==========================================================
// ROUTE GUARDS
// ==========================================================

const PrivateRoute = ({ children }) => {
  const location = useLocation();
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
        state={{
          from: location.pathname,
        }}
      />
    );
  }

  return children;
};

const PublicRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();

  if (isAuthenticated) {
    return (
      <Navigate
        to="/dashboard"
        replace
      />
    );
  }

  return children;
};

// ==========================================================
// AUTH PAGE LAYOUT
// ==========================================================

const AuthPage = ({
  title,
  subtitle,
  icon,
  children,
}) => {
  return (
    <div
      style={{
        width: "100%",
        minHeight: "100vh",
        padding: 20,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background:
          "radial-gradient("
          + "circle at top right, "
          + "rgba(79, 70, 229, 0.25), "
          + "transparent 35%"
          + "), "
          + "radial-gradient("
          + "circle at bottom left, "
          + "rgba(14, 165, 233, 0.14), "
          + "transparent 38%"
          + "), "
          + "#090d16",
      }}
    >
      <Card
        variant="outlined"
        style={{
          width: "min(460px, 100%)",
          borderRadius: 20,
          border:
            "1px solid rgba(255,255,255,0.09)",
          background: "#111827",
          boxShadow:
            "0 24px 80px rgba(0,0,0,0.5)",
        }}
        styles={{
          body: {
            padding: 32,
          },
        }}
      >
        <div
          style={{
            textAlign: "center",
            marginBottom: 28,
          }}
        >
          <div
            style={{
              width: 56,
              height: 56,
              margin: "0 auto 16px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              borderRadius: 16,
              fontSize: 26,
              color: "#ffffff",
              background:
                "linear-gradient(135deg, #4f46e5, #7c3aed)",
              boxShadow:
                "0 12px 30px rgba(79,70,229,0.35)",
            }}
          >
            {icon}
          </div>

          <Title
            level={3}
            style={{
              marginBottom: 8,
              color: "#ffffff",
            }}
          >
            {title}
          </Title>

          <Text type="secondary">
            {subtitle}
          </Text>
        </div>

        {children}
      </Card>
    </div>
  );
};

// ==========================================================
// LOGIN PAGE
// ==========================================================

const LoginPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const { message } = AntdApp.useApp();

  const [loading, setLoading] = useState(false);

  const handleLogin = async (values) => {
    setLoading(true);

    const messageKey = "login";

    message.loading({
      content: "Đang xác thực tài khoản...",
      key: messageKey,
      duration: 0,
    });

    try {
      const loginValue =
        values.login.trim();

      const response = await axiosClient.post(
        "/auth/login",
        {
          login: loginValue,
          password: values.password,
        }
      );

      const authData = normalizeLoginResponse(
        response.data
      );

      if (!authData.accessToken) {
        throw new Error(
          "Backend không trả về access token."
        );
      }

      const fallbackUser = {
        username: loginValue,
        email: loginValue.includes("@")
          ? loginValue
          : null,
      };

      login({
        accessToken: authData.accessToken,
        refreshToken: authData.refreshToken,
        user: authData.user ?? fallbackUser,
      });

      message.success({
        content: "Đăng nhập thành công!",
        key: messageKey,
        duration: 3,
      });

      const destination =
        location.state?.from ??
        "/dashboard";

      navigate(destination, {
        replace: true,
      });
    } catch (error) {
      message.error({
        content: getErrorMessage(
          error,
          "Đăng nhập thất bại."
        ),
        key: messageKey,
        duration: 5,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthPage
      title="AI TASKER"
      subtitle="Đăng nhập để sử dụng nền tảng AI Marketplace"
      icon={<SafetyCertificateOutlined />}
    >
      <Form
        layout="vertical"
        onFinish={handleLogin}
        autoComplete="on"
        requiredMark
      >
        <Form.Item
          name="login"
          label="Tài khoản hoặc email"
          rules={[
            {
              required: true,
              message:
                "Vui lòng nhập tài khoản hoặc email.",
            },
          ]}
        >
          <Input
            prefix={<UserOutlined />}
            placeholder="Nhập tài khoản hoặc email"
            size="large"
            autoComplete="username"
          />
        </Form.Item>

        <Form.Item
          name="password"
          label="Mật khẩu"
          rules={[
            {
              required: true,
              message:
                "Vui lòng nhập mật khẩu.",
            },
            {
              min: 6,
              message:
                "Mật khẩu phải có ít nhất 6 ký tự.",
            },
          ]}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="Nhập mật khẩu"
            size="large"
            autoComplete="current-password"
          />
        </Form.Item>

        <div
          style={{
            marginTop: -10,
            marginBottom: 20,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 12,
          }}
        >
          <Form.Item
            name="remember"
            valuePropName="checked"
            noStyle
          >
            <Checkbox>
              Ghi nhớ đăng nhập
            </Checkbox>
          </Form.Item>

          <Link to="/forgot-password">
            Quên mật khẩu?
          </Link>
        </div>

        <Button
          type="primary"
          htmlType="submit"
          size="large"
          loading={loading}
          block
          style={{
            fontWeight: 700,
          }}
        >
          ĐĂNG NHẬP
        </Button>
      </Form>

      <Divider plain>
        Hoặc
      </Divider>

      <div
        style={{
          textAlign: "center",
        }}
      >
        <Text type="secondary">
          Chưa có tài khoản?{" "}
        </Text>

        <Link
          to="/register"
          style={{
            fontWeight: 700,
          }}
        >
          Đăng ký ngay
        </Link>
      </div>
    </AuthPage>
  );
};

// ==========================================================
// REGISTER PAGE
// ==========================================================

const RegisterPage = () => {
  const navigate = useNavigate();
  const { message } = AntdApp.useApp();

  const [loading, setLoading] = useState(false);

  const handleRegister = async (values) => {
    setLoading(true);

    const messageKey = "register";

    message.loading({
      content: "Đang tạo tài khoản...",
      key: messageKey,
      duration: 0,
    });

    try {
      await axiosClient.post(
        "/auth/register",
        {
          full_name: values.fullName.trim(),
          username: values.username.trim(),
          email: values.email.trim().toLowerCase(),
          password: values.password,
          role: values.role.toUpperCase(),
        }
      );

      message.success({
        content:
          "Đăng ký thành công. Hãy đăng nhập!",
        key: messageKey,
        duration: 4,
      });

      navigate("/login", {
        replace: true,
      });
    } catch (error) {
      message.error({
        content: getErrorMessage(
          error,
          "Không thể đăng ký tài khoản."
        ),
        key: messageKey,
        duration: 5,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthPage
      title="TẠO TÀI KHOẢN"
      subtitle="Tham gia nền tảng kết nối doanh nghiệp và chuyên gia AI"
      icon={<UserAddOutlined />}
    >
      <Form
        layout="vertical"
        onFinish={handleRegister}
        autoComplete="off"
        initialValues={{
          role: "ENTERPRISE",
        }}
      >
        <Form.Item
          name="fullName"
          label="Họ và tên"
          rules={[
            {
              required: true,
              message:
                "Vui lòng nhập họ và tên.",
            },
            {
              min: 2,
              message:
                "Họ và tên phải có ít nhất 2 ký tự.",
            },
          ]}
        >
          <Input
            prefix={<UserOutlined />}
            placeholder="Nhập họ và tên"
            size="large"
          />
        </Form.Item>

        <Form.Item
          name="username"
          label="Tên đăng nhập"
          rules={[
            {
              required: true,
              message:
                "Vui lòng nhập tên đăng nhập.",
            },
            {
              min: 3,
              message:
                "Tên đăng nhập phải có ít nhất 3 ký tự.",
            },
          ]}
        >
          <Input
            prefix={<UserOutlined />}
            placeholder="Nhập tên đăng nhập"
            size="large"
            autoComplete="username"
          />
        </Form.Item>

        <Form.Item
          name="email"
          label="Email"
          rules={[
            {
              required: true,
              message:
                "Vui lòng nhập email.",
            },
            {
              type: "email",
              message:
                "Email không đúng định dạng.",
            },
          ]}
        >
          <Input
            prefix={<MailOutlined />}
            placeholder="example@gmail.com"
            size="large"
            autoComplete="email"
          />
        </Form.Item>

        <Form.Item
          name="role"
          label="Loại tài khoản"
          rules={[
            {
              required: true,
              message:
                "Vui lòng chọn loại tài khoản.",
            },
          ]}
        >
          <Select
            size="large"
            options={[
              {
                value: "ENTERPRISE",
                label: "Doanh nghiệp",
              },
              {
                value: "EXPERT",
                label: "Chuyên gia AI",
              },
            ]}
          />
        </Form.Item>

        <Form.Item
          name="password"
          label="Mật khẩu"
          rules={[
            {
              required: true,
              message:
                "Vui lòng nhập mật khẩu.",
            },
            {
              min: 6,
              message:
                "Mật khẩu phải có ít nhất 6 ký tự.",
            },
          ]}
          hasFeedback
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="Nhập mật khẩu"
            size="large"
            autoComplete="new-password"
          />
        </Form.Item>

        <Form.Item
          name="confirmPassword"
          label="Xác nhận mật khẩu"
          dependencies={["password"]}
          hasFeedback
          rules={[
            {
              required: true,
              message:
                "Vui lòng xác nhận mật khẩu.",
            },
            ({ getFieldValue }) => ({
              validator(_, value) {
                if (
                  !value ||
                  getFieldValue("password") === value
                ) {
                  return Promise.resolve();
                }

                return Promise.reject(
                  new Error(
                    "Mật khẩu xác nhận không khớp."
                  )
                );
              },
            }),
          ]}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="Nhập lại mật khẩu"
            size="large"
            autoComplete="new-password"
          />
        </Form.Item>

        <Form.Item
          name="acceptTerms"
          valuePropName="checked"
          rules={[
            {
              validator: (_, value) =>
                value
                  ? Promise.resolve()
                  : Promise.reject(
                      new Error(
                        "Bạn phải đồng ý với điều khoản."
                      )
                    ),
            },
          ]}
        >
          <Checkbox>
            Tôi đồng ý với điều khoản sử dụng
            và chính sách bảo mật
          </Checkbox>
        </Form.Item>

        <Button
          type="primary"
          htmlType="submit"
          size="large"
          loading={loading}
          block
          style={{
            fontWeight: 700,
          }}
        >
          ĐĂNG KÝ
        </Button>
      </Form>

      <div
        style={{
          marginTop: 22,
          textAlign: "center",
        }}
      >
        <Text type="secondary">
          Đã có tài khoản?{" "}
        </Text>

        <Link
          to="/login"
          style={{
            fontWeight: 700,
          }}
        >
          Đăng nhập
        </Link>
      </div>
    </AuthPage>
  );
};

// ==========================================================
// FORGOT PASSWORD PAGE
// ==========================================================

const ForgotPasswordPage = () => {
  const { message } = AntdApp.useApp();

  const [loading, setLoading] = useState(false);
  const [submittedEmail, setSubmittedEmail] =
    useState("");

  const handleSubmit = async (values) => {
    setLoading(true);

    const messageKey = "forgot-password";

    message.loading({
      content:
        "Đang gửi yêu cầu đặt lại mật khẩu...",
      key: messageKey,
      duration: 0,
    });

    try {
      await axiosClient.post(
        "/auth/forgot-password",
        {
          email: values.email
            .trim()
            .toLowerCase(),
        }
      );

      setSubmittedEmail(
        values.email
          .trim()
          .toLowerCase()
      );

      message.success({
        content:
          "Yêu cầu đặt lại mật khẩu đã được gửi.",
        key: messageKey,
        duration: 5,
      });
    } catch (error) {
      message.error({
        content: getErrorMessage(
          error,
          "Không thể gửi yêu cầu đặt lại mật khẩu."
        ),
        key: messageKey,
        duration: 5,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthPage
      title="QUÊN MẬT KHẨU"
      subtitle="Nhập email để nhận hướng dẫn đặt lại mật khẩu"
      icon={<MailOutlined />}
    >
      {submittedEmail ? (
        <div
          style={{
            textAlign: "center",
          }}
        >
          <Paragraph>
            Hệ thống đã tiếp nhận yêu cầu cho:
          </Paragraph>

          <Text
            strong
            style={{
              display: "block",
              marginBottom: 20,
            }}
          >
            {submittedEmail}
          </Text>

          <Paragraph type="secondary">
            Hãy kiểm tra hộp thư đến và thư mục
            spam để tiếp tục.
          </Paragraph>

          <Link to="/login">
            <ArrowLeftOutlined /> Quay lại đăng nhập
          </Link>
        </div>
      ) : (
        <>
          <Form
            layout="vertical"
            onFinish={handleSubmit}
          >
            <Form.Item
              name="email"
              label="Email tài khoản"
              rules={[
                {
                  required: true,
                  message:
                    "Vui lòng nhập email.",
                },
                {
                  type: "email",
                  message:
                    "Email không đúng định dạng.",
                },
              ]}
            >
              <Input
                prefix={<MailOutlined />}
                placeholder="example@gmail.com"
                size="large"
                autoComplete="email"
              />
            </Form.Item>

            <Button
              type="primary"
              htmlType="submit"
              size="large"
              loading={loading}
              block
              style={{
                fontWeight: 700,
              }}
            >
              GỬI YÊU CẦU
            </Button>
          </Form>

          <div
            style={{
              marginTop: 22,
              textAlign: "center",
            }}
          >
            <Link to="/login">
              <ArrowLeftOutlined /> Quay lại đăng nhập
            </Link>
          </div>
        </>
      )}
    </AuthPage>
  );
};

// ==========================================================
// PROTECTED PAGE WRAPPER
// ==========================================================

const ProtectedPage = ({ children }) => {
  return (
    <PrivateRoute>
      <MainLayout>
        {children}
      </MainLayout>
    </PrivateRoute>
  );
};

// ==========================================================
// CHATBOT VISIBILITY
// ==========================================================

const ChatbotController = () => {
  const location = useLocation();
  const { isAuthenticated } = useAuth();

  const hiddenPaths = [
    "/login",
    "/register",
    "/forgot-password",
  ];

  if (
    !isAuthenticated ||
    hiddenPaths.includes(location.pathname)
  ) {
    return null;
  }

  return <EnterpriseChatbot />;
};

// ==========================================================
// APPLICATION ROUTES
// ==========================================================

const ApplicationRoutes = () => {
  return (
    <>
      <Routes>
        <Route
          path="/login"
          element={
            <PublicRoute>
              <LoginPage />
            </PublicRoute>
          }
        />

        <Route
          path="/register"
          element={
            <PublicRoute>
              <RegisterPage />
            </PublicRoute>
          }
        />

        <Route
          path="/forgot-password"
          element={
            <PublicRoute>
              <ForgotPasswordPage />
            </PublicRoute>
          }
        />

        <Route
          path="/"
          element={
            <Navigate
              to="/dashboard"
              replace
            />
          }
        />

        <Route
          path="/dashboard"
          element={
            <ProtectedPage>
              <Dashboard />
            </ProtectedPage>
          }
        />

        <Route
          path="/projects"
          element={
            <ProtectedPage>
              <ProjectList />
            </ProtectedPage>
          }
        />

        <Route
          path="/experts"
          element={
            <ProtectedPage>
              <ExpertList />
            </ProtectedPage>
          }
        />

        <Route
          path="/proposals"
          element={
            <ProtectedPage>
              <ProposalList />
            </ProtectedPage>
          }
        />

        <Route
          path="/contracts"
          element={
            <ProtectedPage>
              <ContractsEscrow />
            </ProtectedPage>
          }
        />

        <Route
          path="/job-assistant"
          element={
            <ProtectedPage>
              <JobAssistant />
            </ProtectedPage>
          }
        />

        <Route
          path="/ai-services"
          element={
            <ProtectedPage>
              <AIServiceList />
            </ProtectedPage>
          }
        />

        <Route
          path="/ai-services/create"
          element={
            <ProtectedPage>
              <CreateAIService />
            </ProtectedPage>
          }
        />

        <Route
          path="/ai-services/:slug"
          element={
            <ProtectedPage>
              <AIServiceDetail />
            </ProtectedPage>
          }
        />

        <Route
          path="/service-orders/create"
          element={
            <ProtectedPage>
              <CreateServiceOrder />
            </ProtectedPage>
          }
        />

        <Route
          path="/service-orders/:orderId"
          element={
            <ProtectedPage>
              <ServiceOrderDetail />
            </ProtectedPage>
          }
        />

        <Route
          path="/enterprises"
          element={
            <ProtectedPage>
              <EnterpriseList />
            </ProtectedPage>
          }
        />

        <Route
          path="/payments"
          element={
            <ProtectedPage>
              <PaymentList />
            </ProtectedPage>
          }
        />

        <Route
          path="/analytics"
          element={
            <ProtectedPage>
              <Analytics />
            </ProtectedPage>
          }
        />

        <Route
          path="/profile"
          element={
            <ProtectedPage>
              <Profile />
            </ProtectedPage>
          }
        />

        <Route
          path="/settings"
          element={
            <ProtectedPage>
              <Settings />
            </ProtectedPage>
          }
        />

        <Route
          path="*"
          element={
            <Navigate
              to="/dashboard"
              replace
            />
          }
        />
      </Routes>

      <ChatbotController />
    </>
  );
};

// ==========================================================
// APP
// ==========================================================

function App() {
  return (
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          colorPrimary: "#4f46e5",
          colorBgBase: "#090d16",
          colorBgContainer: "#111827",
          borderRadius: 10,
        },
      }}
    >
      <AntdApp>
        <AuthProvider>
          <BrowserRouter>
            <ApplicationRoutes />
          </BrowserRouter>
        </AuthProvider>
      </AntdApp>
    </ConfigProvider>
  );
}

export default App;
