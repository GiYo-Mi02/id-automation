import { useEffect, useState } from 'react'
import { clsx } from 'clsx'
import { X, CheckCircle, XCircle, Warning, Info } from '@phosphor-icons/react'

const icons = {
  success: CheckCircle,
  error: XCircle,
  warning: Warning,
  info: Info,
}

const colors = {
  success: 'text-green-400',
  error: 'text-red-400',
  warning: 'text-amber-400',
  info: 'text-blue-400',
}

const progressColors = {
  success: 'bg-green-500',
  error: 'bg-red-500',
  warning: 'bg-amber-500',
  info: 'bg-blue-500',
}

export default function Toast({ id, type = 'info', title, message, duration = 4000, onClose }) {
  const [progress, setProgress] = useState(100)
  const [isPaused, setIsPaused] = useState(false)
  const Icon = icons[type]

  useEffect(() => {
    if (isPaused || duration === 0) return

    const startTime = Date.now()
    const endTime = startTime + duration
    let frameId

    const tick = () => {
      const now = Date.now()
      const elapsed = now - startTime
      const newProgress = Math.max(0, 100 - (elapsed / duration) * 100)

      if (newProgress <= 0) {
        onClose()
      } else {
        setProgress(newProgress)
        frameId = requestAnimationFrame(tick)
      }
    }

    frameId = requestAnimationFrame(tick)
    return () => {
      if (frameId) cancelAnimationFrame(frameId)
    }
  }, [isPaused, duration, onClose])

  return (
    <div
      className="card p-4 shadow-xl animate-slide-down relative overflow-hidden"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      <div className="flex gap-3 items-start">
        <Icon size={24} weight="fill" className={colors[type]} />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-slate-200">{title}</p>
          {message && <p className="text-xs text-slate-400 mt-1">{message}</p>}
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded hover:bg-navy-800 text-slate-500 hover:text-slate-200 transition-colors"
        >
          <X size={16} />
        </button>
      </div>
      {duration > 0 && (
        <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-navy-700">
          <div
            className={clsx('h-full transition-all', progressColors[type])}
            style={{ width: `${progress}%` }}
          />
        </div>
      )}
    </div>
  )
}
