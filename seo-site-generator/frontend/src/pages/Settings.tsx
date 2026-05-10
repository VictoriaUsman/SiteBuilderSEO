import { useState } from 'react'
import { Save, Eye, EyeOff, CheckCircle } from 'lucide-react'

interface Field {
  key: string
  label: string
  placeholder: string
  secret?: boolean
  hint?: string
}

interface Section {
  heading: string
  fields: Field[]
}

const SECTIONS: Section[] = [
  {
    heading: 'WordPress.com',
    fields: [
      { key: 'WP_ACCESS_TOKEN', label: 'OAuth Access Token', placeholder: 'Paste token from authorize URL', secret: true, hint: 'Get from: public-api.wordpress.com/oauth2/authorize' },
      { key: 'WP_SITE', label: 'Site domain', placeholder: 'allaroundph.wordpress.com' },
    ],
  },
  {
    heading: 'Self-hosted WordPress (alternative)',
    fields: [
      { key: 'WP_URL', label: 'WordPress URL', placeholder: 'https://yoursite.com' },
      { key: 'WP_USERNAME', label: 'Username', placeholder: 'admin' },
      { key: 'WP_APP_PASSWORD', label: 'Application Password', placeholder: 'xxxx xxxx xxxx xxxx xxxx xxxx', secret: true },
    ],
  },
  {
    heading: 'AI & Media',
    fields: [
      { key: 'GEMINI_API_KEY', label: 'Gemini API Key', placeholder: 'AIza...', secret: true },
      { key: 'OPENAI_API_KEY', label: 'OpenAI API Key', placeholder: 'sk-...', secret: true },
      { key: 'PEXELS_API_KEY', label: 'Pexels API Key', placeholder: 'Your Pexels key', secret: true },
    ],
  },
]


export function Settings() {
  const [values, setValues] = useState<Record<string, string>>({})
  const [visible, setVisible] = useState<Record<string, boolean>>({})
  const [saved, setSaved] = useState(false)

  const set = (k: string, v: string) => setValues((prev) => ({ ...prev, [k]: v }))
  const toggle = (k: string) => setVisible((prev) => ({ ...prev, [k]: !prev[k] }))

  const handleSave = async () => {
    // POST to backend to update .env — this is a dev-time helper
    await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(values),
    })
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  return (
    <div className="max-w-xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <p className="text-slate-400 text-sm mt-1">API keys and WordPress credentials</p>
      </div>

      <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4 text-sm text-amber-300">
        These values are written to your <code className="font-mono">.env</code> file on the server. Do not expose this page publicly.
      </div>

      {SECTIONS.map((section) => (
        <div key={section.heading} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-5">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-500">{section.heading}</h2>
          {section.fields.map((f) => (
          <div key={f.key}>
            <label className="text-xs text-slate-400 mb-1.5 block font-medium">{f.label}</label>
            <div className="relative">
              <input
                type={f.secret && !visible[f.key] ? 'password' : 'text'}
                value={values[f.key] ?? ''}
                onChange={(e) => set(f.key, e.target.value)}
                placeholder={f.placeholder}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-slate-200 placeholder-slate-600 outline-none focus:border-sky-500 transition-colors pr-10"
              />
              {f.secret && (
                <button
                  onClick={() => toggle(f.key)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
                >
                  {visible[f.key] ? <EyeOff size={14} /> : <Eye size={14} />}
                </button>
              )}
            </div>
            {f.hint && <p className="text-xs text-slate-600 mt-1">{f.hint}</p>}
          </div>
          ))}
        </div>
      ))}

      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <button
          onClick={handleSave}
          className="w-full flex items-center justify-center gap-2 bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold rounded-lg py-3 text-sm transition-colors"
        >
          {saved ? (
            <>
              <CheckCircle size={16} /> Saved
            </>
          ) : (
            <>
              <Save size={16} /> Save to .env
            </>
          )}
        </button>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
        <h2 className="text-sm font-semibold text-slate-300 mb-3">Quick Links</h2>
        <ul className="space-y-2 text-sm">
          {[
            ['Gemini API Keys', 'https://aistudio.google.com/app/apikey'],
            ['OpenAI API Keys', 'https://platform.openai.com/api-keys'],
            ['Pexels API', 'https://www.pexels.com/api/'],
            ['WP Application Passwords', 'https://make.wordpress.org/core/2020/11/05/application-passwords-integration-guide/'],
          ].map(([label, url]) => (
            <li key={url}>
              <a href={url} target="_blank" rel="noopener noreferrer" className="text-sky-400 hover:text-sky-300 transition-colors">
                {label} ↗
              </a>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
