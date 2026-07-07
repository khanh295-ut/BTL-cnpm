import './Navbar.css'
import viteLogo from '../../assets/vite.svg'

export default function Navbar() {
  return (
    <nav class="navbar">
      <div class="navbar-container">
        <a href="/" class="navbar-logo">
          <img src={viteLogo} alt="logo" />
          <span>AI Expert Hub</span>
        </a>

        <ul class="navbar-links">
          <li><a href="/">Home</a></li>
          <li><a href="/experts">Experts</a></li>
          <li><a href="/projects">Projects</a></li>
        </ul>

        <div class="navbar-auth">
          <a href="/login" class="btn btn-outline">Login</a>
          <a href="/register" class="btn btn-primary">Register</a>
        </div>
      </div>
    </nav>
  )
}