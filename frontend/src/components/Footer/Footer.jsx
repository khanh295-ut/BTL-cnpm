import './Footer.css'

export default function Footer() {
  return (
    <footer class="footer">
      <div class="footer-container">
        <div class="footer-brand">
          <h3>AI Expert Hub</h3>
          <p>Kết nối bạn với các chuyên gia AI hàng đầu.</p>
        </div>

        <div class="footer-links">
          <div class="footer-col">
            <h4>Khám phá</h4>
            <a href="/">Home</a>
            <a href="/experts">Experts</a>
            <a href="/projects">Projects</a>
          </div>

          <div class="footer-col">
            <h4>Tài khoản</h4>
            <a href="/login">Login</a>
            <a href="/register">Register</a>
          </div>
        </div>
      </div>

      <div class="footer-bottom">
        <p>&copy; {new Date().getFullYear()} AI Expert Hub. All rights reserved.</p>
      </div>
    </footer>
  )
}