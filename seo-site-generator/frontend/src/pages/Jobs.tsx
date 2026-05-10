import { useState, useEffect } from 'react'
import { Search, ChevronDown, ChevronUp } from 'lucide-react'
import { listJobs } from '../lib/api'
import type { Job } from '../lib/api'
import { JobProgress } from '../components/JobProgress'

export function Jobs() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [search, setSearch] = useState('')
  const [expanded, setExpanded] = useState<string | null>(null)

  useEffect(() => {
    listJobs().then(setJobs)
    const id = setInterval(() => listJobs().then(setJobs), 5000)
    return () => clearInterval(id)
  }, [])

  const filtered = jobs.filter(
    (j) =>
      j.domain.includes(search) ||
      j.id.includes(search) ||
      j.status.includes(search)
  )

  const statusStyles: Record<Job['status'], string> = {
    running: 'bg-sky-500/10 text-sky-400 border-sky-500/20',
    done: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    failed: 'bg-red-500/10 text-red-400 border-red-500/20',
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Job History</h1>
        <p className="text-slate-400 text-sm mt-1">{jobs.length} total jobs</p>
      </div>

      <div className="relative">
        <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by domain, job ID, status..."
          className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-8 pr-3 py-2.5 text-sm text-slate-200 placeholder-slate-600 outline-none focus:border-sky-500 transition-colors"
        />
      </div>

      {filtered.length === 0 ? (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center text-slate-500">
          {jobs.length === 0 ? 'No jobs yet — generate your first site on the Dashboard.' : 'No jobs match your search.'}
        </div>
      ) : (
        <div className="space-y-2">
          {filtered.map((job) => (
            <div key={job.id} className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
              <button
                className="w-full flex items-center justify-between px-5 py-4 hover:bg-slate-800/50 transition-colors text-left"
                onClick={() => setExpanded(expanded === job.id ? null : job.id)}
              >
                <div className="flex items-center gap-4">
                  <span className="font-mono text-sm text-slate-400">#{job.id}</span>
                  <span className="text-slate-200 font-medium">{job.domain}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${statusStyles[job.status]}`}>
                    {job.status}
                  </span>
                </div>
                <div className="flex items-center gap-4 text-sm text-slate-500">
                  <span>{job.pages.length} pages</span>
                  {expanded === job.id ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </div>
              </button>

              {expanded === job.id && (
                <div className="px-5 pb-5 border-t border-slate-800 pt-4">
                  <JobProgress job={job} totalRows={job.pages.length || 1} />
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
