import { NavLink } from 'react-router-dom'
import { Network, Plus, Users, Zap, GitBranch } from 'lucide-react'

const links = [
  { to: '/',            label: 'Dashboard', icon: Network   },
  { to: '/add-startup', label: 'Add Startup', icon: Plus    },
  { to: '/add-mentor',  label: 'Add Mentor',  icon: Users   },
  { to: '/match',       label: 'AI Match',    icon: Zap     },
  { to: '/graph',       label: 'Graph View',  icon: GitBranch },
]

export default function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 h-16 flex items-center px-6 justify-between"
         style={{ background: 'rgba(5,5,16,0.8)', backdropFilter: 'blur(20px)', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
      {/* Logo */}
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-lg flex items-center justify-center"
             style={{ background: 'linear-gradient(135deg, #7c5cfc, #c084fc)' }}>
          <Network size={16} className="text-white" />
        </div>
        <span className="font-bold text-base tracking-tight">
          <span className="gradient-text">EcosystemGraph</span>
          <span className="text-white/40 ml-1 font-normal">AI</span>
        </span>
      </div>

      {/* Nav Links */}
      <div className="flex items-center gap-1">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                isActive
                  ? 'bg-brand-600/30 text-brand-300 border border-brand-500/30'
                  : 'text-white/50 hover:text-white/80 hover:bg-white/5'
              }`
            }
          >
            <Icon size={14} />
            {label}
          </NavLink>
        ))}
      </div>

      {/* Status dot */}
      <div className="flex items-center gap-2 text-xs text-white/40">
        <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse-slow" />
        Live
      </div>
    </nav>
  )
}
