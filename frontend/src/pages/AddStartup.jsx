import { useState } from 'react'
import { Rocket, Sparkles, CheckCircle, AlertCircle } from 'lucide-react'
import { api } from '../api/client'

const INDUSTRIES = ['Fintech', 'Healthtech', 'SaaS', 'EdTech', 'CleanTech', 'Cybersecurity', 'Logistics', 'AI/ML', 'E-Commerce', 'Other']
const STAGES     = ['idea', 'pre-seed', 'seed', 'growth', 'scale']

export default function AddStartup() {
  const [form, setForm]       = useState({ name: '', industry: '', stage: '', description: '' })
  const [result, setResult]   = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.name) return
    setLoading(true); setError(null); setResult(null)
    try {
      const data = await api.createStartup(form)
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
          <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'rgba(124,92,252,0.2)', border: '1px solid rgba(124,92,252,0.4)' }}>
            <Rocket size={20} className="text-brand-400" />
          </div>
          <div>
            <h1 className="section-title">Add Startup</h1>
            <p className="text-white/40 text-sm">Gemini AI will enrich your profile automatically</p>
          </div>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="glass-card p-8 mb-6 space-y-5">
        <div>
          <label className="label-text">Startup Name *</label>
          <input id="startup-name" value={form.name} onChange={set('name')} required
                 placeholder="e.g. LendAI" className="input-field" />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label-text">Industry</label>
            <select id="startup-industry" value={form.industry} onChange={set('industry')} className="input-field">
              <option value="">Select industry</option>
              {INDUSTRIES.map(i => <option key={i} value={i}>{i}</option>)}
            </select>
          </div>
          <div>
            <label className="label-text">Stage</label>
            <select id="startup-stage" value={form.stage} onChange={set('stage')} className="input-field">
              <option value="">Select stage</option>
              {STAGES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
        </div>

        <div>
          <label className="label-text">Description</label>
          <textarea id="startup-description" value={form.description} onChange={set('description')}
                    rows={4} placeholder="Describe your startup, its mission, target market, and key differentiators…"
                    className="input-field resize-none" />
        </div>

        {error && (
          <div className="flex items-start gap-2 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-300 text-sm">
            <AlertCircle size={16} className="mt-0.5 flex-shrink-0" /> {error}
          </div>
        )}

        <button id="submit-startup" type="submit" disabled={loading || !form.name}
                className="btn-primary w-full flex items-center justify-center gap-2">
          {loading ? (
            <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Enriching with Gemini AI…</>
          ) : (
            <><Sparkles size={16} /> Create & Enrich with AI</>
          )}
        </button>
      </form>

      {/* Result */}
      {result && (
        <div className="glass-card p-6 border-green-500/30 animate-slide-up">
          <div className="flex items-center gap-2 mb-4 text-green-400 font-semibold">
            <CheckCircle size={18} /> Startup created & enriched!
          </div>

          <div className="space-y-4">
            <div className="flex items-start justify-between">
              <div>
                <div className="text-lg font-bold text-white">{result.name}</div>
                <div className="text-sm text-white/50">{result.industry} · {result.stage}</div>
              </div>
              {result.ai_confidence > 0 && (
                <div className="text-right">
                  <div className="text-2xl font-bold text-brand-400">{Math.round(result.ai_confidence * 100)}%</div>
                  <div className="text-xs text-white/40">AI confidence</div>
                </div>
              )}
            </div>

            {result.tags?.length > 0 && (
              <div>
                <div className="text-xs text-white/40 mb-2">AI-extracted tags</div>
                <div className="flex flex-wrap gap-2">
                  {result.tags.map(tag => <span key={tag} className="tag-badge">{tag}</span>)}
                </div>
              </div>
            )}

            {result.clean_description && (
              <div>
                <div className="text-xs text-white/40 mb-2">AI-improved description</div>
                <p className="text-sm text-white/70 leading-relaxed bg-white/5 rounded-xl p-3">
                  {result.clean_description}
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
