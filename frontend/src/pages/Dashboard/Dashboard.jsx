import { useState } from 'preact/hooks'
import './Dashboard.css'

const clientStats = [
  { label: 'Project đang chạy', value: 3 },
  { label: 'Proposal nhận được', value: 12 },
  { label: 'Chuyên gia đã thuê', value: 5 },
]

const expertStats = [
  { label: 'Project đang nhận', value: 4 },
  { label: 'Thu nhập tháng này', value: '12.500.000đ' },
  { label: 'Đánh giá trung bình', value: '4.8 ★' },
]

const clientProjects = [
  { name: 'Xây dựng Chatbot CSKH', status: 'Đang thực hiện', expert: 'Nguyễn Văn A' },
  { name: 'Hệ thống Computer Vision kiểm tra lỗi', status: 'Chờ duyệt', expert: 'Trần Thị B' },
  { name: 'Phân tích văn bản phản hồi khách hàng', status: 'Hoàn thành', expert: 'Lê Văn C' },
]

const expertProjects = [
  { name: 'Chatbot bán hàng cho Shop ABC', status: 'Đang thực hiện', client: 'Công ty XYZ' },
  { name: 'Tự động hóa quy trình duyệt đơn', status: 'Chờ phản hồi', client: 'Công ty DEF' },
]

export default function Dashboard() {
  const [role, setRole] = useState('client') // 'client' | 'expert' — sẽ lấy từ auth thật sau này

  const stats = role === 'client' ? clientStats : expertStats
  const projects = role === 'client' ? clientProjects : expertProjects

  return (
    <div class="dashboard-page">
      <aside class="dashboard-sidebar">
        <a href="/" class="dashboard-logo">AI Expert Hub</a>

        <nav class="dashboard-nav">
          <a href="/dashboard" class="active">Dashboard</a>
          <a href="/projects">Projects</a>
          <a href="/experts">Experts</a>
          <a href="/profile">Hồ sơ</a>
        </nav>

        {/* TODO: xóa phần này khi có auth thật, role sẽ tự lấy từ tài khoản đăng nhập */}
        <div class="role-switch">
          <p>Xem thử vai trò:</p>
          <button
            class={role === 'client' ? 'active' : ''}
            onClick={() => setRole('client')}
          >
            Client
          </button>
          <button
            class={role === 'expert' ? 'active' : ''}
            onClick={() => setRole('expert')}
          >
            Expert
          </button>
        </div>
      </aside>

      <main class="dashboard-main">
        <h1>
          Chào mừng trở lại, {role === 'client' ? 'Khách hàng' : 'Chuyên gia'}!
        </h1>

        <div class="dashboard-stats">
          {stats.map((stat, i) => (
            <div class="stat-card" key={i}>
              <p class="stat-value">{stat.value}</p>
              <p class="stat-label">{stat.label}</p>
            </div>
          ))}
        </div>

        <section class="dashboard-table-section">
          <h2>{role === 'client' ? 'Project của bạn' : 'Project đang nhận'}</h2>
          <table class="dashboard-table">
            <thead>
              <tr>
                <th>Tên project</th>
                <th>{role === 'client' ? 'Chuyên gia' : 'Khách hàng'}</th>
                <th>Trạng thái</th>
              </tr>
            </thead>
            <tbody>
              {projects.map((p, i) => (
                <tr key={i}>
                  <td>{p.name}</td>
                  <td>{role === 'client' ? p.expert : p.client}</td>
                  <td>
                    <span class={`status-badge status-${p.status === 'Hoàn thành' ? 'done' : p.status === 'Đang thực hiện' ? 'progress' : 'pending'}`}>
                      {p.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </main>
    </div>
  )
}