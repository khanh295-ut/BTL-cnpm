import React, { useEffect, useState } from "react";
import {
  Card,
  Table,
  Tag,
  Typography,
  Button,
  Input,
  App as AntdApp,
  Spin,
} from "antd";
import {
  CreditCardOutlined,
  ReloadOutlined,
  SearchOutlined,
} from "@ant-design/icons";

// ĐÃ SỬA: Dùng axiosClient chung thay vì gọi axios thuần bị hardcode URL
import axiosClient from "../api/axiosClient";

const { Title, Text } = Typography;
const { Search } = Input;

const PaymentListContent = () => {
  const { message } = AntdApp.useApp();

  const [payments, setPayments] = useState([]);
  const [filteredPayments, setFilteredPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchText, setSearchText] = useState("");

  useEffect(() => {
    loadPayments();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    let list = [...payments];
    if (searchText) {
      const keyword = searchText.toLowerCase();
      list = list.filter(
        (item) =>
          String(item.id || item.transaction_id || "").toLowerCase().includes(keyword) ||
          String(item.description || "").toLowerCase().includes(keyword) ||
          String(item.type || "").toLowerCase().includes(keyword)
      );
    }
    setFilteredPayments(list);
  }, [payments, searchText]);

  const loadPayments = async () => {
    try {
      setLoading(true);
      
      // ĐÃ SỬA: Đi qua axiosClient thì chỉ cần endpoint `/payments` ngắn gọn
      const response = await axiosClient.get("/payments");

      const data = response.data?.data || response.data?.results || response.data || [];
      const list = Array.isArray(data) ? data : [];
      setPayments(list);
      setFilteredPayments(list);
    } catch (error) {
      console.error("[API Error Trace]:", error.response || error);
      
      const mockData = [
        { id: "TXN-9921", amount: 15000000, type: "Deposit", description: "Doanh nghiệp VinAI nạp tiền cọc dự án NLP", created_at: new Date().toISOString(), status: "SUCCESS" },
        { id: "TXN-8842", amount: 4500000, type: "Withdraw", description: "Thanh toán giải ngân cho Expert Nguyễn Văn A", created_at: new Date().toISOString(), status: "SUCCESS" },
        { id: "TXN-1102", amount: 2000000, type: "Deposit", description: "Nạp thử nghiệm cổng Sandbox", created_at: new Date().toISOString(), status: "PENDING" }
      ];
      setPayments(mockData);
      setFilteredPayments(mockData);

      message.warning(`Không kết nối được Backend. Đang hiển thị dữ liệu mẫu!`);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { 
      title: "STT", 
      width: 70, 
      align: "center", 
      render: (_, __, index) => <Text style={{ color: "#fff" }}>{index + 1}</Text> 
    },
    {
      title: "Mã giao dịch",
      key: "id",
      // ĐÃ SỬA: Đổi màu mã giao dịch sang màu Indigo sáng để nổi bật trên nền tối
      render: (_, record) => <Text strong style={{ color: "#818cf8" }}>#{record.id || record.transaction_id || "N/A"}</Text>,
    },
    {
      title: "Số tiền",
      dataIndex: "amount",
      render: (val) => <Text style={{ color: "#fff" }}>{Number(val || 0).toLocaleString("vi-VN", { style: "currency", currency: "VND" })}</Text>,
    },
    {
      title: "Loại giao dịch",
      dataIndex: "type",
      render: (type) => type === "Deposit" ? <Tag color="blue">Doanh nghiệp đặt cọc</Tag> : <Tag color="purple">Giải ngân Chuyên gia</Tag>,
    },
    { 
      title: "Nội dung", 
      dataIndex: "description",
      render: (text) => <Text style={{ color: "#9ca3af" }}>{text}</Text>
    },
    {
      title: "Thời gian",
      render: (_, record) => <Text style={{ color: "#9ca3af" }}>{record.created_at ? new Date(record.created_at).toLocaleString("vi-VN") : "-"}</Text>,
    },
    {
      title: "Trạng thái",
      dataIndex: "status",
      align: "center",
      render: (status) => {
        const s = String(status || "").toUpperCase();
        return <Tag color={s === "SUCCESS" ? "green" : s === "PENDING" ? "orange" : "red"}>{status}</Tag>;
      },
    },
  ];

  return (
    <div style={{ padding: "24px", background: "#090d16", minHeight: "100vh" }}>
      
      {/* ĐÃ THÊM: Tiêm CSS Style để xử lý hoàn toàn Dark Mode cho Table */}
      <style>{`
        /* Tiêu đề cột (Header) */
        .ant-table-thead > tr > th {
          background: #1f2937 !important;
          color: #fff !important;
          border-bottom: 1px solid #374151 !important;
        }
        /* Dòng dữ liệu (Body Rows) */
        .ant-table-tbody > tr > td {
          background: #111827 !important;
          border-bottom: 1px solid #1f2937 !important;
        }
        /* Hiệu ứng Hover dòng */
        .ant-table-tbody > tr:hover > td {
          background: #1f2937 !important;
        }
        /* Khung viền tổng của table */
        .ant-table {
          border: 1px solid #1f2937 !important;
          background: #111827 !important;
        }
        /* Phân trang (Pagination) */
        .ant-pagination-item a, .ant-pagination-item-link {
          color: #fff !important;
        }
        .ant-pagination-item-active {
          background: #4f46e5 !important;
          border-color: #4f46e5 !important;
        }
        /* Thanh Search Input */
        .ant-input-search .ant-input {
          background: #1f2937 !important;
          color: #fff !important;
        }
        .ant-input-affix-wrapper {
          background: #1f2937 !important;
          border: 1px solid #374151 !important;
        }
        .ant-input-clear-icon {
          color: #9ca3af !important;
        }
      `}</style>

      {/* ĐÃ SỬA: Áp dụng nền tối cho Card */}
      <Card style={{ background: "#111827", border: "1px solid #1f2937", borderRadius: 12, padding: "8px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
          <div>
            {/* ĐÃ SỬA: Ép chữ sang màu trắng */}
            <Title level={3} style={{ margin: 0, color: "#fff" }}>
              <CreditCardOutlined style={{ marginRight: 8 }} /> Lịch sử giao dịch
            </Title>
          </div>
          <Button 
            ghost 
            icon={<ReloadOutlined />} 
            onClick={loadPayments} 
            style={{ color: "#9ca3af", borderColor: "#374151" }}
          >
            Làm mới
          </Button>
        </div>

        <Search 
          allowClear 
          placeholder="Tìm kiếm..." 
          prefix={<SearchOutlined style={{ color: "#6b7280" }} />} 
          style={{ width: 350, marginBottom: 20 }} 
          onChange={(e) => setSearchText(e.target.value)} 
        />

        {loading ? (
          <div style={{ textAlign: "center", padding: 60 }}>
            {/* ĐÃ SỬA: Bọc Spin bằng chữ sáng màu */}
            <Spin size="large" tip={<span style={{ color: "#9ca3af", marginTop: 8, display: "block" }}>Hệ thống đang truy xuất dữ liệu...</span>} />
          </div>
        ) : (
          <Table 
            columns={columns} 
            dataSource={filteredPayments} 
            rowKey={(r) => r.id || Math.random()} 
            pagination={{ pageSize: 8 }} 
          />
        )}
      </Card>
    </div>
  );
};

const PaymentList = () => (
  <AntdApp>
    <PaymentListContent />
  </AntdApp>
);

export default PaymentList;