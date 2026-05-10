import { useEffect, useRef } from 'react'
import type { PageResult } from '../lib/api'

interface Props {
  pages: PageResult[]
}

interface Node {
  id: string
  x: number
  y: number
  vx: number
  vy: number
  valid: boolean
  connections: number
}

interface Link {
  source: string
  target: string
}

export function LinkGraph({ pages }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animRef = useRef<number>(0)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || pages.length === 0) return
    const ctx = canvas.getContext('2d')!

    const W = canvas.width = canvas.offsetWidth
    const H = canvas.height = canvas.offsetHeight

    // Build nodes and links from internal_link_suggestions
    const nodes: Record<string, Node> = {}
    const links: Link[] = []

    pages.forEach((p, i) => {
      const angle = (i / pages.length) * Math.PI * 2
      const r = Math.min(W, H) * 0.3
      nodes[p.slug] = {
        id: p.slug,
        x: W / 2 + r * Math.cos(angle),
        y: H / 2 + r * Math.sin(angle),
        vx: 0, vy: 0,
        valid: p.valid,
        connections: 0,
      }
    })

    pages.forEach((p) => {
      (p.content?.internal_link_suggestions || []).forEach((target) => {
        if (nodes[target]) {
          links.push({ source: p.slug, target })
          nodes[p.slug].connections++
        }
      })
    })

    let hovered: string | null = null

    const simulate = () => {
      const nodeArr = Object.values(nodes)
      const k = 0.01
      const repulsion = 2000

      // Spring forces along links
      links.forEach(({ source, target }) => {
        const a = nodes[source], b = nodes[target]
        if (!a || !b) return
        const dx = b.x - a.x, dy = b.y - a.y
        const dist = Math.sqrt(dx * dx + dy * dy) || 1
        const ideal = 120
        const f = k * (dist - ideal)
        a.vx += f * dx / dist; a.vy += f * dy / dist
        b.vx -= f * dx / dist; b.vy -= f * dy / dist
      })

      // Node repulsion
      for (let i = 0; i < nodeArr.length; i++) {
        for (let j = i + 1; j < nodeArr.length; j++) {
          const a = nodeArr[i], b = nodeArr[j]
          const dx = b.x - a.x, dy = b.y - a.y
          const dist = Math.sqrt(dx * dx + dy * dy) || 1
          const f = repulsion / (dist * dist)
          a.vx -= f * dx / dist; a.vy -= f * dy / dist
          b.vx += f * dx / dist; b.vy += f * dy / dist
        }
      }

      // Center gravity
      nodeArr.forEach((n) => {
        n.vx += (W / 2 - n.x) * 0.002
        n.vy += (H / 2 - n.y) * 0.002
        n.vx *= 0.85; n.vy *= 0.85
        n.x += n.vx; n.y += n.vy
        n.x = Math.max(40, Math.min(W - 40, n.x))
        n.y = Math.max(40, Math.min(H - 40, n.y))
      })
    }

    const draw = () => {
      ctx.clearRect(0, 0, W, H)

      // Links
      links.forEach(({ source, target }) => {
        const a = nodes[source], b = nodes[target]
        if (!a || !b) return
        const isHighlit = hovered === source || hovered === target
        ctx.beginPath()
        ctx.moveTo(a.x, a.y)
        ctx.lineTo(b.x, b.y)
        ctx.strokeStyle = isHighlit ? 'rgba(56,189,248,0.6)' : 'rgba(100,116,139,0.25)'
        ctx.lineWidth = isHighlit ? 1.5 : 1
        ctx.stroke()

        // Arrow
        const angle = Math.atan2(b.y - a.y, b.x - a.x)
        const r = 14
        const ax = b.x - r * Math.cos(angle), ay = b.y - r * Math.sin(angle)
        ctx.beginPath()
        ctx.moveTo(ax, ay)
        ctx.lineTo(ax - 6 * Math.cos(angle - 0.4), ay - 6 * Math.sin(angle - 0.4))
        ctx.lineTo(ax - 6 * Math.cos(angle + 0.4), ay - 6 * Math.sin(angle + 0.4))
        ctx.closePath()
        ctx.fillStyle = isHighlit ? 'rgba(56,189,248,0.6)' : 'rgba(100,116,139,0.3)'
        ctx.fill()
      })

      // Nodes
      Object.values(nodes).forEach((n) => {
        const isHov = hovered === n.id
        const size = 10 + n.connections * 2
        ctx.beginPath()
        ctx.arc(n.x, n.y, size, 0, Math.PI * 2)
        ctx.fillStyle = isHov
          ? '#38bdf8'
          : n.valid
          ? 'rgba(52,211,153,0.8)'
          : 'rgba(251,191,36,0.8)'
        ctx.fill()
        ctx.strokeStyle = isHov ? '#fff' : 'rgba(255,255,255,0.15)'
        ctx.lineWidth = isHov ? 2 : 1
        ctx.stroke()

        // Label
        if (isHov || n.connections > 1) {
          ctx.font = '10px monospace'
          ctx.fillStyle = isHov ? '#fff' : 'rgba(148,163,184,0.9)'
          ctx.textAlign = 'center'
          ctx.fillText(n.id.length > 20 ? n.id.slice(0, 18) + '…' : n.id, n.x, n.y - size - 4)
        }
      })
    }

    const tick = () => {
      simulate()
      draw()
      animRef.current = requestAnimationFrame(tick)
    }
    animRef.current = requestAnimationFrame(tick)

    const onMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect()
      const mx = e.clientX - rect.left, my = e.clientY - rect.top
      hovered = null
      Object.values(nodes).forEach((n) => {
        if (Math.hypot(mx - n.x, my - n.y) < 18) hovered = n.id
      })
      canvas.style.cursor = hovered ? 'pointer' : 'default'
    }
    canvas.addEventListener('mousemove', onMove)

    return () => {
      cancelAnimationFrame(animRef.current)
      canvas.removeEventListener('mousemove', onMove)
    }
  }, [pages])

  if (pages.length === 0) return null

  return (
    <div>
      <p className="text-xs text-slate-500 mb-2 font-medium uppercase tracking-wider">Internal Link Graph</p>
      <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden" style={{ height: 300 }}>
        <canvas ref={canvasRef} className="w-full h-full" />
      </div>
      <div className="flex gap-4 mt-2 text-xs text-slate-500">
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400/80 inline-block" /> Valid page
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-400/80 inline-block" /> Has warnings
        </span>
        <span className="flex items-center gap-1.5 ml-auto">Hover to inspect</span>
      </div>
    </div>
  )
}
