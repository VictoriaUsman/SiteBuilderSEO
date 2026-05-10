import { useEffect, useRef, useState } from 'react'
import type { Job } from '../lib/api'

export function useJobSocket(jobId: string | null) {
  const [job, setJob] = useState<Job | null>(null)
  const ws = useRef<WebSocket | null>(null)

  useEffect(() => {
    if (!jobId) return

    const proto = location.protocol === 'https:' ? 'wss' : 'ws'
    const socket = new WebSocket(`${proto}://${location.host}/ws/${jobId}`)
    ws.current = socket

    socket.onmessage = (e) => {
      const data = JSON.parse(e.data) as Job
      setJob(data)
    }

    socket.onerror = () => {
      // Fallback to polling if WebSocket unavailable
      const interval = setInterval(async () => {
        const res = await fetch(`/jobs/${jobId}`)
        if (res.ok) {
          const data: Job = await res.json()
          setJob(data)
          if (data.status !== 'running') clearInterval(interval)
        }
      }, 2000)
      socket.close()
      return () => clearInterval(interval)
    }

    return () => socket.close()
  }, [jobId])

  return job
}
