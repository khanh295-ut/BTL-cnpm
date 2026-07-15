import React, { useEffect, useState } from "react";
import {
  Table,
  Card,
  Button,
  Modal,
  Form,
  Input,
  InputNumber,
  Space,
  Popconfirm,
  message,
  Typography,
} from "antd";

import {
  PlusOutlined,
  DeleteOutlined,
  EditOutlined,
} from "@ant-design/icons";

import reviewApi from "../api/reviewApi";

const { Text } = Typography;

const ReviewList = () => {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form] = Form.useForm();

  // =====================================
  // Load dữ liệu
  // =====================================
  const fetchReviews = async () => {
    try {
      setLoading(true);
      const res = await reviewApi.getAll();
      setReviews(res.data);
    } catch (err) {
      console.error(err);
      message.error("Không tải được danh sách đánh giá");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReviews();
  }, []);

  // =====================================
  // CREATE / UPDATE
  // =====================================
  const handleFinish = async (values) => {
    try {
      setLoading(true);
      if (editing) {
        await reviewApi.update(editing.id, values);
        message.success("Cập nhật đánh giá thành công");
      } else {
        await reviewApi.create(values);
        message.success("Thêm đánh giá thành công");
      }
      setOpen(false);
      setEditing(null);
      form.resetFields();
      fetchReviews();
    } catch (err) {
      console.error(err);
      message.error("Thao tác thất bại");
    } finally {
      setLoading(false);
    }
  };

  // =====================================
  // DELETE
  // =====================================
  const handleDelete = async (id) => {
    try {
      await reviewApi.delete(id);
      message.success("Đã xóa đánh giá");
      fetchReviews();
    } catch (err) {
      console.error(err);
      message.error("Không thể xóa");
    }
  };

  // =====================================
  // OPEN EDIT
  // =====================================
  const handleEdit = (record) => {
    setEditing(record);
    form.setFieldsValue({
      project_id: record.project_id,
      expert_id: record.expert_id,
      rating: record.rating,
      comment: record.comment,
    });
    setOpen(true);
  };

  // =====================================
  // TABLE COLUMNS CONFIG
  // =====================================
  const columns = [
    {
      title: "Project ID",
      dataIndex: "project_id",
      render: (text) => <Text style={{ color: "#818cf8", fontWeight: 500 }}>{text}</Text>,
    },
    {
      title: "Expert ID",
      dataIndex: "expert_id",
      render: (text) => <Text style={{ color: "#e5e7eb" }}>{text}</Text>,
    },
    {
      title: "Rating",
      dataIndex: "rating",
      render: (rating) => <Text style={{ color: "#fbbf24", fontWeight: "bold" }}>⭐ {rating}/5</Text>,
    },
    {
      title: "Comment",
      dataIndex: "comment",
      render: (text) => <Text style={{ color: "#d1d5db" }}>{text || "-"}</Text>,
    },
    {
      title: "Created",
      dataIndex: "created_at",
      render: (value) => (
        <Text style={{ color: "#9ca3af" }}>
          {value ? new Date(value).toLocaleString() : "-"}
        </Text>
      ),
    },
    {
      title: "Action",
      render: (_, record) => (
        <Space>
          <Button
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            ghost
            style={{ color: "#9ca3af", borderColor: "#374151" }}
          >
            Sửa
          </Button>

          <Popconfirm
            title="Xóa đánh giá này?"
            onConfirm={() => handleDelete(record.id)}
            okText="Xóa"
            cancelText="Hủy"
          >
            <Button danger icon={<DeleteOutlined />} ghost>
              Xóa
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    // Khối cha phủ nền tối sâu toàn trang #090d16
    <div style={{ padding: 24, background: "#090d16", minHeight: "100vh" }}>
      
      {/* CSS Injection để điều hướng style mượt mà sang giao diện tối */}
      <style>{`
        /* --- ĐỊNH DẠNG KHUNG TABLE TỐI ANTD --- */
        .ant-table-thead > tr > th {
          background: #1f2937 !important;
          color: #fff !important;
          border-bottom: 1px solid #374151 !important;
        }
        .ant-table-tbody > tr > td {
          background: #111827 !important;
          border-bottom: 1px solid #1f2937 !important;
        }
        .ant-table-tbody > tr:hover > td {
          background: #1f2937 !important;
        }
        .ant-table {
          border: 1px solid #1f2937 !important;
          background: #111827 !important;
        }
        .ant-pagination-item a, .ant-pagination-item-link {
          color: #fff !important;
        }
        .ant-pagination-item-active {
          background: #4f46e5 !important;
          border-color: #4f46e5 !important;
        }

        /* --- ĐỊNH DẠNG ĐƯỜNG FORM NHẬP LIỆU TỐI --- */
        .dark-form .ant-form-item-label > label {
          color: #9ca3af !important;
        }
        .dark-input, .ant-input-number {
          background-color: #1f2937 !important;
          border-color: #374151 !important;
          color: #fff !important;
        }
        .dark-input:focus, .ant-input-number-focused {
          border-color: #818cf8 !important;
        }
        .ant-input-number-input {
          color: #fff !important;
        }
      `}</style>

      {/* Cấu hình Thẻ Card bao bọc mang đậm phong cách Dark Cyberpunk */}
      <Card
        style={{ background: "#111827", border: "1px solid #1f2937", borderRadius: 12 }}
        title={<span style={{ color: "#fff", fontSize: 18, fontWeight: 600 }}>Quản lý đánh giá</span>}
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => {
              setEditing(null);
              form.resetFields();
              setOpen(true);
            }}
            style={{ background: "#4f46e5", border: "none" }}
          >
            Thêm đánh giá
          </Button>
        }
      >
        <Table
          rowKey="id"
          loading={loading}
          columns={columns}
          dataSource={reviews}
        />

        {/* Hộp thoại Modal Dark Mode đồng bộ */}
        <Modal
          open={open}
          footer={null}
          destroyOnClose
          onCancel={() => setOpen(false)}
          title={
            <span style={{ color: "#fff", fontSize: 18, fontWeight: 600 }}>
              {editing ? "Cập nhật đánh giá" : "Thêm đánh giá"}
            </span>
          }
          styles={{
            body: { background: "#111827", paddingTop: 16 },
            content: { background: "#111827", border: "1px solid #1f2937" },
            header: { background: "#111827", borderBottom: "1px solid #1f2937", paddingBottom: 12 }
          }}
        >
          <Form
            layout="vertical"
            form={form}
            onFinish={handleFinish}
            className="dark-form"
          >
            <Form.Item
              label="Project ID"
              name="project_id"
              rules={[{ required: true, message: "Vui lòng nhập Project ID!" }]}
            >
              <Input className="dark-input" placeholder="Nhập mã dự án..." />
            </Form.Item>

            <Form.Item
              label="Expert ID"
              name="expert_id"
              rules={[{ required: true, message: "Vui lòng nhập Expert ID!" }]}
            >
              <Input className="dark-input" placeholder="Nhập mã chuyên gia..." />
            </Form.Item>

            <Form.Item
              label="Rating (1 - 5)"
              name="rating"
              rules={[{ required: true, message: "Vui lòng chọn số sao đánh giá!" }]}
            >
              <InputNumber
                min={1}
                max={5}
                style={{ width: "100%" }}
                placeholder="Ví dụ: 5"
              />
            </Form.Item>

            <Form.Item label="Comment" name="comment">
              <Input.TextArea className="dark-input" rows={4} placeholder="Nhập nhận xét chi tiết..." />
            </Form.Item>

            <Form.Item style={{ marginBottom: 0, marginTop: 24 }}>
              <Button
                htmlType="submit"
                type="primary"
                loading={loading}
                block
                style={{ background: "#4f46e5", border: "none", height: 40 }}
              >
                {editing ? "Cập nhật thay đổi" : "Xác nhận thêm mới"}
              </Button>
            </Form.Item>
          </Form>
        </Modal>
      </Card>
    </div>
  );
};

export default ReviewList;