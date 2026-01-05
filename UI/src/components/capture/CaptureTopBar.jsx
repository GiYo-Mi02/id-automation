import { clsx } from 'clsx'
import { BoundingBox, Circle, WifiHigh, WifiSlash } from '@phosphor-icons/react'
import Badge from '../shared/Badge'
import Spinner from '../shared/Spinner'

export default function CaptureTopBar({ status, showGuide, onToggleGuide }) {
  return (
    <header className="h-14 px-4 bg-navy-900/90 backdrop-blur-xl border-b border-navy-700 flex items-center justify-between shrink-0">
      <h1 className="text-lg font-semibold text-slate-50">Capture Station</h1>

      <div className="flex items-center gap-3">
        {/* Connection Status */}
        {status === 'connected' && (
          <Badge variant="success" icon={WifiHigh}>
            <span className="relative flex items-center gap-1.5">
              <span className="absolute w-2 h-2 rounded-full bg-green-400 animate-ping" />
              <span className="relative w-2 h-2 rounded-full bg-green-400" />
              Online
            </span>
          </Badge>
        )}
        {status === 'disconnected' && (
          <Badge variant="error" icon={WifiSlash}>
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-red-400" />
              Offline
            </span>
          </Badge>
        )}
        {status === 'connecting' && (
          <Badge variant="neutral">
            <Spinner size="sm" />
            Connecting...
          </Badge>
        )}

        {/* Guide Toggle */}
        <button
          onClick={onToggleGuide}
          className={clsx(
            'w-9 h-9 flex items-center justify-center rounded-md border transition-all duration-150',
            showGuide
              ? 'bg-navy-800 border-blue-500 text-blue-400 shadow-glow-blue/30'
              : 'bg-transparent border-navy-700 text-slate-400 hover:bg-navy-800 hover:text-slate-200'
          )}
          title={showGuide ? 'Hide Guide' : 'Show Guide'}
        >
          <BoundingBox size={18} weight="bold" />
        </button>
      </div>
    </header>
  )
}
