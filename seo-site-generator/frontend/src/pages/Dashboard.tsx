import { useState } from 'react'
import { Globe, Cpu, FileOutput, FileText, RefreshCw } from 'lucide-react'
import type { Row } from '../lib/api'
import { startJob } from '../lib/api'
import { CsvUploader } from '../components/CsvUploader'
import { CsvEditor } from '../components/CsvEditor'
import { JobProgress } from '../components/JobProgress'
import { LinkGraph } from '../components/LinkGraph'
import { useJobSocket } from '../hooks/useJobSocket'

type Step = 'upload' | 'configure' | 'running' | 'done'

export function Dashboard() {
  const [step, setStep] = useState<Step>('upload')
  const [rows, setRows] = useState<Row[]>([])
  const [domain, setDomain] = useState('')
  const [provider, setProvider] = useState<'gemini' | 'openai'>('gemini')
  const [status, setStatus] = useState<'draft' | 'publish'>('draft')
  const [postType, setPostType] = useState<'posts' | 'pages'>('posts')
  const [dryRun, setDryRun] = useState(true)
  const [jobId, setJobId] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const job = useJobSocket(jobId)

  const handleRows = (r: Row[]) => {
    setRows(r)
    if (r.length > 0) setStep('configure')
  }

  const handleGenerate = async () => {
    if (!domain.trim() || rows.length === 0) return
    setLoading(true)
    setError('')
    try {
      const { job_id } = await startJob({ rows, domain, provider, status, post_type: postType, dry_run: dryRun })
      setJobId(job_id)
      setStep('running')
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to start job')
    } finally {
      setLoading(false)
    }
  }

  const reset = () => {
    setStep('upload')
    setRows([])
    setDomain('')
    setJobId(null)
    setError('')
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Generate Site</h1>
        <p className="text-slate-400 text-sm mt-1">Upload keywords, configure, and publish pages to WordPress</p>
      </div>

      {/* Steps indicator */}
      <div className="flex items-center gap-2 text-sm">
        {(['upload', 'configure', 'running'] as Step[]).map((s, i) => {
          const labels = ['1. Upload CSV', '2. Configure', '3. Generate']
          const done = step === 'running' ? i < 2 : step === 'configure' ? i < 1 : false
          const active = step === s
          return (
            <span key={s} className={`flex items-center gap-2 ${active ? 'text-sky-400' : done ? 'text-emerald-400' : 'text-slate-600'}`}>
              {i > 0 && <span className="text-slate-700">›</span>}
              {labels[i]}
            </span>
          )
        })}
      </div>

      {/* Upload step */}
      {step === 'upload' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
          <CsvUploader onRows={handleRows} />
          {rows.length === 0 && (
            <p className="text-center text-sm text-slate-600">
              No CSV yet?{' '}
              <button
                className="text-sky-400 underline underline-offset-2"
                onClick={() =>
                  handleRows([
                    { keyword: 'roof repair', city: 'Dallas', service: 'Roof Repair' },
                    { keyword: 'emergency roofing', city: 'Dallas', service: 'Emergency Roofing' },
                    { keyword: 'plumber', city: 'Austin', service: 'Plumbing Services' },
                  ])
                }
              >
                load sample data
              </button>
            </p>
          )}
        </div>
      )}

      {/* Configure step */}
      {step === 'configure' && (
        <div className="space-y-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <div className="flex items-center justify-between mb-1">
              <h2 className="text-sm font-semibold text-slate-300">Keyword Rows</h2>
              <button onClick={() => setStep('upload')} className="text-xs text-slate-500 hover:text-slate-300">
                Re-upload
              </button>
            </div>
            <CsvEditor rows={rows} onChange={setRows} />
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h2 className="text-sm font-semibold text-slate-300">Configuration</h2>

            <div>
              <label className="text-xs text-slate-400 mb-1.5 block">Domain</label>
              <div className="relative">
                <Globe size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  value={domain}
                  onChange={(e) => setDomain(e.target.value)}
                  placeholder="bestroofingdallas.com"
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-8 pr-3 py-2.5 text-sm text-slate-200 placeholder-slate-600 outline-none focus:border-sky-500 transition-colors"
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="text-xs text-slate-400 mb-1.5 block flex items-center gap-1.5">
                  <Cpu size={12} /> AI Provider
                </label>
                <select
                  value={provider}
                  onChange={(e) => setProvider(e.target.value as 'gemini' | 'openai')}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-slate-200 outline-none focus:border-sky-500"
                >
                  <option value="gemini">Gemini</option>
                  <option value="openai">OpenAI</option>
                </select>
              </div>
              <div>
                <label className="text-xs text-slate-400 mb-1.5 block flex items-center gap-1.5">
                  <FileText size={12} /> Post Type
                </label>
                <select
                  value={postType}
                  onChange={(e) => setPostType(e.target.value as 'posts' | 'pages')}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-slate-200 outline-none focus:border-sky-500"
                >
                  <option value="posts">Post</option>
                  <option value="pages">Page</option>
                </select>
              </div>
              <div>
                <label className="text-xs text-slate-400 mb-1.5 block flex items-center gap-1.5">
                  <FileOutput size={12} /> Publish Status
                </label>
                <select
                  value={status}
                  onChange={(e) => setStatus(e.target.value as 'draft' | 'publish')}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-slate-200 outline-none focus:border-sky-500"
                >
                  <option value="draft">Draft</option>
                  <option value="publish">Publish</option>
                </select>
              </div>
              <div>
                <label className="text-xs text-slate-400 mb-1.5 block">Mode</label>
                <label className="flex items-center gap-2 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 cursor-pointer hover:border-slate-600 transition-colors">
                  <input
                    type="checkbox"
                    checked={dryRun}
                    onChange={(e) => setDryRun(e.target.checked)}
                    className="w-3.5 h-3.5 accent-sky-400"
                  />
                  <span className="text-sm text-slate-300">Dry run</span>
                </label>
              </div>
            </div>

            {error && <p className="text-red-400 text-sm">{error}</p>}

            <button
              onClick={handleGenerate}
              disabled={!domain.trim() || rows.length === 0 || loading}
              className="w-full bg-sky-500 hover:bg-sky-400 disabled:opacity-40 disabled:cursor-not-allowed text-slate-950 font-bold rounded-lg py-3 text-sm transition-colors"
            >
              {loading ? 'Starting...' : `Generate ${rows.length} Pages`}
            </button>
          </div>
        </div>
      )}

      {/* Running/done step */}
      {(step === 'running' || step === 'done') && job && (
        <div className="space-y-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <JobProgress job={job} totalRows={rows.length} />
          </div>

          {job.pages.length > 1 && (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
              <LinkGraph pages={job.pages} />
            </div>
          )}

          {job.status !== 'running' && (
            <button
              onClick={reset}
              className="flex items-center gap-2 text-sm text-slate-400 hover:text-slate-200 transition-colors"
            >
              <RefreshCw size={14} /> Start new job
            </button>
          )}
        </div>
      )}

      {/* Waiting for first job update */}
      {step === 'running' && !job && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 text-center">
          <div className="inline-flex items-center gap-2 text-sky-400 text-sm">
            <RefreshCw size={16} className="animate-spin" /> Connecting to job #{jobId}...
          </div>
        </div>
      )}
    </div>
  )
}
