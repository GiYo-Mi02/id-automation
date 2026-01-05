import { useRef, useState, useCallback, useEffect } from 'react'
import { clsx } from 'clsx'
import { Minus, Plus, GridFour, MagnetStraight } from '@phosphor-icons/react'
import { Toggle } from '../shared'

const CANVAS_WIDTH = 591
const CANVAS_HEIGHT = 1004

const elementLabels = {
  photo: 'PHOTO AREA',
  name: 'NAME',
  id_number: 'ID NUMBER',
  grade_section: 'GRADE & SECTION',
  lrn: 'LRN',
  guardian: 'GUARDIAN',
  address: 'ADDRESS',
  contact: 'CONTACT',
}

export default function EditorCanvas({
  template,
  layout,
  selectedElement,
  onElementSelect,
  onPositionChange,
  onSizeChange,
  zoom,
  onZoomChange,
  showGrid,
  onShowGridChange,
  snapToGrid,
  onSnapToGridChange,
}) {
  const containerRef = useRef(null)
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const [dragElement, setDragElement] = useState(null)

  const scale = zoom / 100

  const snapValue = useCallback((value) => {
    if (!snapToGrid) return value
    return Math.round(value / 10) * 10
  }, [snapToGrid])

  const handleMouseDown = (e, elementKey) => {
    if (e.button !== 0) return
    e.stopPropagation()
    
    onElementSelect(elementKey)
    setIsDragging(true)
    setDragElement(elementKey)
    setDragStart({
      x: e.clientX,
      y: e.clientY,
      elementX: layout[elementKey]?.x || 0,
      elementY: layout[elementKey]?.y || 0,
    })
  }

  const handleMouseMove = useCallback((e) => {
    if (!isDragging || !dragElement) return

    const deltaX = (e.clientX - dragStart.x) / scale
    const deltaY = (e.clientY - dragStart.y) / scale

    const newX = snapValue(dragStart.elementX + deltaX)
    const newY = snapValue(dragStart.elementY + deltaY)

    onPositionChange(dragElement, newX, newY)
  }, [isDragging, dragElement, dragStart, scale, snapValue, onPositionChange])

  const handleMouseUp = useCallback(() => {
    setIsDragging(false)
    setDragElement(null)
  }, [])

  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove)
      window.addEventListener('mouseup', handleMouseUp)
      return () => {
        window.removeEventListener('mousemove', handleMouseMove)
        window.removeEventListener('mouseup', handleMouseUp)
      }
    }
  }, [isDragging, handleMouseMove, handleMouseUp])

  const handleCanvasClick = () => {
    onElementSelect(null)
  }

  const zoomIn = () => onZoomChange(Math.min(zoom + 25, 150))
  const zoomOut = () => onZoomChange(Math.max(zoom - 25, 50))

  return (
    <div
      ref={containerRef}
      className="flex-1 bg-black overflow-auto relative"
      style={{
        backgroundImage: showGrid
          ? `radial-gradient(circle, rgba(255,255,255,0.05) 1px, transparent 1px)`
          : 'none',
        backgroundSize: '24px 24px',
      }}
    >
      {/* Canvas */}
      <div
        className="absolute"
        style={{
          left: '50%',
          top: '40px',
          transform: `translateX(-50%) scale(${scale})`,
          transformOrigin: 'top center',
        }}
      >
        <div
          className="relative bg-white rounded-lg shadow-2xl overflow-hidden"
          style={{ width: CANVAS_WIDTH, height: CANVAS_HEIGHT }}
          onClick={handleCanvasClick}
        >
          {/* Template Background */}
          {template && (
            <img
              src={template.path || template}
              alt="Template"
              className="absolute inset-0 w-full h-full object-cover pointer-events-none"
            />
          )}

          {/* Draggable Elements */}
          {Object.entries(layout).map(([key, data]) => (
            <DraggableElement
              key={key}
              elementKey={key}
              data={data}
              isSelected={selectedElement === key}
              isPhoto={key === 'photo'}
              onMouseDown={(e) => handleMouseDown(e, key)}
              isDragging={isDragging && dragElement === key}
            />
          ))}
        </div>
      </div>

      {/* Toolbar */}
      <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-10 flex items-center gap-4 px-4 py-2 bg-navy-900 border border-navy-700 rounded-xl shadow-xl">
        {/* Zoom Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={zoomOut}
            className="w-8 h-8 flex items-center justify-center rounded-md bg-navy-800 border border-navy-700 text-slate-400 hover:text-blue-400 hover:bg-navy-700 transition-colors"
          >
            <Minus size={16} weight="bold" />
          </button>
          <span className="w-14 text-center text-sm text-slate-400 tabular-nums">
            {zoom}%
          </span>
          <button
            onClick={zoomIn}
            className="w-8 h-8 flex items-center justify-center rounded-md bg-navy-800 border border-navy-700 text-slate-400 hover:text-blue-400 hover:bg-navy-700 transition-colors"
          >
            <Plus size={16} weight="bold" />
          </button>
        </div>

        <div className="w-px h-6 bg-navy-700" />

        {/* Grid Toggle */}
        <label className="flex items-center gap-2 cursor-pointer">
          <GridFour size={16} className={showGrid ? 'text-blue-400' : 'text-slate-500'} />
          <span className="text-xs text-slate-400">Grid</span>
          <input
            type="checkbox"
            checked={showGrid}
            onChange={(e) => onShowGridChange(e.target.checked)}
            className="sr-only"
          />
          <div className={clsx(
            'w-8 h-4 rounded-full transition-colors relative',
            showGrid ? 'bg-blue-600' : 'bg-navy-700'
          )}>
            <div className={clsx(
              'absolute top-0.5 w-3 h-3 rounded-full bg-white transition-all',
              showGrid ? 'left-[18px]' : 'left-0.5'
            )} />
          </div>
        </label>

        {/* Snap Toggle */}
        <label className="flex items-center gap-2 cursor-pointer">
          <MagnetStraight size={16} className={snapToGrid ? 'text-blue-400' : 'text-slate-500'} />
          <span className="text-xs text-slate-400">Snap</span>
          <input
            type="checkbox"
            checked={snapToGrid}
            onChange={(e) => onSnapToGridChange(e.target.checked)}
            className="sr-only"
          />
          <div className={clsx(
            'w-8 h-4 rounded-full transition-colors relative',
            snapToGrid ? 'bg-blue-600' : 'bg-navy-700'
          )}>
            <div className={clsx(
              'absolute top-0.5 w-3 h-3 rounded-full bg-white transition-all',
              snapToGrid ? 'left-[18px]' : 'left-0.5'
            )} />
          </div>
        </label>
      </div>
    </div>
  )
}

