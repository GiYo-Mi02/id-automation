import { clsx } from 'clsx'
import { ClockCounterClockwise, ArrowsClockwise, Eye, Camera } from '@phosphor-icons/react'
import { formatDistanceToNow } from '../utils/formatTime'

export default function RecentCaptures({ captures, onRefresh, onView }) {
  return (
    <div className="card">
      {/* Header */}
      <div className="h-12 px-4 flex items-center justify-between border-b border-navy-700 bg-gradient-to-r from-navy-850 to-navy-900">
        <div className="flex items-center gap-2 text-base font-semibold text-slate-200">
          <ClockCounterClockwise size={18} />
          Recent Captures
        </div>
        <button
          onClick={onRefresh}
          className="w-8 h-8 flex items-center justify-center rounded-md border border-navy-700 text-slate-400 hover:bg-navy-800 hover:text-slate-200 transition-colors active:rotate-180 active:transition-transform active:duration-500"
        >
          <ArrowsClockwise size={16} />
        </button>
      </div>

      {/* List */}
      <div className="max-h-60 overflow-y-auto p-2">
        {captures.length === 0 ? (
          <EmptyState />
        ) : (
          <ul className="space-y-1">
            {captures.map((capture, index) => (
              <CaptureItem key={`${capture.student_id || capture.id_number}-${capture.timestamp || capture.created_at}-${index}`} capture={capture} onView={onView} />
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}

function CaptureItem({ capture, onView }) {
  return (
    <li
      onClick={() => onView(capture)}
      className="group flex items-center gap-3 p-3 rounded-lg cursor-pointer hover:bg-navy-800 transition-all hover:translate-x-1"
    >
      {/* Thumbnail */}
      <div className="w-12 h-12 rounded-lg border border-navy-700 bg-navy-800 overflow-hidden shrink-0">
        {capture.front_image ? (
          <img
            src={capture.front_image}
            alt=""
            className="w-full h-full object-cover"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-slate-700">
            <Camera size={20} />
          </div>
        )}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-bold text-slate-50 group-hover:text-blue-400 transition-colors truncate">
          {capture.student_id || capture.id_number}
        </p>
        <p className="text-xs text-slate-400 truncate">{capture.full_name}</p>
        <p className="text-xs text-slate-600 mt-0.5">
          {formatDistanceToNow(capture.timestamp || capture.created_at)}
        </p>
      </div>

      {/* View Icon */}
      <div className="text-slate-600 group-hover:text-blue-400 transition-all group-hover:scale-110">
        <Eye size={18} />
      </div>
    </li>
  )
}

function EmptyState() {
  return (
    <div className="py-12 text-center">
      <Camera size={64} className="mx-auto text-slate-700 animate-pulse-slow" weight="thin" />
      <p className="mt-4 text-base font-medium text-slate-400">No captures yet</p>
      <p className="text-sm text-slate-600">Capture your first ID to get started</p>
    </div>
  )
}
