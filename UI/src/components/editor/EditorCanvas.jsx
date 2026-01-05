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
      className="flex-1 bg-slate-950 overflow-auto relative"
      style={{
        backgroundImage: showGrid
          ? `radial-gradient(circle, #475569 1px, transparent 1px)`
          : 'none',
        backgroundSize: '20px 20px',
        backgroundPosition: 'center center',
      }}
      onClick={handleCanvasClick}
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
        >
          {/* Template Background */}
          {template && (
            <img
              src={template.path || template}
              alt="Template"
              className="absolute inset-0 w-full h-full object-cover pointer-events-none select-none"
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
          'absolute flex items-center justify-center cursor-move transition-all duration-200 group',
          isSelected
            ? 'ring-2 ring-blue-400 ring-offset-2 ring-offset-white bg-blue-400/10'
            : 'ring-2 ring-slate-400 ring-dashed ring-offset-2 ring-offset-white hover:ring-blue-300'
        )}
        style={{
          left: data.x,
          top: data.y,
          width: data.width || 200,
          height: data.height || 250,
          borderRadius: 4,
        }}
      >
        <span className="text-sm font-bold uppercase text-slate-400 pointer-events-none select-none">
          {label}
        </span>
      </div>
    )
  }

  return (
    <div
      onMouseDown={onMouseDown}
      className={clsx(
        'absolute cursor-move transition-all duration-200 whitespace-nowrap px-2 py-1 rounded select-none',
        isSelected
          ? 'ring-2 ring-blue-400 bg-blue-400/10'
          : 'ring-1 ring-transparent hover:ring-blue-300 hover:bg-blue-500/5'
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
    </div>
  )
}

/* Old toolbar and duplicate elements removed - see FloatingToolbar and DynamicPropertiesPanel components */
/* SelectionHandles and PositionHandles kept for visual feedback */

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

