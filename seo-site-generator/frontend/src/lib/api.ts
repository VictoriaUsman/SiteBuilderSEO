export interface Row {
  keyword: string
  city: string
  service: string
}

export interface PageResult {
  slug: string
  url: string
  valid: boolean
  content?: PageContent
}

export interface PageContent {
  title_tag: string
  meta_description: string
  slug: string
  h1: string
  intro_paragraph: string
  h2_sections: { heading: string; content: string }[]
  faq: { question: string; answer: string }[]
  cta: string
  image_alt_text: string
  internal_link_suggestions: string[]
}

export interface Job {
  id: string
  domain: string
  status: 'running' | 'done' | 'failed'
  logs: string[]
  pages: PageResult[]
}

export interface GeneratePayload {
  rows: Row[]
  domain: string
  provider: 'gemini' | 'openai'
  status: 'publish' | 'draft'
  post_type: 'posts' | 'pages'
  dry_run: boolean
}

const BASE = ''

export async function startJob(payload: GeneratePayload): Promise<{ job_id: string }> {
  const fd = new FormData()
  const csv = ['keyword,city,service', ...payload.rows.map(r => `${r.keyword},${r.city},${r.service}`)].join('\n')
  fd.append('csv_file', new Blob([csv], { type: 'text/csv' }), 'keywords.csv')
  fd.append('domain', payload.domain)
  fd.append('provider', payload.provider)
  fd.append('status', payload.status)
  fd.append('post_type', payload.post_type)
  fd.append('dry_run', String(payload.dry_run))

  const res = await fetch(`${BASE}/generate`, { method: 'POST', body: fd })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getJob(id: string): Promise<Job> {
  const res = await fetch(`${BASE}/jobs/${id}`)
  if (!res.ok) throw new Error('Job not found')
  return res.json()
}

export async function listJobs(): Promise<Job[]> {
  const res = await fetch(`${BASE}/api/jobs`)
  if (!res.ok) return []
  return res.json()
}