function DraggableElement({ elementKey, data, isSelected, isPhoto, onMouseDown, isDragging }) {
  const label = elementLabels[elementKey] || elementKey.toUpperCase()

  if (isPhoto) {
    return (
      <div
        onMouseDown={onMouseDown}
        className={clsx(
          'absolute flex items-center justify-center cursor-move transition-all duration-100',
          isSelected
            ? 'border-2 border-yellow-400 bg-yellow-400/15'
            : 'border-2 border-dashed border-blue-500/40 bg-blue-500/5 hover:border-blue-400 hover:bg-blue-500/10'
        )}
        style={{
          left: data.x,
          top: data.y,
          width: data.width || 200,
          height: data.height || 250,
          borderRadius: 4,
        }}
      >
        <span className="text-sm font-bold uppercase pointer-events-none" style={{ color: 'rgba(0,0,0,0.4)' }}>
          {label}
        </span>
        {isSelected && <SelectionHandles />}
      </div>
    )
  }

  return (
    <div
      onMouseDown={onMouseDown}
      className={clsx(
        'absolute cursor-move transition-all duration-100 whitespace-nowrap px-2 py-1 rounded',
        isSelected
          ? 'border-2 border-yellow-400 bg-yellow-400/10'
          : 'border border-transparent hover:border-blue-400 hover:bg-blue-500/5'
      )}
      style={{
        left: data.x,
        top: data.y,
        fontSize: data.fontSize || 16,
        fontWeight: data.fontWeight || 'normal',
        color: data.color || '#000000',
      }}
    >
      {label}
      {isSelected && <PositionHandles />}
    </div>
  )
}

function SelectionHandles() {
  const handlePositions = [
    { top: -4, left: -4 },
    { top: -4, right: -4 },
    { bottom: -4, left: -4 },
    { bottom: -4, right: -4 },
    { top: -4, left: '50%', transform: 'translateX(-50%)' },
    { bottom: -4, left: '50%', transform: 'translateX(-50%)' },
    { top: '50%', left: -4, transform: 'translateY(-50%)' },
    { top: '50%', right: -4, transform: 'translateY(-50%)' },
  ]

  return (
    <>
      {handlePositions.map((style, i) => (
        <div
          key={i}
          className="absolute w-2 h-2 bg-white border-2 border-blue-500 rounded-sm shadow-sm pointer-events-none"
          style={style}
        />
      ))}
    </>
  )
}

function PositionHandles() {
  return null // Text elements don't have resize handles
}
