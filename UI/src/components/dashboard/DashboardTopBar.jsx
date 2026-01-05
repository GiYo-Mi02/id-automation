import { CirclesFour, WifiHigh, WifiSlash, User } from '@phosphor-icons/react'
import Badge from '../shared/Badge'
import Spinner from '../shared/Spinner'

export default function DashboardTopBar({ status }) {
  return (
    <header className="h-16 px-6 bg-navy-900/95 backdrop-blur-xl border-b border-navy-700 flex items-center justify-between shrink-0 shadow-sm">
      {/* Left: Title */}
      <div className="flex items-center gap-3">
        <CirclesFour size={24} weight="fill" className="text-blue-500" />
        <span className="text-xl font-bold text-slate-50">ID Automation System v2.0</span>
      </div>

      {/* Right: Status & Profile */}
      <div className="flex items-center gap-4">
        {/* System Status */}
        {status === 'connected' && (
          <Badge variant="success">
            <span className="relative flex items-center gap-1.5">
              <span className="absolute w-1.5 h-1.5 rounded-full bg-green-400 animate-ping" />
              <span className="relative w-1.5 h-1.5 rounded-full bg-green-400" />
              System Online
            </span>
          </Badge>
        )}
        {status === 'disconnected' && (
          <Badge variant="error" icon={WifiSlash}>
            System Offline
          </Badge>
        )}
        {status === 'connecting' && (
          <Badge variant="neutral">
            <Spinner size="sm" />
            Connecting...
          </Badge>
        )}

        {/* Profile Button */}
        <button className="w-10 h-10 rounded-full bg-navy-800 border border-navy-700 flex items-center justify-center text-slate-400 hover:border-blue-500 hover:text-blue-400 hover:scale-105 transition-all">
          <User size={20} weight="bold" />
        </button>
      </div>
    </header>
  )
}
