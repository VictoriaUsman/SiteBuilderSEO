import { X, CheckCircle, AlertCircle, ExternalLink } from 'lucide-react'
import type { PageResult } from '../lib/api'

interface Props {
  page: PageResult
  onClose: () => void
}

export function ContentPreviewModal({ page, onClose }: Props) {
  const c = page.content

  return (
    <div
      className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-3xl max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-slate-700 sticky top-0 bg-slate-900 z-10">
          <div className="flex items-center gap-3">
            {page.valid ? (
              <CheckCircle size={18} className="text-emerald-400" />
            ) : (
              <AlertCircle size={18} className="text-amber-400" />
            )}
            <span className="font-mono text-sm text-sky-400">/{page.slug}</span>
          </div>
          <div className="flex items-center gap-3">
            <a
              href={page.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-sky-400 transition-colors"
            >
              <ExternalLink size={14} />
              Open
            </a>
            <button onClick={onClose} className="text-slate-500 hover:text-slate-200 transition-colors">
              <X size={20} />
            </button>
          </div>
        </div>

        {c ? (
          <div className="p-5 space-y-5">
            {/* SEO Meta */}
            <section className="space-y-2">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500">SEO</h3>
              <div className="space-y-2">
                <div>
                  <p className="text-xs text-slate-500 mb-0.5">Title tag</p>
                  <p className="text-white font-medium">{c.title_tag}</p>
                  <p className={`text-xs mt-0.5 ${c.title_tag.length > 60 ? 'text-red-400' : 'text-slate-500'}`}>
                    {c.title_tag.length}/60 chars
                  </p>
                </div>
                <div>
                  <p className="text-xs text-slate-500 mb-0.5">Meta description</p>
                  <p className="text-slate-300 text-sm">{c.meta_description}</p>
                  <p className={`text-xs mt-0.5 ${c.meta_description.length > 160 ? 'text-red-400' : 'text-slate-500'}`}>
                    {c.meta_description.length}/160 chars
                  </p>
                </div>
              </div>
            </section>

            {/* Content */}
            <section className="space-y-3">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500">Content</h3>
              <div className="bg-slate-800 rounded-xl p-4 space-y-3">
                <h1 className="text-xl font-bold text-white">{c.h1}</h1>
                <p className="text-slate-300 text-sm leading-relaxed">{c.intro_paragraph}</p>
                {c.h2_sections.map((s, i) => (
                  <div key={i}>
                    <h2 className="font-semibold text-white text-sm mt-3">{s.heading}</h2>
                    <p className="text-slate-400 text-sm leading-relaxed mt-1">{s.content}</p>
                  </div>
                ))}
              </div>
            </section>

            {/* FAQ */}
            {c.faq?.length > 0 && (
              <section className="space-y-2">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500">FAQ ({c.faq.length} questions)</h3>
                <div className="space-y-2">
                  {c.faq.map((q, i) => (
                    <div key={i} className="bg-slate-800/50 rounded-lg p-3">
                      <p className="text-sm font-medium text-white">{q.question}</p>
                      <p className="text-sm text-slate-400 mt-1">{q.answer}</p>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Internal links */}
            {c.internal_link_suggestions?.length > 0 && (
              <section className="space-y-2">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500">Internal Links</h3>
                <div className="flex flex-wrap gap-2">
                  {c.internal_link_suggestions.map((slug) => (
                    <span key={slug} className="bg-slate-800 text-sky-400 text-xs font-mono px-2 py-1 rounded">
                      /{slug}
                    </span>
                  ))}
                </div>
              </section>
            )}

            {/* CTA */}
            <section>
              <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">CTA</h3>
              <div className="bg-sky-500/10 border border-sky-500/20 rounded-lg p-3 text-sky-300 text-sm">
                {c.cta}
              </div>
            </section>
          </div>
        ) : (
          <div className="p-8 text-center text-slate-500">No content preview available</div>
        )}
      </div>
    </div>
  )
}
