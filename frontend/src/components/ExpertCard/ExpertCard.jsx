import './ExpertCard.css'

export default function ExpertCard({ name, title, avatar, rating }) {
  return (
    <div class="expert-card">
      <img src={avatar} alt={name} class="expert-avatar" />
      <h3 class="expert-name">{name}</h3>
      <p class="expert-title">{title}</p>
      <div class="expert-rating">
        {'★'.repeat(rating)}{'☆'.repeat(5 - rating)}
      </div>
      <button class="btn btn-outline expert-btn">View Profile</button>
    </div>
  )
}