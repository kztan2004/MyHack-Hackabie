import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import AddStartup from './pages/AddStartup'
import AddMentor from './pages/AddMentor'
import MatchPage from './pages/MatchPage'
import GraphPage from './pages/GraphPage'

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen ambient-bg relative">
        <Navbar />
        <main className="relative z-10 pt-20">
          <Routes>
            <Route path="/"            element={<Dashboard />} />
            <Route path="/add-startup" element={<AddStartup />} />
            <Route path="/add-mentor"  element={<AddMentor />} />
            <Route path="/match"       element={<MatchPage />} />
            <Route path="/graph"       element={<GraphPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
