import { useState } from 'preact/hooks'
import './Project.css'

const initialProjects = [
  { id: 1, name: 'Xây dựng Chatbot CSKH', budget: '15.000.000đ', status: 'Đang thực hiện', description: 'Chatbot hỗ trợ khách hàng tự động 24/7 cho website bán lẻ.' },
  { id: 2, name: 'Hệ thống Computer Vision kiểm tra lỗi', budget: '25.000.000đ', status: 'Chờ duyệt', description: 'Phát hiện lỗi sản phẩm trên dây chuyền sản xuất bằng camera AI.' },
  { id: 3, name: 'Phân tích văn bản phản hồi khách hàng', budget: '8.000.000đ', status: 'Hoàn thành', description: 'NLP phân loại cảm xúc từ đánh giá sản phẩm.' },
]

const emptyForm = { name: '', budget: '', status: 'Chờ duyệt', description: '' }

export default function Project() {
  const [projects, setProjects] = useState(initialProjects)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [editingId, setEditingId] = useState(null)

  const openCreateForm = () => {
    setForm(emptyForm)
    setEditingId(null)
    setShowForm(true)
  }

  const openEditForm = (project) => {
    setForm({ name: project.name, budget: project.budget, status: project.status, description: project.description })
    setEditingId(project.id)
    setShowForm(true)
  }

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!form.name || !form.budget) return

    if (editingId) {
      // Update
      setProjects(projects.map((p) => (p.id === editingId ? { ...p, ...form } : p)))
    } else {
      // Create
      const newProject = { id: Date.now(), ...form }
      setProjects([newProject, ...projects])
    }

    setShowForm(false)
  }

  const handleDelete = (id) => {
    if (confirm('Bạn có chắc muốn xóa project này?')) {
      setProjects(projects.filter((p) => p.id !== id))
    }
  }

  return (
    <div class="project-page">
      <div class="project-header">
        <h1>Danh sách Project</h1>
        <button class="btn btn-primary" onClick={openCreateForm}>+ Tạo Project mới</button>
      </div>

      <div class="project-grid">
        {projects.map((p) => (
          <div class="project-card" key={p.id}>
            <div class="project-card-top">
              <h3>{p.name}</h3>
              <span class={`status-badge status-${p.status === 'Hoàn thành' ? 'done' : p.status === 'Đang thực hiện' ? 'progress' : 'pending'}`}>
                {p.status}
              </span>
            </div>
            <p class="project-desc">{p.description}</p>
            <p class="project-budget">Ngân sách: <strong>{p.budget}</strong></p>

            <div class="project-actions">
              <button class="btn btn-outline" onClick={() => openEditForm(p)}>Sửa</button>
              <button class="btn btn-danger" onClick={() => handleDelete(p.id)}>Xóa</button>
            </div>
          </div>
        ))}

        {projects.length === 0 && (
          <p class="project-empty">Chưa có project nào. Bấm "Tạo Project mới" để bắt đầu.</p>
        )}
      </div>

      {showForm && (
        <div class="modal-overlay" onClick={() => setShowForm(false)}>
          <div class="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>{editingId ? 'Chỉnh sửa Project' : 'Tạo Project mới'}</h2>

            <form onSubmit={handleSubmit}>
              <div class="form-group">
                <label>Tên project</label>
                <input type="text" name="name" value={form.name} onChange={handleChange} placeholder="Ví dụ: Xây dựng chatbot bán hàng" />
              </div>

              <div class="form-group">
                <label>Ngân sách</label>
                <input type="text" name="budget" value={form.budget} onChange={handleChange} placeholder="Ví dụ: 15.000.000đ" />
              </div>

              <div class="form-group">
                <label>Trạng thái</label>
                <select name="status" value={form.status} onChange={handleChange}>
                  <option value="Chờ duyệt">Chờ duyệt</option>
                  <option value="Đang thực hiện">Đang thực hiện</option>
                  <option value="Hoàn thành">Hoàn thành</option>
                </select>
              </div>

              <div class="form-group">
                <label>Mô tả</label>
                <textarea name="description" value={form.description} onChange={handleChange} placeholder="Mô tả ngắn về project" rows="3" />
              </div>

              <div class="modal-actions">
                <button type="button" class="btn btn-outline" onClick={() => setShowForm(false)}>Hủy</button>
                <button type="submit" class="btn btn-primary">{editingId ? 'Lưu thay đổi' : 'Tạo project'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}