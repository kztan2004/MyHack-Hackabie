import { useState } from 'react'
import { ThumbsUp, ThumbsDown, Star, ChevronDown, ChevronUp } from 'lucide-react'
import { api } from '../api/client'

export default function MatchCard({ match, startupId, index, onFeedback }) {
  const [expanded, setExpanded] = useState(index === 0)
  const [status, setStatus] = useState('pending')
  const [loading, setLoading] = useState(null)

  const scorePercent = Math.round(match.score * 100)

  const handleFeedback = async (action) => {
    setLoading(action)
    try {
      await api.submitFeedback({
        startup_id: startupId,
        mentor_id: match.mentor_id,
        action,
      })
      setStatus(action)
      onFeedback?.(match.mentor_id, action)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(null)
    }
  }

  const rankColors = ['from-yellow-400 to-orange-400', 'from-slate-300 to-slate-400', 'from-orange-600 to-orange-700']
  const rankLabels = ['#1 Best Match', '#2 Great Match', '#3 Good Match']

  return (
    <div className={`glass-card overflow-hidden animate-slide-up transition-all duration-300 ${
      status === 'accepted' ? 'border-green-500/30' : status === 'rejected' ? 'border-red-500/20 opacity-60' : 'hover:border-white/20'
    }`} style={{ animationDelay: `${index * 100}ms` }}>

      {/* Header */}
      <div className="p-5 flex items-start gap-4">
        {/* Rank badge */}
        <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${rankColors[index] || 'from-brand-500 to-brand-600'} flex items-center justify-center text-white font-bold text-sm flex-shrink-0`}>
          {index + 1}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-semibold text-white text-base">{match.mentor_name}</h3>
            <span className="text-xs text-white/30">{rankLabels[index]}</span>
          </div>

          {/* Tags */}
          <div className="flex flex-wrap gap-1.5 mb-3">
            {(match.expertise_tags || []).slice(0, 4).map(tag => (
              <span key={tag} className="tag-badge">{tag}</span>
            ))}
            <span className="text-xs text-white/30 self-center">
              {match.experience_years}y exp
            </span>
          </div>

          {/* Score bar */}
          <div className="flex items-center gap-3">
            <div className="score-bar-track flex-1">
              <div className="score-bar-fill" style={{ width: `${scorePercent}%` }} />
            </div>
            <span className="text-sm font-bold text-brand-300 flex-shrink-0">{scorePercent}%</span>
          </div>
        </div>

        {/* Status + expand */}
        <div className="flex flex-col items-end gap-2">
          {status !== 'pending' && (
            <span className={`status-${status}`}>
              {status === 'accepted' ? '✓ Accepted' : '✗ Rejected'}
            </span>
          )}
          <button
            onClick={() => setExpanded(e => !e)}
            className="text-white/30 hover:text-white/70 transition-colors"
          >
            {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
        </div>
      </div>

      {/* Expanded: AI Explanation + Actions */}
      {expanded && (
        <div className="px-5 pb-5 border-t border-white/5 pt-4">
          <div className="mb-4">
            <div className="text-xs text-brand-400 font-medium mb-2 flex items-center gap-1">
              <Star size={12} /> AI Explanation
            </div>
            <p className="text-sm text-white/70 leading-relaxed">{match.reason}</p>
          </div>

          {status === 'pending' && (
            <div className="flex gap-3">
              <button
                id={`accept-${match.mentor_id}`}
                onClick={() => handleFeedback('accepted')}
                disabled={!!loading}
                className="btn-success flex items-center gap-2 flex-1 justify-center"
              >
                <ThumbsUp size={14} />
                {loading === 'accepted' ? 'Saving…' : 'Accept Match'}
              </button>
              <button
                id={`reject-${match.mentor_id}`}
                onClick={() => handleFeedback('rejected')}
                disabled={!!loading}
                className="btn-danger flex items-center gap-2 flex-1 justify-center"
              >
                <ThumbsDown size={14} />
                {loading === 'rejected' ? 'Saving…' : 'Reject'}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
