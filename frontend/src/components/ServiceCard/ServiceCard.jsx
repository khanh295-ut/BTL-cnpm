import './ServiceCard.css'

export default function ServiceCard({ icon, title, description }) {
  return (
    <div class="service-card">
      <div class="service-icon">{icon}</div>
      <h3 class="service-title">{title}</h3>
      <p class="service-desc">{description}</p>
    </div>
  )
}