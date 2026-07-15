import React from 'react';
import { Card, Switch, Typography, Divider, Button, message, Flex } from 'antd';
import { SaveOutlined } from '@ant-design/icons';

const { Text } = Typography;

const Settings = () => {
  // Mảng dữ liệu cấu hình để render cho sạch code
  const settingItems = [
    {
      key: 'email',
      title: 'Thông báo qua Email',
      desc: 'Nhận báo cáo khi có chuyên gia mới nộp hồ sơ.',
      defaultChecked: true,
    },
    {
      key: 'swagger',
      title: 'Đồng bộ Swagger',
      desc: 'Tự động cập nhật dữ liệu từ Backend.',
      defaultChecked: true,
    },
    {
      key: 'maintenance',
      title: 'Chế độ bảo trì',
      desc: 'Tạm dừng các hoạt động công khai của hệ thống.',
      defaultChecked: false,
    },
  ];

  return (
    // Khối cha phủ nền tối sâu toàn trang #090d16
    <div style={{ padding: 24, background: '#090d16', minHeight: '100vh' }}>
      
      {/* ĐÃ THÊM: Tiêm CSS Style để làm tối phần nền xám mặc định của Switch khi chưa bật */}
      <style>{`
        .ant-switch {
          background-color: #374151 !important;
        }
        .ant-switch-checked {
          background-color: #4f46e5 !important;
        }
      `}</style>

      <Card 
        title={<span style={{ color: '#fff', fontSize: 18, fontWeight: 600 }}>Cài đặt hệ thống</span>} 
        variant="none"
        style={{ background: '#111827', color: '#fff', border: '1px solid #1f2937', borderRadius: 12 }}
      >
        {/* ĐÃ SỬA WARNING: Thay thế `direction="vertical"` bằng thuộc tính chuẩn `vertical` */}
        <Flex vertical gap={20}>
          {settingItems.map((item, index) => (
            <div key={item.key}>
              <Flex justify="space-between" align="center">
                {/* ĐÃ SỬA WARNING: Thay đổi tương tự tại đây */}
                <Flex vertical>
                  <Text strong style={{ color: '#fff', fontSize: '16px' }}>{item.title}</Text>
                  <Text style={{ color: '#9ca3af', marginTop: 2 }}>{item.desc}</Text>
                </Flex>
                <Switch defaultChecked={item.defaultChecked} />
              </Flex>
              {index < settingItems.length - 1 && (
                <Divider style={{ borderColor: '#1f2937', margin: '16px 0' }} />
              )}
            </div>
          ))}
        </Flex>

        <Divider style={{ borderColor: '#1f2937', margin: '24px 0' }} />
        
        <Button 
          type="primary" 
          icon={<SaveOutlined />} 
          onClick={() => message.success('Đã lưu cài đặt thành công!')}
          style={{ background: '#4f46e5', border: 'none', height: 40, padding: '0 20px' }}
        >
          Lưu thay đổi
        </Button>
      </Card>
    </div>
  );
};

export default Settings;