// Centralised API client — proxies via Vite to http://localhost:8000
const BASE = '/api'

async function request(method, path, body = null) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  }
  if (body) opts.body = JSON.stringify(body)

  const res = await fetch(`${BASE}${path}`, opts)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export const api = {
  // Startups
  createStartup:  (data)       => request('POST', '/startup', data),
  listStartups:   ()           => request('GET',  '/startups'),
  getStartup:     (id)         => request('GET',  `/startup/${id}`),

  // Mentors
  createMentor:   (data)       => request('POST', '/mentor', data),
  listMentors:    ()           => request('GET',  '/mentors'),
  getMentor:      (id)         => request('GET',  `/mentor/${id}`),

  // Matching
  generateMatches: (startupId) => request('POST', `/match/${startupId}`),

  // Feedback
  submitFeedback: (data)       => request('POST', '/feedback', data),

  // Graph
  getGraph:       ()           => request('GET',  '/graph'),

  // Health
  health:         ()           => request('GET',  '/health'),
}
