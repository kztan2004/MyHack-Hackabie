export default function StatCard({ icon: Icon, label, value, color = 'brand', trend }) {
  const colors = {
    brand:  { bg: 'rgba(124,92,252,0.15)', border: 'rgba(124,92,252,0.3)', icon: '#c084fc' },
    green:  { bg: 'rgba(16,185,129,0.15)', border: 'rgba(16,185,129,0.3)', icon: '#6ee7b7' },
    blue:   { bg: 'rgba(59,130,246,0.15)', border: 'rgba(59,130,246,0.3)', icon: '#93c5fd' },
    yellow: { bg: 'rgba(234,179,8,0.15)',  border: 'rgba(234,179,8,0.3)',  icon: '#fde047' },
  }
  const c = colors[color] || colors.brand

  return (
    <div className="glass-card p-6 animate-fade-in hover:border-white/20 transition-all duration-300 group cursor-default">
      <div className="flex items-start justify-between mb-4">
        <div className="w-11 h-11 rounded-xl flex items-center justify-center"
             style={{ background: c.bg, border: `1px solid ${c.border}` }}>
          <Icon size={20} style={{ color: c.icon }} />
        </div>
        {trend && (
          <span className="text-xs px-2 py-0.5 rounded-full bg-green-500/15 text-green-400 border border-green-500/20">
            {trend}
          </span>
        )}
      </div>
      <div className="text-3xl font-bold text-white mb-1 group-hover:gradient-text transition-all">
        {value ?? '—'}
      </div>
      <div className="text-sm text-white/50">{label}</div>
    </div>
  )
}
