import { useState } from 'preact/hooks'
import './Login.css'

export default function Login() {
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    setError('')

    if (!form.email || !form.password) {
      setError('Vui lòng nhập đầy đủ email và mật khẩu.')
      return
    }

    // TODO: gọi API đăng nhập ở buổi kết nối Axios với FastAPI
    console.log('Login data:', form)
  }

  return (
    <div class="auth-page">
      <div class="auth-card">
        <a href="/" class="auth-logo">AI Expert Hub</a>
        <h2>Đăng nhập</h2>
        <p class="auth-subtitle">Chào mừng bạn trở lại!</p>

        {error && <div class="auth-error">{error}</div>}

        <form onSubmit={handleSubmit}>
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

          <button type="submit" class="btn btn-primary auth-btn">Đăng nhập</button>
        </form>

        <p class="auth-footer-text">
          Chưa có tài khoản? <a href="/register">Đăng ký ngay</a>
        </p>
      </div>
    </div>
  )
}