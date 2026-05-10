import { Plus, Trash2 } from 'lucide-react'
import type { Row } from '../lib/api'

interface Props {
  rows: Row[]
  onChange: (rows: Row[]) => void
}

const COLS: (keyof Row)[] = ['keyword', 'city', 'service']

export function CsvEditor({ rows, onChange }: Props) {
  const update = (i: number, field: keyof Row, value: string) => {
    const next = rows.map((r, idx) => (idx === i ? { ...r, [field]: value } : r))
    onChange(next)
  }

  const addRow = () => onChange([...rows, { keyword: '', city: '', service: '' }])

  const removeRow = (i: number) => onChange(rows.filter((_, idx) => idx !== i))

  return (
    <div>
      <div className="overflow-x-auto rounded-lg border border-slate-700">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700 bg-slate-800/50">
              <th className="px-3 py-2 text-left text-slate-400 font-medium w-8">#</th>
              {COLS.map((c) => (
                <th key={c} className="px-3 py-2 text-left text-slate-400 font-medium capitalize">
                  {c}
                </th>
              ))}
              <th className="px-3 py-2 w-10" />
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={i} className="border-b border-slate-800 hover:bg-slate-800/30">
                <td className="px-3 py-1.5 text-slate-600 text-xs">{i + 1}</td>
                {COLS.map((col) => (
                  <td key={col} className="px-2 py-1">
                    <input
                      value={row[col]}
                      onChange={(e) => update(i, col, e.target.value)}
                      className="w-full bg-transparent border border-transparent hover:border-slate-600 focus:border-sky-500 rounded px-2 py-1 text-slate-200 outline-none transition-colors"
                    />
                  </td>
                ))}
                <td className="px-2 py-1">
                  <button
                    onClick={() => removeRow(i)}
                    className="text-slate-600 hover:text-red-400 transition-colors p-1 rounded"
                  >
                    <Trash2 size={14} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <button
        onClick={addRow}
        className="mt-3 flex items-center gap-2 text-sm text-slate-400 hover:text-sky-400 transition-colors px-2 py-1"
      >
        <Plus size={14} />
        Add row
      </button>

      <p className="mt-2 text-xs text-slate-600">{rows.length} rows</p>
    </div>
  )
}
