import React, { useEffect, useState } from "react";
import {
  Table,
  Button,
  Modal,
  Form,
  Input,
  InputNumber,
  DatePicker,
  Select,
  Popconfirm,
  Tag,
  App,
  Flex,
  Typography,
} from "antd";

import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
} from "@ant-design/icons";

// ĐÃ SỬA: Thay thế axios thuần bằng axiosClient được định tuyến chuẩn hóa
import axiosClient from "../api/axiosClient";
import dayjs from "dayjs";

const { Text } = Typography;

// 1. COMPONENT NỘI DUNG CHÍNH
const ProjectListContent = () => {
  const { message } = App.useApp();
  
  const [projects, setProjects] = useState([]);
  const [enterprises, setEnterprises] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form] = Form.useForm();

  //--------------------------------------
  // Load data
  //--------------------------------------
  const loadProjects = async () => {
    setLoading(true);
    try {
      const res = await axiosClient.get("/projects");
      setProjects(res.data);
    } catch (err) {
      console.error(err);
      message.error("Không tải được danh sách Project");
    } finally {
      setLoading(false);
    }
  };

  const loadEnterprises = async () => {
    try {
      const res = await axiosClient.get("/enterprises");
      setEnterprises(res.data);
    } catch (err) {
      console.error("Lỗi tải doanh nghiệp:", err);
    }
  };

  const loadCategories = async () => {
    try {
      const res = await axiosClient.get("/categories");
      setCategories(res.data);
    } catch (err) {
      console.error("Lỗi tải danh mục:", err);
    }
  };

  useEffect(() => {
    loadProjects();
    loadEnterprises();
    loadCategories();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  //--------------------------------------
  // Save
  //--------------------------------------
  const onFinish = async (values) => {
    try {
      const payload = {
        ...values,
        deadline: values.deadline ? values.deadline.format("YYYY-MM-DD") : null,
      };

      if (editing) {
        await axiosClient.put(`/projects/${editing.id}`, payload);
        message.success("Cập nhật thành công");
      } else {
        await axiosClient.post("/projects", payload);
        message.success("Thêm thành công");
      }

      form.resetFields();
      setOpen(false);
      setEditing(null);
      loadProjects();
    } catch (err) {
      console.error(err.response?.data || err);
      message.error("Lưu thất bại. Vui lòng kiểm tra lại kết nối.");
    }
  };

  //--------------------------------------
  // Delete
  //--------------------------------------
  const deleteProject = async (id) => {
    try {
      await axiosClient.delete(`/projects/${id}`);
      message.success("Đã xóa dự án");
      loadProjects();
    } catch (err) {
      console.error(err);
      message.error("Không xóa được dự án");
    }
  };

  //--------------------------------------
  // Edit
  //--------------------------------------
  const editProject = (record) => {
    setEditing(record);
    form.setFieldsValue({
      ...record,
      deadline: record.deadline ? dayjs(record.deadline) : null,
    });
    setOpen(true);
  };

  const columns = [
    { 
      title: "Tên dự án", 
      dataIndex: "title", 
      key: "title",
      render: (text) => <Text style={{ color: "#fff", fontWeight: 500 }}>{text}</Text>
    },
    { 
      title: "Ngân sách", 
      dataIndex: "budget", 
      key: "budget",
      render: (val) => <Text style={{ color: "#fff" }}>{val ? `${Number(val).toLocaleString()} VNĐ` : 'Chưa có'}</Text>
    },
    { 
      title: "Deadline", 
      dataIndex: "deadline", 
      key: "deadline",
      render: (text) => <Text style={{ color: "#9ca3af" }}>{text || "-"}</Text>
    },
    {
      title: "Trạng thái",
      dataIndex: "status",
      key: "status",
      render: (status) => {
        let color = "default";
        if (status === "OPEN") color = "green";
        else if (status === "IN_PROGRESS") color = "blue";
        else if (status === "PENDING") color = "gold";
        else if (status === "COMPLETED") color = "cyan";
        else if (status === "CANCELLED") color = "magenta";

        return <Tag color={color}>{status}</Tag>;
      },
    },
    {
      title: "Thao tác",
      key: "action",
      render: (_, record) => (
        <Flex gap="small">
          <Button 
            icon={<EditOutlined />} 
            onClick={() => editProject(record)} 
            ghost
            style={{ color: "#9ca3af", borderColor: "#374151" }}
          />
          <Popconfirm title="Bạn có chắc chắn muốn xóa?" onConfirm={() => deleteProject(record.id)}>
            <Button danger icon={<DeleteOutlined />} ghost />
          </Popconfirm>
        </Flex>
      ),
    },
  ];

  return (
    <div style={{ padding: 24, background: "#090d16", minHeight: "100vh" }}>
      
      <style>{`
        /* --- ĐỊNH DẠNG TABLE --- */
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

        /* --- ĐỊNH DẠNG INPUT CONTROLS --- */
        .dark-input, .ant-input-number, .ant-picker, .ant-select-selector {
          background-color: #1f2937 !important;
          color: #fff !important;
          border: 1px solid #374151 !important;
        }
        .ant-select-arrow, .ant-picker-suffix {
          color: #9ca3af !important;
        }
        .dark-dropdown {
          background-color: #1f2937 !important;
        }
        .dark-dropdown .ant-select-item {
          color: #fff !important;
        }
        .dark-dropdown .ant-select-item-option-active {
          background-color: #374151 !important;
        }
        .dark-dropdown .ant-select-item-option-selected {
          background-color: #4f46e5 !important;
        }
      `}</style>

      <Button
        type="primary"
        icon={<PlusOutlined />}
        onClick={() => {
          setEditing(null);
          form.resetFields();
          setOpen(true);
        }}
        style={{ marginBottom: 20, background: "#4f46e5", border: "none" }}
      >
        Thêm Project
      </Button>

      <Table 
        rowKey="id" 
        loading={loading} 
        columns={columns} 
        dataSource={projects} 
        pagination={{ pageSize: 10 }}
      />

      {/* ĐÃ SỬA: Thay thế destroyOnClose thành destroyOnHidden để xóa cảnh báo antd */}
      <Modal
        open={open}
        title={<span style={{ color: "#fff", fontSize: 18, fontWeight: 600 }}>{editing ? "Sửa Project" : "Thêm Project"}</span>}
        onCancel={() => {
          setOpen(false);
          form.resetFields();
        }}
        onOk={() => form.submit()}
        okText="Lưu dự án"
        cancelText="Hủy bỏ"
        destroyOnHidden
        styles={{
          body: { background: "#111827" },
          content: { background: "#111827", border: "1px solid #1f2937" },
          header: { background: "#111827" }
        }}
      >
        <Form form={form} layout="vertical" onFinish={onFinish} style={{ marginTop: 16 }}>
          <Form.Item 
            name="title" 
            label={<span style={{ color: "#9ca3af" }}>Tên dự án</span>} 
            rules={[{ required: true, message: 'Vui lòng nhập tên dự án!' }]}
          >
            <Input className="dark-input" placeholder="Nhập tên dự án AI..." />
          </Form.Item>
          
          <Form.Item 
            name="description" 
            label={<span style={{ color: "#9ca3af" }}>Mô tả</span>} 
            rules={[{ required: true, message: 'Vui lòng nhập mô tả!' }]}
          >
            <Input.TextArea className="dark-input" rows={4} placeholder="Nhập mô tả chi tiết..." />
          </Form.Item>
          
          <Form.Item name="budget" label={<span style={{ color: "#9ca3af" }}>Ngân sách (VNĐ)</span>}>
            <InputNumber style={{ width: "100%" }} placeholder="Nhập số tiền..." />
          </Form.Item>
          
          <Form.Item name="deadline" label={<span style={{ color: "#9ca3af" }}>Hạn chót (Deadline)</span>}>
            <DatePicker style={{ width: "100%" }} format="YYYY-MM-DD" placeholder="Chọn ngày..." />
          </Form.Item>
          
          <Form.Item 
            name="enterprise_id" 
            label={<span style={{ color: "#9ca3af" }}>Doanh nghiệp</span>} 
            rules={[{ required: true, message: 'Vui lòng chọn doanh nghiệp!' }]}
          >
            <Select popupClassName="dark-dropdown" placeholder="Chọn doanh nghiệp đối tác">
              {enterprises.map((e) => (
                <Select.Option key={e.id} value={e.id}>{e.name}</Select.Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item name="category_id" label={<span style={{ color: "#9ca3af" }}>Danh mục (Category)</span>}>
            <Select popupClassName="dark-dropdown" allowClear placeholder="Chọn lĩnh vực AI">
              {categories.map((c) => (
                <Select.Option key={c.id} value={c.id}>{c.name}</Select.Option>
              ))}
            </Select>
          </Form.Item>
          
          {editing && (
            <Form.Item name="status" label={<span style={{ color: "#9ca3af" }}>Trạng thái</span>}>
              <Select popupClassName="dark-dropdown">
                <Select.Option value="OPEN">OPEN (Đang mở)</Select.Option>
                <Select.Option value="IN_PROGRESS">IN_PROGRESS (Đang thực thi)</Select.Option>
                <Select.Option value="COMPLETED">COMPLETED (Hoàn thành)</Select.Option>
                <Select.Option value="CANCELLED">CANCELLED (Đã hủy)</Select.Option>
              </Select>
            </Form.Item>
          )}
        </Form>
      </Modal>
    </div>
  );
};

// 2. WRAPPER GỐC BỌC THE APP
const ProjectList = () => {
  return (
    <App>
      <ProjectListContent />
    </App>
  );
};

export default ProjectList;