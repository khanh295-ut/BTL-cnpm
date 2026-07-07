import { LocationProvider, Router, Route } from 'preact-iso'
import Home from './pages/Home/Home'
import Login from './pages/Login/Login'
import Register from './pages/Register/Register'
import Dashboard from './pages/Dashboard/Dashboard'
import Project from './pages/Project/Project'
import Expert from './pages/Expert/Expert'
import Admin from './pages/Admin/Admin'

export function App() {
  return (
    <LocationProvider>
      <Router>
        <Route path="/" component={Home} />
        <Route path="/login" component={Login} />
        <Route path="/register" component={Register} />
        <Route path="/dashboard" component={Dashboard} />
        <Route path="/projects" component={Project} />
        <Route path="/experts" component={Expert} />
        <Route path="/admin" component={Admin} />
      </Router>
    </LocationProvider>
  )
}