import Navbar from '../../components/Navbar/Navbar'
import Hero from '../../components/Hero/Hero'
import ExpertCard from '../../components/ExpertCard/ExpertCard'
import ServiceCard from '../../components/ServiceCard/ServiceCard'
import Footer from '../../components/Footer/Footer'
import './Home.css'

const experts = [
  { name: 'Nguyễn Văn A', title: 'Chatbot Specialist', avatar: 'https://i.pravatar.cc/300?img=1', rating: 5 },
  { name: 'Trần Thị B', title: 'Computer Vision Engineer', avatar: 'https://i.pravatar.cc/300?img=2', rating: 4 },
  { name: 'Lê Văn C', title: 'NLP Researcher', avatar: 'https://i.pravatar.cc/300?img=3', rating: 5 },
]

const services = [
  { icon: '💬', title: 'Chatbot', description: 'Xây dựng chatbot thông minh cho doanh nghiệp' },
  { icon: '⚙️', title: 'Automation', description: 'Tự động hóa quy trình nghiệp vụ với AI' },
  { icon: '👁️', title: 'Computer Vision', description: 'Nhận diện hình ảnh, video thông minh' },
  { icon: '📝', title: 'NLP', description: 'Xử lý ngôn ngữ tự nhiên, phân tích văn bản' },
]

export default function Home() {
  return (
    <>
      <Navbar />
      <Hero />

      <section class="section">
        <h2 class="section-title">Popular Experts</h2>
        <div class="grid grid-3">
          {experts.map((expert, i) => (
            <ExpertCard key={i} {...expert} />
          ))}
        </div>
      </section>

      <section class="section">
        <h2 class="section-title">Popular Services</h2>
        <div class="grid grid-4">
          {services.map((service, i) => (
            <ServiceCard key={i} {...service} />
          ))}
        </div>
      </section>

      <Footer />
    </>
  )
}