import { useEffect, useState } from 'react'
import { Zap, ChevronDown, AlertCircle, Sparkles, RefreshCw } from 'lucide-react'
import MatchCard from '../components/MatchCard'
import { api } from '../api/client'

export default function MatchPage() {
  const [startups,    setStartups]    = useState([])
  const [selectedId,  setSelectedId]  = useState('')
  const [matches,     setMatches]     = useState(null)
  const [loading,     setLoading]     = useState(false)
  const [loadingList, setLoadingList] = useState(true)
  const [error,       setError]       = useState(null)

  useEffect(() => {
    api.listStartups().then(s => { setStartups(s); setLoadingList(false) }).catch(() => setLoadingList(false))
  }, [])

  const selected = startups.find(s => String(s.id) === String(selectedId))

  const handleMatch = async () => {
    if (!selectedId) return
    setLoading(true); setError(null); setMatches(null)
    try {
      const data = await api.generateMatches(selectedId)
      setMatches(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-container max-w-3xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'rgba(59,130,246,0.2)', border: '1px solid rgba(59,130,246,0.4)' }}>
            <Zap size={20} className="text-blue-400" />
          </div>
          <div>
            <h1 className="section-title">AI Match Engine</h1>
            <p className="text-white/40 text-sm">Google Gemini analyzes profiles and ranks the top 3 mentor matches</p>
          </div>
        </div>
      </div>

      {/* Startup selector + generate */}
      <div className="glass-card p-6 mb-6">
        <label className="label-text">Select Startup</label>
        <div className="flex gap-3">
          <div className="relative flex-1">
            <select id="match-startup-select" value={selectedId}
                    onChange={e => { setSelectedId(e.target.value); setMatches(null); setError(null) }}
                    className="input-field appearance-none pr-10"
                    disabled={loadingList}>
              <option value="">
                {loadingList ? 'Loading startups…' : startups.length === 0 ? 'No startups — add one first' : 'Choose a startup…'}
              </option>
              {startups.map(s => (
                <option key={s.id} value={s.id}>{s.name} ({s.industry || 'Unknown'} · {s.stage || '—'})</option>
              ))}
            </select>
            <ChevronDown size={16} className="absolute right-3 top-1/2 -translate-y-1/2 text-white/30 pointer-events-none" />
          </div>

          <button id="generate-matches-btn" onClick={handleMatch}
                  disabled={!selectedId || loading}
                  className="btn-primary flex items-center gap-2 flex-shrink-0">
            {loading ? (
              <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Matching…</>
            ) : (
              <><Sparkles size={16} /> Generate Matches</>
            )}
          </button>
        </div>

        {/* Selected startup preview */}
        {selected && (
          <div className="mt-4 p-4 rounded-xl bg-white/3 border border-white/5">
            <div className="flex items-start gap-3">
              <div className="text-2xl">🚀</div>
              <div className="flex-1">
                <div className="font-semibold text-white">{selected.name}</div>
                <div className="text-xs text-white/40 mb-2">{selected.industry} · {selected.stage}</div>
                {selected.tags?.length > 0 && (
                  <div className="flex flex-wrap gap-1.5">
                    {selected.tags.map(t => <span key={t} className="tag-badge">{t}</span>)}
                  </div>
                )}
                {selected.clean_description && (
                  <p className="text-sm text-white/50 mt-2 leading-relaxed">{selected.clean_description}</p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Loading animation */}
      {loading && (
        <div className="glass-card p-12 text-center animate-fade-in">
          <div className="w-16 h-16 mx-auto mb-6 rounded-full flex items-center justify-center animate-pulse"
               style={{ background: 'linear-gradient(135deg, rgba(124,92,252,0.3), rgba(192,132,252,0.3))' }}>
            <Sparkles size={28} className="text-brand-400" />
          </div>
          <div className="text-white font-semibold mb-2">Gemini AI is analyzing…</div>
          <div className="text-white/40 text-sm">Comparing startup profile with all mentors and generating ranked matches</div>
          <div className="flex justify-center gap-1.5 mt-6">
            {[0, 1, 2].map(i => (
              <div key={i} className="w-2 h-2 rounded-full bg-brand-500 animate-bounce"
                   style={{ animationDelay: `${i * 150}ms` }} />
            ))}
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="glass-card p-5 border-red-500/20 flex items-start gap-3 animate-fade-in">
          <AlertCircle size={18} className="text-red-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <div className="text-red-300 font-medium text-sm mb-1">Matching failed</div>
            <div className="text-red-400/70 text-sm">{error}</div>
          </div>
          <button onClick={handleMatch} className="text-white/40 hover:text-white transition-colors">
            <RefreshCw size={16} />
          </button>
        </div>
      )}

      {/* Results */}
      {matches && !loading && (
        <div className="animate-fade-in">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-semibold text-white">
                Top {matches.matches.length} Matches for <span className="gradient-text">{matches.startup_name}</span>
              </h2>
              <p className="text-white/40 text-sm mt-0.5">Click a card to expand the AI explanation and accept/reject</p>
            </div>
            <button onClick={handleMatch} className="btn-secondary text-sm flex items-center gap-1.5 px-3 py-1.5">
              <RefreshCw size={14} /> Regenerate
            </button>
          </div>

          {matches.matches.length === 0 ? (
            <div className="glass-card p-8 text-center text-white/40">
              No matches found. Try adding more mentors to the system.
            </div>
          ) : (
            <div className="space-y-4">
              {matches.matches.map((match, i) => (
                <MatchCard key={match.mentor_id} match={match} startupId={matches.startup_id} index={i} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
