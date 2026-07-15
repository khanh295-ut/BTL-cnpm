import axios from "axios";


const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL
  || "http://127.0.0.1:8000/api"
);


const axiosClient = axios.create({
  baseURL: API_BASE_URL,

  // Gemini hoặc các tác vụ AI có thể xử lý lâu.
  timeout: 90000,

  // Cho phép gửi cookie session tới FastAPI.
  withCredentials: true,

  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});


// ==========================================================
// STORAGE KEYS
// ==========================================================

const ACCESS_TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";
const USER_KEY = "auth_user";


// ==========================================================
// REQUEST INTERCEPTOR
// ==========================================================

axiosClient.interceptors.request.use(
  (config) => {
    const accessToken = localStorage.getItem(
      ACCESS_TOKEN_KEY
    );

    if (accessToken) {
      config.headers = config.headers ?? {};

      config.headers.Authorization =
        `Bearer ${accessToken}`;
    }

    return config;
  },

  (error) => {
    return Promise.reject(error);
  }
);


// ==========================================================
// CLEAR AUTHENTICATION
// ==========================================================

const clearAuthentication = () => {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USER_KEY);

  // Xóa dữ liệu đăng nhập giả lập cũ.
  localStorage.removeItem("token");
  localStorage.removeItem("isAdmin");
  localStorage.removeItem("username");
};


// ==========================================================
// RESPONSE INTERCEPTOR
// ==========================================================

axiosClient.interceptors.response.use(
  (response) => {
    return response;
  },

  (error) => {
    if (error.code === "ECONNABORTED") {
      error.message = (
        "Yêu cầu xử lý quá thời gian. "
        + "Vui lòng thử lại."
      );

      return Promise.reject(error);
    }

    if (!error.response) {
      error.message = (
        "Không thể kết nối tới backend. "
        + "Hãy kiểm tra FastAPI đang chạy tại "
        + API_BASE_URL
        + "."
      );

      return Promise.reject(error);
    }

    const status = error.response.status;

    const backendMessage = (
      error.response.data?.message
      || error.response.data?.detail
    );

    if (backendMessage) {
      error.message = backendMessage;
    }

    if (status === 401) {
      const currentPath = window.location.pathname;

      clearAuthentication();

      const publicPaths = [
        "/login",
        "/register",
        "/forgot-password",
      ];

      if (!publicPaths.includes(currentPath)) {
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);


export {
  API_BASE_URL,
  clearAuthentication,
};

export default axiosClient;