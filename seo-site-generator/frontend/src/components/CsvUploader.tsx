import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import Papa from 'papaparse'
import { Upload, FileText } from 'lucide-react'
import type { Row } from '../lib/api'

interface Props {
  onRows: (rows: Row[]) => void
}

export function CsvUploader({ onRows }: Props) {
  const onDrop = useCallback((files: File[]) => {
    const file = files[0]
    if (!file) return
    Papa.parse<Row>(file, {
      header: true,
      skipEmptyLines: true,
      complete: (result) => onRows(result.data),
    })
  }, [onRows])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/csv': ['.csv'] },
    maxFiles: 1,
  })

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors ${
        isDragActive
          ? 'border-sky-400 bg-sky-400/5'
          : 'border-slate-700 hover:border-slate-500 hover:bg-slate-800/50'
      }`}
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center gap-3">
        {isDragActive ? (
          <FileText size={32} className="text-sky-400" />
        ) : (
          <Upload size={32} className="text-slate-500" />
        )}
        <div>
          <p className="text-slate-300 font-medium">
            {isDragActive ? 'Drop your CSV here' : 'Drag & drop a keyword CSV'}
          </p>
          <p className="text-slate-500 text-sm mt-1">
            or click to browse — needs columns: <code className="text-sky-400">keyword, city, service</code>
          </p>
        </div>
      </div>
    </div>
  )
}
