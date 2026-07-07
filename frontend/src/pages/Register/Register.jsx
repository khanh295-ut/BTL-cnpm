import { useState } from 'preact/hooks'
import './Register.css'

export default function Register() {
  const [form, setForm] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
  })
  const [error, setError] = useState('')

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    setError('')

    if (!form.fullName || !form.email || !form.password || !form.confirmPassword) {
      setError('Vui lòng nhập đầy đủ thông tin.')
      return
    }

    if (form.password.length < 6) {
      setError('Mật khẩu phải có ít nhất 6 ký tự.')
      return
    }

    if (form.password !== form.confirmPassword) {
      setError('Mật khẩu xác nhận không khớp.')
      return
    }

    // TODO: gọi API đăng ký ở buổi kết nối Axios với FastAPI
    console.log('Register data:', form)
  }

  return (
    <div class="auth-page">
      <div class="auth-card">
        <a href="/" class="auth-logo">AI Expert Hub</a>
        <h2>Tạo tài khoản</h2>
        <p class="auth-subtitle">Bắt đầu kết nối với chuyên gia AI ngay hôm nay</p>

        {error && <div class="auth-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div class="form-group">
            <label>Họ và tên</label>
            <input
              type="text"
              name="fullName"
              placeholder="Nguyễn Văn A"
              value={form.fullName}
              onChange={handleChange}
            />
          </div>

          <div class="form-group">
            <label>Email</label>
            <input
              type="email"
              name="email"
              placeholder="you@example.com"
              value={form.email}
              onChange={handleChange}
            />
          </div>

          <div class="form-group">
            <label>Mật khẩu</label>
            <input
              type="password"
              name="password"
              placeholder="••••••••"
              value={form.password}
              onChange={handleChange}
            />
          </div>

          <div class="form-group">
            <label>Xác nhận mật khẩu</label>
            <input
              type="password"
              name="confirmPassword"
              placeholder="••••••••"
              value={form.confirmPassword}
              onChange={handleChange}
            />
          </div>

          <button type="submit" class="btn btn-primary auth-btn">Đăng ký</button>
        </form>

        <p class="auth-footer-text">
          Đã có tài khoản? <a href="/login">Đăng nhập</a>
        </p>
      </div>
    </div>
  )
}