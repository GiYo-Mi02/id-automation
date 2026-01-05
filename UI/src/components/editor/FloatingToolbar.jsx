import { 
  MagnifyingGlassPlus, 
  MagnifyingGlassMinus, 
  ArrowCounterClockwise, 
  ArrowClockwise,
  GridFour,
  MagnetStraight 
} from '@phosphor-icons/react'
import { clsx } from 'clsx'

export default function FloatingToolbar({ 
  zoom, 
  onZoomChange, 
  showGrid, 
  onShowGridChange,
  snapToGrid,
  onSnapToGridChange,
  onUndo,
  onRedo,
  canUndo,
  canRedo
}) {
  const zoomIn = () => onZoomChange(Math.min(zoom + 25, 200))
  const zoomOut = () => onZoomChange(Math.max(zoom - 25, 25))

  return (
    <div className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 flex items-center gap-1 px-3 py-2 bg-slate-900/90 backdrop-blur-xl border border-slate-700 rounded-full shadow-2xl">
      {/* Zoom Out */}
      <button
        onClick={zoomOut}
        disabled={zoom <= 25}
        className="w-9 h-9 flex items-center justify-center rounded-full text-slate-400 hover:text-white hover:bg-slate-800 transition-all duration-200 disabled:opacity-30 disabled:cursor-not-allowed"
        title="Zoom Out"
      >
        <MagnifyingGlassMinus size={18} weight="bold" />
      </button>

      {/* Zoom Display */}
      <div className="px-3 min-w-[60px] text-center">
        <span className="text-xs font-medium text-slate-300 tabular-nums">{zoom}%</span>
      </div>

      {/* Zoom In */}
      <button
        onClick={zoomIn}
        disabled={zoom >= 200}
        className="w-9 h-9 flex items-center justify-center rounded-full text-slate-400 hover:text-white hover:bg-slate-800 transition-all duration-200 disabled:opacity-30 disabled:cursor-not-allowed"
        title="Zoom In"
      >
        <MagnifyingGlassPlus size={18} weight="bold" />
      </button>

      <div className="w-px h-5 bg-slate-700 mx-1" />

      {/* Undo */}
      <button
        onClick={onUndo}
        disabled={!canUndo}
        className="w-9 h-9 flex items-center justify-center rounded-full text-slate-400 hover:text-white hover:bg-slate-800 transition-all duration-200 disabled:opacity-30 disabled:cursor-not-allowed"
        title="Undo"
      >
        <ArrowCounterClockwise size={18} weight="bold" />
      </button>

      {/* Redo */}
      <button
        onClick={onRedo}
        disabled={!canRedo}
        className="w-9 h-9 flex items-center justify-center rounded-full text-slate-400 hover:text-white hover:bg-slate-800 transition-all duration-200 disabled:opacity-30 disabled:cursor-not-allowed"
        title="Redo"
      >
        <ArrowClockwise size={18} weight="bold" />
      </button>

      <div className="w-px h-5 bg-slate-700 mx-1" />

      {/* Grid Toggle */}
      <button
        onClick={() => onShowGridChange(!showGrid)}
        className={clsx(
          "w-9 h-9 flex items-center justify-center rounded-full transition-all duration-200",
          showGrid ? "text-blue-400 bg-blue-500/10" : "text-slate-400 hover:text-white hover:bg-slate-800"
        )}
        title="Toggle Grid"
      >
        <GridFour size={18} weight="bold" />
      </button>

      {/* Snap to Grid Toggle */}
      <button
        onClick={() => onSnapToGridChange(!snapToGrid)}
        className={clsx(
          "w-9 h-9 flex items-center justify-center rounded-full transition-all duration-200",
          snapToGrid ? "text-blue-400 bg-blue-500/10" : "text-slate-400 hover:text-white hover:bg-slate-800"
        )}
        title="Snap to Grid"
      >
        <MagnetStraight size={18} weight="bold" />
      </button>
    </div>
  )
}
