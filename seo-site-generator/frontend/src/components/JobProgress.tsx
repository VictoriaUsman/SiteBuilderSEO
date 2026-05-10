import { useState } from 'react'
import { CheckCircle, AlertCircle, Clock, ChevronRight } from 'lucide-react'
import type { Job, PageResult } from '../lib/api'
import { ContentPreviewModal } from './ContentPreviewModal'

interface Props {
  job: Job
  totalRows: number
}

function StatusIcon({ status }: { status: Job['status'] }) {
  if (status === 'done') return <CheckCircle size={16} className="text-emerald-400" />
  if (status === 'failed') return <AlertCircle size={16} className="text-red-400" />
  return <Clock size={16} className="text-sky-400 animate-pulse" />
}

function StatusBadge({ status }: { status: Job['status'] }) {
  const styles = {
    running: 'bg-sky-500/10 text-sky-400 border-sky-500/20',
    done: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    failed: 'bg-red-500/10 text-red-400 border-red-500/20',
  }
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${styles[status]}`}>
      <StatusIcon status={status} />
      {status}
    </span>
  )
}

export function JobProgress({ job, totalRows }: Props) {
  const [preview, setPreview] = useState<PageResult | null>(null)

  const pct = totalRows > 0 ? Math.round((job.pages.length / totalRows) * 100) : 0
  const passed = job.pages.filter((p) => p.valid).length
  const failed = job.pages.filter((p) => !p.valid).length

  return (
    <>
      <div className="space-y-5">
        {/* Header stats */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="font-mono text-sm text-slate-400">Job #{job.id}</span>
            <StatusBadge status={job.status} />
          </div>
          <div className="flex gap-4 text-sm">
            <span className="text-emerald-400">{passed} passed</span>
            {failed > 0 && <span className="text-amber-400">{failed} warned</span>}
          </div>
        </div>

        {/* Progress bar */}
        <div>
          <div className="flex justify-between text-xs text-slate-500 mb-1.5">
            <span>{job.pages.length} / {totalRows} pages</span>
            <span>{pct}%</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${
                job.status === 'failed' ? 'bg-red-500' : 'bg-sky-500'
              }`}
              style={{ width: `${pct}%` }}
            />
          </div>
        </div>

        {/* Per-page results */}
        {job.pages.length > 0 && (
          <div className="space-y-1.5">
            {job.pages.map((page) => (
              <button
                key={page.slug}
                onClick={() => setPreview(page)}
                className="w-full flex items-center justify-between bg-slate-800/50 hover:bg-slate-800 border border-slate-700/50 rounded-lg px-4 py-2.5 transition-colors group text-left"
              >
                <div className="flex items-center gap-3">
                  {page.valid ? (
                    <CheckCircle size={14} className="text-emerald-400 flex-shrink-0" />
                  ) : (
                    <AlertCircle size={14} className="text-amber-400 flex-shrink-0" />
                  )}
                  <span className="font-mono text-sm text-slate-300">/{page.slug}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-500 group-hover:text-sky-400 transition-colors">Preview</span>
                  <ChevronRight size={14} className="text-slate-600 group-hover:text-sky-400 transition-colors" />
                </div>
              </button>
            ))}
          </div>
        )}

        {/* Log */}
        {job.logs.length > 0 && (
          <div>
            <p className="text-xs text-slate-500 mb-1.5 font-medium uppercase tracking-wider">Logs</p>
            <div className="bg-slate-950 rounded-lg p-3 font-mono text-xs text-emerald-400 max-h-40 overflow-y-auto space-y-0.5">
              {job.logs.map((line, i) => (
                <p key={i} className={line.startsWith('ERROR') ? 'text-red-400' : ''}>
                  {line}
                </p>
              ))}
            </div>
          </div>
        )}
      </div>

      {preview && <ContentPreviewModal page={preview} onClose={() => setPreview(null)} />}
    </>
  )
}
