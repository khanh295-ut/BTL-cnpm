import { useState } from 'preact/hooks'
import ExpertCard from '../../components/ExpertCard/ExpertCard'
import './Expert.css'

const allExperts = [
  { name: 'Nguyễn Văn A', title: 'Chatbot Specialist', avatar: 'https://i.pravatar.cc/300?img=1', rating: 5, skill: 'Chatbot' },
  { name: 'Trần Thị B', title: 'Computer Vision Engineer', avatar: 'https://i.pravatar.cc/300?img=2', rating: 4, skill: 'Computer Vision' },
  { name: 'Lê Văn C', title: 'NLP Researcher', avatar: 'https://i.pravatar.cc/300?img=3', rating: 5, skill: 'NLP' },
  { name: 'Phạm Thị D', title: 'Automation Engineer', avatar: 'https://i.pravatar.cc/300?img=4', rating: 4, skill: 'Automation' },
  { name: 'Hoàng Văn E', title: 'Chatbot Developer', avatar: 'https://i.pravatar.cc/300?img=5', rating: 5, skill: 'Chatbot' },
  { name: 'Vũ Thị F', title: 'Computer Vision Researcher', avatar: 'https://i.pravatar.cc/300?img=6', rating: 3, skill: 'Computer Vision' },
  { name: 'Đặng Văn G', title: 'NLP Engineer', avatar: 'https://i.pravatar.cc/300?img=7', rating: 4, skill: 'NLP' },
  { name: 'Ngô Thị H', title: 'RPA Automation Specialist', avatar: 'https://i.pravatar.cc/300?img=8', rating: 5, skill: 'Automation' },
]

const skills = ['Tất cả', 'Chatbot', 'Automation', 'Computer Vision', 'NLP']

export default function Expert() {
  const [activeSkill, setActiveSkill] = useState('Tất cả')
  const [search, setSearch] = useState('')

  const filteredExperts = allExperts.filter((expert) => {
    const matchSkill = activeSkill === 'Tất cả' || expert.skill === activeSkill
    const matchSearch = expert.name.toLowerCase().includes(search.toLowerCase()) ||
                         expert.title.toLowerCase().includes(search.toLowerCase())
    return matchSkill && matchSearch
  })

  return (
    <div class="expert-page">
      <div class="expert-page-header">
        <h1>Danh sách Chuyên gia AI</h1>
        <p>Tìm chuyên gia phù hợp cho project của bạn</p>
      </div>

      <div class="expert-filter-bar">
        <input
          type="text"
          class="expert-search"
          placeholder="Tìm theo tên hoặc chức danh..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        <div class="skill-tabs">
          {skills.map((skill) => (
            <button
              key={skill}
              class={activeSkill === skill ? 'active' : ''}
              onClick={() => setActiveSkill(skill)}
            >
              {skill}
            </button>
          ))}
        </div>
      </div>

      <div class="expert-grid">
        {filteredExperts.map((expert, i) => (
          <ExpertCard key={i} {...expert} />
        ))}

        {filteredExperts.length === 0 && (
          <p class="expert-empty">Không tìm thấy chuyên gia phù hợp.</p>
        )}
      </div>
    </div>
  )
}