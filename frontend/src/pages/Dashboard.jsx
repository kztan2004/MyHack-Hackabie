import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Rocket, Users, GitMerge, Zap, ArrowRight, Activity } from 'lucide-react'
import StatCard from '../components/StatCard'
import { api } from '../api/client'

export default function Dashboard() {
  const [startups, setStartups]   = useState([])
  const [mentors,  setMentors]    = useState([])
  const [graph,    setGraph]      = useState(null)
  const [health,   setHealth]     = useState(null)
  const [loading,  setLoading]    = useState(true)

  useEffect(() => {
    Promise.all([
      api.listStartups().catch(() => []),
      api.listMentors().catch(() => []),
      api.getGraph().catch(() => null),
      api.health().catch(() => null),
    ]).then(([s, m, g, h]) => {
      setStartups(s)
      setMentors(m)
      setGraph(g)
      setHealth(h)
      setLoading(false)
    })
  }, [])

  const matchCount = graph?.edge_count ?? 0
  const acceptedCount = graph?.edges?.filter(e => e.status === 'accepted').length ?? 0

  return (
    <div className="page-container">
      {/* Hero */}
      <div className="mb-10">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium mb-4"
             style={{ background: 'rgba(124,92,252,0.15)', border: '1px solid rgba(124,92,252,0.3)', color: '#c084fc' }}>
          <Activity size={12} />
          AI-Powered Ecosystem Intelligence
        </div>
        <h1 className="text-4xl font-bold mb-3">
          <span className="gradient-text">EcosystemGraph</span>
          <span className="text-white"> AI</span>
        </h1>
        <p className="text-white/50 text-lg max-w-2xl">
          Automate startup-mentor relationships using Google Gemini + Neo4j Graph Intelligence.
          Every match is AI-generated, explainable, and continuously improving.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
        <StatCard icon={Rocket}   label="Startups"       value={loading ? '…' : startups.length} color="brand" />
        <StatCard icon={Users}    label="Mentors"        value={loading ? '…' : mentors.length}  color="green" />
        <StatCard icon={GitMerge} label="AI Matches"     value={loading ? '…' : matchCount}      color="blue"  />
        <StatCard icon={Zap}      label="Accepted"       value={loading ? '…' : acceptedCount}   color="yellow" />
      </div>

      {/* Quick actions */}
      <div className="grid md:grid-cols-3 gap-4 mb-10">
        {[
          { to: '/add-startup', icon: Rocket, title: 'Add Startup',     desc: 'Register a startup and let AI enrich its profile with tags and insights.', color: 'brand' },
          { to: '/add-mentor',  icon: Users,  title: 'Add Mentor',      desc: 'Onboard a mentor and normalize their expertise with Gemini AI.',            color: 'green' },
          { to: '/match',       icon: Zap,    title: 'Generate Matches', desc: 'Select a startup and let Gemini find the top 3 mentor matches.',            color: 'blue'  },
        ].map(({ to, icon: Icon, title, desc, color }) => (
          <Link key={to} to={to} className="glass-card p-6 block hover:border-white/20 transition-all duration-300 group animate-fade-in">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-4 transition-all group-hover:scale-110`}
                 style={{ background: color === 'brand' ? 'rgba(124,92,252,0.2)' : color === 'green' ? 'rgba(16,185,129,0.2)' : 'rgba(59,130,246,0.2)',
                          border: color === 'brand' ? '1px solid rgba(124,92,252,0.4)' : color === 'green' ? '1px solid rgba(16,185,129,0.4)' : '1px solid rgba(59,130,246,0.4)' }}>
              <Icon size={18} style={{ color: color === 'brand' ? '#c084fc' : color === 'green' ? '#6ee7b7' : '#93c5fd' }} />
            </div>
            <h3 className="font-semibold text-white mb-2 group-hover:gradient-text transition-all">{title}</h3>
            <p className="text-sm text-white/50 leading-relaxed mb-4">{desc}</p>
            <div className="flex items-center gap-1 text-xs text-white/30 group-hover:text-brand-400 transition-colors">
              Get started <ArrowRight size={12} />
            </div>
          </Link>
        ))}
      </div>

      {/* Recent startups + mentors side by side */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Recent Startups */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-white flex items-center gap-2"><Rocket size={16} className="text-brand-400" /> Recent Startups</h2>
            <Link to="/add-startup" className="text-xs text-brand-400 hover:text-brand-300 transition-colors">+ Add</Link>
          </div>
          {loading ? (
            <div className="space-y-3">{[...Array(3)].map((_, i) => <div key={i} className="h-14 rounded-xl bg-white/5 animate-pulse" />)}</div>
          ) : startups.length === 0 ? (
            <div className="text-center py-8 text-white/30 text-sm">No startups yet. <Link to="/add-startup" className="text-brand-400 hover:underline">Add one →</Link></div>
          ) : (
            <div className="space-y-2">
              {startups.slice(0, 5).map(s => (
                <div key={s.id} className="flex items-center gap-3 p-3 rounded-xl bg-white/3 hover:bg-white/6 transition-colors">
                  <div className="w-8 h-8 rounded-lg bg-brand-600/30 border border-brand-500/30 flex items-center justify-center text-sm">🚀</div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-white truncate">{s.name}</div>
                    <div className="text-xs text-white/40">{s.industry || 'Unknown'} · {s.stage || '—'}</div>
                  </div>
                  {s.ai_confidence > 0 && (
                    <div className="text-xs text-brand-400">{Math.round(s.ai_confidence * 100)}%</div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Mentors */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-white flex items-center gap-2"><Users size={16} className="text-green-400" /> Available Mentors</h2>
            <Link to="/add-mentor" className="text-xs text-green-400 hover:text-green-300 transition-colors">+ Add</Link>
          </div>
          {loading ? (
            <div className="space-y-3">{[...Array(3)].map((_, i) => <div key={i} className="h-14 rounded-xl bg-white/5 animate-pulse" />)}</div>
          ) : mentors.length === 0 ? (
            <div className="text-center py-8 text-white/30 text-sm">No mentors yet. <Link to="/add-mentor" className="text-green-400 hover:underline">Add one →</Link></div>
          ) : (
            <div className="space-y-2">
              {mentors.slice(0, 5).map(m => (
                <div key={m.id} className="flex items-center gap-3 p-3 rounded-xl bg-white/3 hover:bg-white/6 transition-colors">
                  <div className="w-8 h-8 rounded-lg bg-green-600/20 border border-green-500/30 flex items-center justify-center text-sm">🧑‍💼</div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-white truncate">{m.name}</div>
                    <div className="text-xs text-white/40">{m.experience_years}y exp · {(m.expertise_tags || []).slice(0, 2).join(', ')}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* System health */}
      {health && (
        <div className="mt-6 glass-card p-4 flex items-center gap-6">
          <div className="text-xs text-white/40 font-medium">System Status</div>
          {[
            { label: 'API',      status: health.status },
            { label: 'Postgres', status: health.postgres },
            { label: 'Neo4j',    status: health.neo4j },
          ].map(({ label, status }) => (
            <div key={label} className="flex items-center gap-1.5 text-xs">
              <span className={`w-1.5 h-1.5 rounded-full ${status === 'healthy' ? 'bg-green-400' : 'bg-red-400'}`} />
              <span className="text-white/50">{label}</span>
              <span className={status === 'healthy' ? 'text-green-400' : 'text-red-400'}>{status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
