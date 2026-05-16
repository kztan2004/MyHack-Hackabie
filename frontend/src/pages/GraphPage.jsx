import { useEffect, useState } from 'react'
import { GitBranch, RefreshCw, AlertCircle, Info } from 'lucide-react'
import GraphView from '../components/GraphView'
import { api } from '../api/client'

export default function GraphPage() {
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)

  const load = () => {
    setLoading(true); setError(null)
    api.getGraph()
      .then(d => { setData(d); setLoading(false) })
      .catch(e => { setError(e.message); setLoading(false) })
  }

  useEffect(() => { load() }, [])

  const statusCounts = data?.edges?.reduce((acc, e) => {
    acc[e.status] = (acc[e.status] || 0) + 1
    return acc
  }, {}) ?? {}

  return (
    <div className="page-container">
      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'rgba(96,165,250,0.2)', border: '1px solid rgba(96,165,250,0.4)' }}>
              <GitBranch size={20} className="text-blue-400" />
            </div>
            <div>
              <h1 className="section-title">Ecosystem Graph</h1>
              <p className="text-white/40 text-sm">Live view of all AI-generated relationships in Neo4j</p>
            </div>
          </div>
        </div>

        <button onClick={load} disabled={loading}
                className="btn-secondary flex items-center gap-2 text-sm">
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          {loading ? 'Loading…' : 'Refresh'}
        </button>
      </div>

      {/* Stats bar */}
      {data && (
        <div className="flex flex-wrap gap-4 mb-6">
          {[
            { label: 'Startups',  value: data.nodes?.filter(n => n.type === 'startup').length ?? 0,  color: '#c084fc' },
            { label: 'Mentors',   value: data.nodes?.filter(n => n.type === 'mentor').length ?? 0,   color: '#6ee7b7' },
            { label: 'Total Edges', value: data.edge_count ?? 0, color: '#93c5fd' },
            { label: 'Accepted',  value: statusCounts.accepted ?? 0,  color: '#6ee7b7' },
            { label: 'Pending',   value: statusCounts.pending ?? 0,   color: '#fde047' },
            { label: 'Rejected',  value: statusCounts.rejected ?? 0,  color: '#fca5a5' },
          ].map(({ label, value, color }) => (
            <div key={label} className="glass-card px-4 py-3 flex items-center gap-3">
              <div className="w-2 h-2 rounded-full" style={{ background: color }} />
              <div>
                <div className="text-lg font-bold text-white">{value}</div>
                <div className="text-xs text-white/40">{label}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Legend */}
      <div className="flex items-center gap-6 mb-4 text-xs text-white/50">
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-full border-2" style={{ borderColor: 'rgba(124,92,252,0.8)', background: 'rgba(124,92,252,0.2)' }} />
          🚀 Startup
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-full border-2" style={{ borderColor: 'rgba(16,185,129,0.8)', background: 'rgba(16,185,129,0.2)' }} />
          🧑‍💼 Mentor
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-6 h-0.5 bg-brand-500/60" style={{ borderTop: '2px dashed rgba(124,92,252,0.4)' }} />
          Pending match
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-6 h-0.5" style={{ background: 'rgba(16,185,129,0.6)' }} />
          Accepted match
        </div>
        <div className="flex items-center gap-1.5">
          <Info size={12} />
          Drag nodes · Scroll to zoom
        </div>
      </div>

      {/* Graph */}
      {loading && (
        <div className="glass-card p-16 text-center animate-fade-in">
          <div className="w-12 h-12 border-2 border-brand-500/30 border-t-brand-500 rounded-full animate-spin mx-auto mb-4" />
          <div className="text-white/40 text-sm">Loading graph from Neo4j…</div>
        </div>
      )}

      {error && !loading && (
        <div className="glass-card p-8 border-red-500/20 text-center">
          <AlertCircle size={32} className="text-red-400 mx-auto mb-3" />
          <div className="text-red-300 font-medium mb-1">Failed to load graph</div>
          <div className="text-red-400/60 text-sm mb-4">{error}</div>
          <button onClick={load} className="btn-secondary text-sm">Try again</button>
        </div>
      )}

      {!loading && !error && data && data.node_count === 0 && (
        <div className="glass-card p-16 text-center">
          <div className="text-4xl mb-4">🌐</div>
          <div className="text-white font-semibold mb-2">No graph data yet</div>
          <p className="text-white/40 text-sm">Add startups and mentors, then generate matches to populate the graph.</p>
        </div>
      )}

      {!loading && !error && data && data.node_count > 0 && (
        <GraphView data={data} height={600} />
      )}
    </div>
  )
}
