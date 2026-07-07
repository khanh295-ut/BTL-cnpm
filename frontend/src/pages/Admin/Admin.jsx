import { useState } from 'preact/hooks'
import './Admin.css'

const initialUsers = [
  { id: 1, name: 'Nguyễn Văn A', email: 'vana@gmail.com', role: 'Expert', status: 'Hoạt động' },
  { id: 2, name: 'Trần Thị B', email: 'thib@gmail.com', role: 'Client', status: 'Hoạt động' },
  { id: 3, name: 'Lê Văn C', email: 'vanc@gmail.com', role: 'Expert', status: 'Đã khóa' },
  { id: 4, name: 'Phạm Thị D', email: 'thid@gmail.com', role: 'Client', status: 'Hoạt động' },
]

const initialProjects = [
  { id: 1, name: 'Xây dựng Chatbot CSKH', client: 'Trần Thị B', status: 'Chờ duyệt' },
  { id: 2, name: 'Hệ thống Computer Vision kiểm tra lỗi', client: 'Phạm Thị D', status: 'Chờ duyệt' },
  { id: 3, name: 'Phân tích văn bản phản hồi khách hàng', client: 'Trần Thị B', status: 'Đã duyệt' },
]

export default function Admin() {
  const [tab, setTab] = useState('overview') // overview | users | projects
  const [users, setUsers] = useState(initialUsers)
  const [projects, setProjects] = useState(initialProjects)

  const toggleUserStatus = (id) => {
    setUsers(users.map((u) =>
      u.id === id
        ? { ...u, status: u.status === 'Hoạt động' ? 'Đã khóa' : 'Hoạt động' }
        : u
    ))
  }

  const updateProjectStatus = (id, newStatus) => {
    setProjects(projects.map((p) => (p.id === id ? { ...p, status: newStatus } : p)))
  }

  const totalUsers = users.length
  const totalExperts = users.filter((u) => u.role === 'Expert').length
  const totalClients = users.filter((u) => u.role === 'Client').length
  const totalProjects = projects.length
  const pendingProjects = projects.filter((p) => p.status === 'Chờ duyệt').length

  return (
    <div class="admin-page">
      <aside class="admin-sidebar">
        <a href="/" class="admin-logo">AI Expert Hub</a>
        <p class="admin-role-tag">Quản trị viên</p>

        <nav class="admin-nav">
          <button class={tab === 'overview' ? 'active' : ''} onClick={() => setTab('overview')}>Tổng quan</button>
          <button class={tab === 'users' ? 'active' : ''} onClick={() => setTab('users')}>Quản lý User</button>
          <button class={tab === 'projects' ? 'active' : ''} onClick={() => setTab('projects')}>Quản lý Project</button>
        </nav>
      </aside>

      <main class="admin-main">
        {tab === 'overview' && (
          <section>
            <h1>Tổng quan hệ thống</h1>
            <div class="admin-stats">
              <div class="stat-card">
                <p class="stat-value">{totalUsers}</p>
                <p class="stat-label">Tổng người dùng</p>
              </div>
              <div class="stat-card">
                <p class="stat-value">{totalExperts}</p>
                <p class="stat-label">Chuyên gia</p>
              </div>
              <div class="stat-card">
                <p class="stat-value">{totalClients}</p>
                <p class="stat-label">Khách hàng</p>
              </div>
              <div class="stat-card">
                <p class="stat-value">{totalProjects}</p>
                <p class="stat-label">Tổng project</p>
              </div>
              <div class="stat-card">
                <p class="stat-value">{pendingProjects}</p>
                <p class="stat-label">Project chờ duyệt</p>
              </div>
            </div>
          </section>
        )}

        {tab === 'users' && (
          <section>
            <h1>Quản lý người dùng</h1>
            <table class="admin-table">
              <thead>
                <tr>
                  <th>Tên</th>
                  <th>Email</th>
                  <th>Vai trò</th>
                  <th>Trạng thái</th>
                  <th>Hành động</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td>{u.name}</td>
                    <td>{u.email}</td>
                    <td>{u.role}</td>
                    <td>
                      <span class={`status-badge ${u.status === 'Hoạt động' ? 'status-active' : 'status-locked'}`}>
                        {u.status}
                      </span>
                    </td>
                    <td>
                      <button
                        class={u.status === 'Hoạt động' ? 'btn btn-danger' : 'btn btn-outline'}
                        onClick={() => toggleUserStatus(u.id)}
                      >
                        {u.status === 'Hoạt động' ? 'Khóa' : 'Mở khóa'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}

        {tab === 'projects' && (
          <section>
            <h1>Quản lý Project</h1>
            <table class="admin-table">
              <thead>
                <tr>
                  <th>Tên project</th>
                  <th>Khách hàng</th>
                  <th>Trạng thái</th>
                  <th>Hành động</th>
                </tr>
              </thead>
              <tbody>
                {projects.map((p) => (
                  <tr key={p.id}>
                    <td>{p.name}</td>
                    <td>{p.client}</td>
                    <td>
                      <span class={`status-badge ${p.status === 'Đã duyệt' ? 'status-active' : 'status-pending'}`}>
                        {p.status}
                      </span>
                    </td>
                    <td class="admin-table-actions">
                      {p.status === 'Chờ duyệt' ? (
                        <>
                          <button class="btn btn-primary" onClick={() => updateProjectStatus(p.id, 'Đã duyệt')}>Duyệt</button>
                          <button class="btn btn-danger" onClick={() => updateProjectStatus(p.id, 'Từ chối')}>Từ chối</button>
                        </>
                      ) : (
                        <span class="admin-no-action">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}
      </main>
    </div>
  )
}