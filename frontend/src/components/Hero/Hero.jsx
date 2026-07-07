import './Hero.css'
import heroImg from '../../assets/hero.png'

export default function Hero() {
  return (
    <section class="hero">
      <div class="hero-content">
        <h1>Hire AI Experts</h1>
        <p>Find the best AI experts for your project — from Chatbot to Computer Vision.</p>
        <a href="/experts" class="btn btn-primary btn-large">Find Expert</a>
      </div>

      <div class="hero-image">
        <img src={heroImg} alt="Hire AI experts" />
      </div>
    </section>
  )
}