import { useState } from 'react'
import { Users, X, Sparkles, CheckCircle, AlertCircle, Plus } from 'lucide-react'
import { api } from '../api/client'

export default function AddMentor() {
  const [form, setForm]       = useState({ name: '', expertise_tags: [], experience_years: '', bio: '' })
  const [tagInput, setTagInput] = useState('')
  const [result, setResult]   = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)

  const addTag = () => {
    const t = tagInput.trim()
    if (t && !form.expertise_tags.includes(t)) {
      setForm(f => ({ ...f, expertise_tags: [...f.expertise_tags, t] }))
    }
    setTagInput('')
  }

  const removeTag = (tag) => setForm(f => ({ ...f, expertise_tags: f.expertise_tags.filter(t => t !== tag) }))

  const handleTagKeyDown = (e) => {
    if (e.key === 'Enter') { e.preventDefault(); addTag() }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.name) return
    setLoading(true); setError(null); setResult(null)
    try {
      const data = await api.createMentor({
        name: form.name,
        expertise_tags: form.expertise_tags,
        experience_years: parseInt(form.experience_years) || 0,
        bio: form.bio,
      })
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  return (
    <div className="page-container max-w-2xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'rgba(16,185,129,0.2)', border: '1px solid rgba(16,185,129,0.4)' }}>
            <Users size={20} className="text-green-400" />
          </div>
          <div>
            <h1 className="section-title">Add Mentor</h1>
            <p className="text-white/40 text-sm">Gemini AI will normalize expertise and improve the bio</p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="glass-card p-8 mb-6 space-y-5">
        <div>
          <label className="label-text">Mentor Name *</label>
          <input id="mentor-name" value={form.name} onChange={set('name')} required
                 placeholder="e.g. Sarah Chen" className="input-field" />
        </div>

        <div>
          <label className="label-text">Experience Years</label>
          <input id="mentor-experience" type="number" min="0" max="50"
                 value={form.experience_years} onChange={set('experience_years')}
                 placeholder="e.g. 10" className="input-field" />
        </div>

        {/* Tag input */}
        <div>
          <label className="label-text">Expertise Tags</label>
          <div className="flex gap-2 mb-2">
            <input id="mentor-tag-input" value={tagInput} onChange={e => setTagInput(e.target.value)}
                   onKeyDown={handleTagKeyDown}
                   placeholder="Add tag (press Enter)…" className="input-field flex-1" />
            <button type="button" onClick={addTag} className="btn-secondary px-3 py-2">
              <Plus size={16} />
            </button>
          </div>
          {form.expertise_tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {form.expertise_tags.map(tag => (
                <span key={tag} className="tag-badge flex items-center gap-1.5">
                  {tag}
                  <button type="button" onClick={() => removeTag(tag)} className="hover:text-white transition-colors">
                    <X size={10} />
                  </button>
                </span>
              ))}
            </div>
          )}
        </div>

        <div>
          <label className="label-text">Bio</label>
          <textarea id="mentor-bio" value={form.bio} onChange={set('bio')} rows={4}
                    placeholder="Describe your background, achievements, and what kind of startups you like to mentor…"
                    className="input-field resize-none" />
        </div>

        {error && (
          <div className="flex items-start gap-2 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-300 text-sm">
            <AlertCircle size={16} className="mt-0.5 flex-shrink-0" /> {error}
          </div>
        )}

        <button id="submit-mentor" type="submit" disabled={loading || !form.name}
                className="btn-primary w-full flex items-center justify-center gap-2">
          {loading ? (
            <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Enriching with Gemini AI…</>
          ) : (
            <><Sparkles size={16} /> Create & Enrich with AI</>
          )}
        </button>
      </form>

      {result && (
        <div className="glass-card p-6 border-green-500/30 animate-slide-up">
          <div className="flex items-center gap-2 mb-4 text-green-400 font-semibold">
            <CheckCircle size={18} /> Mentor created & enriched!
          </div>
          <div className="space-y-4">
            <div>
              <div className="text-lg font-bold text-white">{result.name}</div>
              <div className="text-sm text-white/50">{result.experience_years} years experience</div>
            </div>

            {result.expertise_tags?.length > 0 && (
              <div>
                <div className="text-xs text-white/40 mb-2">AI-normalized expertise tags</div>
                <div className="flex flex-wrap gap-2">
                  {result.expertise_tags.map(tag => <span key={tag} className="tag-badge">{tag}</span>)}
                </div>
              </div>
            )}

            {result.clean_bio && (
              <div>
                <div className="text-xs text-white/40 mb-2">AI-improved bio</div>
                <p className="text-sm text-white/70 leading-relaxed bg-white/5 rounded-xl p-3">{result.clean_bio}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
