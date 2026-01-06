/**
 * Layer-Based Canvas Renderer
 * Renders layers with proper z-index ordering and matches backend rendering
 * Supports text alignment, word wrap, and all layer types
 * 
 * Performance optimizations:
 * - Uses requestAnimationFrame for smooth drag operations
 * - Memoized layer components to prevent unnecessary re-renders
 * - Throttled mouse move events during drag/resize
 */

import { useRef, useState, useCallback, useEffect, memo, useMemo } from 'react'

// Sample data for preview
const SAMPLE_STUDENT_DATA = {
  full_name: 'JUAN DELA CRUZ',
  id_number: '2024-001',
  lrn: '123456789012',
  grade_level: 'Grade 7',
  section: 'Einstein',
  guardian_name: 'MARIA DELA CRUZ',
  guardian_contact: '09171234567',
  address: '123 Sample Street, Barangay San Isidro, Manila',
  birth_date: 'January 1, 2010',
  blood_type: 'O+',
  emergency_contact: '09181234567',
  school_year: '2025-2026',
}

const SAMPLE_TEACHER_DATA = {
  full_name: 'DR. MARIA SANTOS',
  employee_id: 'EMP-2024-001',
  department: 'Science Department',
  position: 'Senior Teacher',
  specialization: 'Physics',
  contact_number: '09171234567',
  emergency_contact_name: 'JUAN SANTOS',
  emergency_contact_number: '09181234567',
  address: '456 Teacher Lane, Quezon City',
  birth_date: 'March 15, 1985',
  blood_type: 'A+',
}

export default function LayerBasedCanvas({
  template,
  currentSide = 'front',
  templateType = 'student',
  selectedLayerId,
  onSelectLayer,
  onLayerMove,
  onLayerResize,
  zoom = 100,
  showGrid = true,
  snapToGrid = true,
  gridSize = 10,
  previewData = null,
}) {
  const canvasRef = useRef(null)
  const containerRef = useRef(null)
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const [isResizing, setIsResizing] = useState(false)
  const [resizeHandle, setResizeHandle] = useState(null)
  
  // RAF (requestAnimationFrame) refs for performance
  const rafRef = useRef(null)
  const pendingUpdateRef = useRef(null)

  // Get canvas dimensions
  const canvasWidth = template?.canvas?.width || 591
  const canvasHeight = template?.canvas?.height || 1004
  const bgColor = template?.canvas?.backgroundColor || '#FFFFFF'
  // Use side-specific background image (front or back)
  const bgImage = template?.[currentSide]?.backgroundImage

  // Get layers for current side - memoized to prevent unnecessary re-sorts
  const sortedLayers = useMemo(() => {
    const layers = template?.[currentSide]?.layers || []
    return [...layers].sort((a, b) => (a.zIndex || 0) - (b.zIndex || 0))
  }, [template, currentSide])
  
  // Keep raw layers reference for lookups
  const layers = template?.[currentSide]?.layers || []

  // Sample data for preview
  const sampleData = previewData || (templateType === 'teacher' ? SAMPLE_TEACHER_DATA : SAMPLE_STUDENT_DATA)

  // Scale factor based on zoom
  const scale = zoom / 100

  const getFieldValue = useCallback((field) => {
    if (!field || field === 'static') return null
    return sampleData[field] || ''
  }, [sampleData])

  const handleCanvasClick = (e) => {
    // Deselect if clicking on empty canvas area
    if (e.target === canvasRef.current || e.target.classList.contains('canvas-background')) {
      onSelectLayer(null)
    }
  }

  const handleLayerMouseDown = (e, layer) => {
    e.stopPropagation()
    
    if (layer.locked) return
    
    onSelectLayer(layer.id)
    
    // Check if clicking on resize handle
    const handle = e.target.dataset.resize
    if (handle) {
      setIsResizing(true)
      setResizeHandle(handle)
      setDragStart({ x: e.clientX, y: e.clientY })
      return
    }
    
    // Start dragging
    setIsDragging(true)
    setDragStart({
      x: e.clientX - (layer.x * scale),
      y: e.clientY - (layer.y * scale),
    })
  }

  // RAF-throttled update function for smooth performance
  const scheduleUpdate = useCallback((updateFn) => {
    pendingUpdateRef.current = updateFn
    
    if (!rafRef.current) {
      rafRef.current = requestAnimationFrame(() => {
        if (pendingUpdateRef.current) {
          pendingUpdateRef.current()
          pendingUpdateRef.current = null
        }
        rafRef.current = null
      })
    }
  }, [])

  const handleMouseMove = useCallback((e) => {
    if (!isDragging && !isResizing) return
    
    const selectedLayer = layers.find(l => l.id === selectedLayerId)
    if (!selectedLayer || selectedLayer.locked) return
    
    // Use RAF to throttle updates for better performance
    scheduleUpdate(() => {
      if (isDragging) {
        let newX = (e.clientX - dragStart.x) / scale
        let newY = (e.clientY - dragStart.y) / scale
        
        // Snap to grid
        if (snapToGrid) {
          newX = Math.round(newX / gridSize) * gridSize
          newY = Math.round(newY / gridSize) * gridSize
        }
        
        // Constrain to canvas
        newX = Math.max(0, Math.min(canvasWidth - selectedLayer.width, newX))
        newY = Math.max(0, Math.min(canvasHeight - selectedLayer.height, newY))
        
        onLayerMove(selectedLayerId, newX, newY)
      }
      
      if (isResizing && resizeHandle) {
        const dx = (e.clientX - dragStart.x) / scale
        const dy = (e.clientY - dragStart.y) / scale
        
        // Get rotation angle in radians
        const rotation = selectedLayer.rotation || 0
        const angleRad = (rotation * Math.PI) / 180
        
        // Use vector projection to calculate local axis deltas
        // Project the mouse delta onto the object's rotated axes
        const localDX = dx * Math.cos(-angleRad) - dy * Math.sin(-angleRad)
        const localDY = dx * Math.sin(-angleRad) + dy * Math.cos(-angleRad)
        
        let newWidth = selectedLayer.width
        let newHeight = selectedLayer.height
        let newX = selectedLayer.x
        let newY = selectedLayer.y
        
        // Apply deltas in local coordinate space
        if (resizeHandle.includes('e')) newWidth += localDX
        if (resizeHandle.includes('w')) { newWidth -= localDX; newX += dx }
        if (resizeHandle.includes('s')) newHeight += localDY
        if (resizeHandle.includes('n')) { newHeight -= localDY; newY += dy }
        
        // Minimum size
        newWidth = Math.max(20, newWidth)
        newHeight = Math.max(20, newHeight)
        
        // Snap to grid
        if (snapToGrid) {
          newWidth = Math.round(newWidth / gridSize) * gridSize
          newHeight = Math.round(newHeight / gridSize) * gridSize
          newX = Math.round(newX / gridSize) * gridSize
          newY = Math.round(newY / gridSize) * gridSize
        }
        
        onLayerResize(selectedLayerId, newX, newY, newWidth, newHeight)
        setDragStart({ x: e.clientX, y: e.clientY })
      }
    })
  }, [isDragging, isResizing, selectedLayerId, layers, dragStart, scale, snapToGrid, gridSize, canvasWidth, canvasHeight, onLayerMove, onLayerResize, resizeHandle, scheduleUpdate])

  const handleMouseUp = useCallback(() => {
    // Cancel any pending RAF
    if (rafRef.current) {
      cancelAnimationFrame(rafRef.current)
      rafRef.current = null
    }
    pendingUpdateRef.current = null
    
    setIsDragging(false)
    setIsResizing(false)
    setResizeHandle(null)
  }, [])

  // Cleanup RAF on unmount
  useEffect(() => {
    return () => {
      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current)
      }
    }
  }, [])

  useEffect(() => {
    if (isDragging || isResizing) {
      window.addEventListener('mousemove', handleMouseMove)
      window.addEventListener('mouseup', handleMouseUp)
      return () => {
        window.removeEventListener('mousemove', handleMouseMove)
        window.removeEventListener('mouseup', handleMouseUp)
      }
    }
  }, [isDragging, isResizing, handleMouseMove, handleMouseUp])

  // Render text with proper alignment and word wrap
  const renderTextContent = (layer) => {
    const text = layer.field === 'static' ? (layer.text || '') : getFieldValue(layer.field) || layer.text || ''
    let displayText = text
    
    if (layer.uppercase) displayText = displayText.toUpperCase()
    if (layer.lowercase) displayText = displayText.toLowerCase()
    
    return displayText
  }

  const getTextStyles = (layer) => ({
    fontSize: `${layer.fontSize || 16}px`,
    fontFamily: layer.fontFamily || 'Arial, sans-serif',
    fontWeight: layer.fontWeight || 'normal',
    color: layer.color || '#000000',
    textAlign: layer.textAlign || 'left',
    lineHeight: layer.lineHeight || 1.2,
    letterSpacing: `${layer.letterSpacing || 0}px`,
    whiteSpace: layer.wordWrap ? 'pre-wrap' : 'nowrap',
    wordBreak: layer.wordWrap ? 'break-word' : 'normal',
    overflow: 'hidden',
    width: '100%',
    height: '100%',
    display: 'flex',
    alignItems: 'flex-start',
    justifyContent: layer.textAlign === 'center' ? 'center' : 
                    layer.textAlign === 'right' ? 'flex-end' : 'flex-start',
  })

  return (
    <div 
      ref={containerRef}
      className="flex-1 overflow-auto bg-slate-900/50 p-8 flex items-start justify-center"
    >
      <div
        ref={canvasRef}
        onClick={handleCanvasClick}
        className="relative shadow-2xl"
        style={{
          width: canvasWidth * scale,
          height: canvasHeight * scale,
          backgroundColor: bgColor,
          backgroundImage: bgImage ? `url(${bgImage})` : undefined,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      >
        {/* Grid Overlay */}
        {showGrid && (
          <div 
            className="absolute inset-0 pointer-events-none opacity-20"
            style={{
              backgroundImage: `
                linear-gradient(to right, #666 1px, transparent 1px),
                linear-gradient(to bottom, #666 1px, transparent 1px)
              `,
              backgroundSize: `${gridSize * scale}px ${gridSize * scale}px`,
            }}
          />
        )}

        {/* Canvas Background Click Area */}
        <div className="canvas-background absolute inset-0" />

        {/* Render Layers */}
        {sortedLayers.map((layer) => {
          if (!layer.visible) return null
          
          const isSelected = layer.id === selectedLayerId
          
          // Layer wrapper style (with rotation - selection box rotates with content)
          const wrapperStyle = {
            position: 'absolute',
            left: layer.x * scale,
            top: layer.y * scale,
            width: layer.width * scale,
            height: layer.height * scale,
            zIndex: layer.zIndex || 0,
            opacity: layer.opacity ?? 1,
            transform: layer.rotation ? `rotate(${layer.rotation}deg)` : undefined,
            transformOrigin: 'center center',
          }
          
          // Layer content style (inherits rotation from wrapper)
          const contentStyle = {
            width: '100%',
            height: '100%',
            cursor: layer.locked ? 'not-allowed' : 'move',
          }
          
          return (
            <div
              key={layer.id}
              className={`
                ${isSelected ? 'ring-2 ring-blue-500 ring-offset-1 ring-offset-transparent' : ''}
              `}
              style={wrapperStyle}
            >
              {/* Layer Content (rotated) */}
              <div
                onMouseDown={(e) => handleLayerMouseDown(e, layer)}
                className={layer.locked ? 'cursor-not-allowed' : ''}
                style={contentStyle}
              >
                {/* Text Layer */}
                {layer.type === 'text' && (
                  <div style={getTextStyles(layer)}>
                    <span>{renderTextContent(layer)}</span>
                  </div>
                )}
                
                {/* Image Layer */}
                {layer.type === 'image' && (
                  <div 
                    className="w-full h-full bg-slate-300 flex items-center justify-center"
                    style={{
                      borderRadius: layer.borderRadius ? `${layer.borderRadius}px` : 0,
                      border: layer.border ? 
                        `${layer.border.width}px ${layer.border.style} ${layer.border.color}` : 
                        undefined,
                    }}
                  >
                    {layer.field === 'photo' ? (
                      <div className="w-full h-full bg-gradient-to-br from-slate-200 to-slate-400 flex items-center justify-center">
                        <span className="text-slate-500 text-sm">Photo</span>
                      </div>
                    ) : layer.src ? (
                      <img 
                        src={layer.src} 
                        alt="" 
                        className="w-full h-full"
                        style={{ objectFit: layer.objectFit || 'cover' }}
                      />
                    ) : (
                      <span className="text-slate-500 text-sm">Image</span>
                    )}
                  </div>
                )}
                
                {/* Shape Layer */}
                {layer.type === 'shape' && (
                  <svg 
                    width="100%" 
                    height="100%" 
                    className="overflow-visible"
                  >
                    {layer.shape === 'rectangle' && (
                      <rect
                        x={layer.strokeWidth ? layer.strokeWidth / 2 : 0}
                        y={layer.strokeWidth ? layer.strokeWidth / 2 : 0}
                        width={layer.width * scale - (layer.strokeWidth || 0)}
                        height={layer.height * scale - (layer.strokeWidth || 0)}
                        fill={layer.fill || 'transparent'}
                        stroke={layer.stroke}
                        strokeWidth={layer.strokeWidth}
                        rx={layer.borderRadius || 0}
                      />
                    )}
                    {layer.shape === 'circle' && (
                      <ellipse
                        cx={(layer.width * scale) / 2}
                        cy={(layer.height * scale) / 2}
                        rx={(layer.width * scale) / 2 - (layer.strokeWidth || 0) / 2}
                        ry={(layer.height * scale) / 2 - (layer.strokeWidth || 0) / 2}
                        fill={layer.fill || 'transparent'}
                        stroke={layer.stroke}
                        strokeWidth={layer.strokeWidth}
                      />
                    )}
                    {layer.shape === 'line' && (
                      <line
                        x1={0}
                        y1={0}
                        x2={layer.width * scale}
                        y2={layer.height * scale}
                        stroke={layer.stroke || layer.fill || '#000'}
                        strokeWidth={layer.strokeWidth || 1}
                      />
                    )}
                  </svg>
                )}
                
                {/* QR Code Layer */}
                {layer.type === 'qr_code' && (
                  <div 
                    className="w-full h-full flex items-center justify-center"
                    style={{ backgroundColor: layer.backgroundColor || '#fff' }}
                  >
                    <div 
                      className="w-4/5 h-4/5 bg-slate-800 flex items-center justify-center text-white text-xs"
                      style={{ color: layer.foregroundColor || '#000' }}
                    >
                      QR: {layer.field}
                    </div>
                  </div>
                )}
              </div>
              
              {/* Selection Resize Handles (unrotated, outside content) */}
              {isSelected && !layer.locked && (
                <>
                  {/* Corner handles */}
                  {['nw', 'ne', 'sw', 'se'].map((pos) => (
                    <div
                      key={pos}
                      data-resize={pos}
                      className={`
                        absolute w-3 h-3 bg-blue-500 border border-white rounded-sm
                        ${pos.includes('n') ? 'top-0 -translate-y-1/2' : 'bottom-0 translate-y-1/2'}
                        ${pos.includes('w') ? 'left-0 -translate-x-1/2' : 'right-0 translate-x-1/2'}
                        cursor-${pos}-resize
                      `}
                      style={{ zIndex: 10 }}
                    />
                  ))}
                  {/* Edge handles */}
                  {['n', 's', 'e', 'w'].map((pos) => (
                    <div
                      key={pos}
                      data-resize={pos}
                      className={`
                        absolute bg-blue-500 border border-white
                        ${pos === 'n' || pos === 's' ? 'w-6 h-2 left-1/2 -translate-x-1/2' : 'h-6 w-2 top-1/2 -translate-y-1/2'}
                        ${pos === 'n' ? 'top-0 -translate-y-1/2 cursor-n-resize' : ''}
                        ${pos === 's' ? 'bottom-0 translate-y-1/2 cursor-s-resize' : ''}
                        ${pos === 'e' ? 'right-0 translate-x-1/2 cursor-e-resize' : ''}
                        ${pos === 'w' ? 'left-0 -translate-x-1/2 cursor-w-resize' : ''}
                        rounded-sm
                      `}
                      style={{ zIndex: 10 }}
                    />
                  ))}
                </>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

// =============================================================================
// MEMOIZED LAYER SUB-COMPONENTS
// =============================================================================

/**
 * Memoized Text Layer component
 * Only re-renders when text-specific props change
 */
const MemoizedTextLayer = memo(function TextLayer({ layer, getFieldValue }) {
  const text = layer.field === 'static' ? (layer.text || '') : getFieldValue(layer.field) || layer.text || ''
  let displayText = text
  
  if (layer.uppercase) displayText = displayText.toUpperCase()
  if (layer.lowercase) displayText = displayText.toLowerCase()
  
  const styles = {
    fontSize: `${layer.fontSize || 16}px`,
    fontFamily: layer.fontFamily || 'Arial, sans-serif',
    fontWeight: layer.fontWeight || 'normal',
    color: layer.color || '#000000',
    textAlign: layer.textAlign || 'left',
    lineHeight: layer.lineHeight || 1.2,
    letterSpacing: `${layer.letterSpacing || 0}px`,
    whiteSpace: layer.wordWrap ? 'pre-wrap' : 'nowrap',
    wordBreak: layer.wordWrap ? 'break-word' : 'normal',
    overflow: 'hidden',
    width: '100%',
    height: '100%',
    display: 'flex',
    alignItems: 'flex-start',
    justifyContent: layer.textAlign === 'center' ? 'center' : 
                    layer.textAlign === 'right' ? 'flex-end' : 'flex-start',
  }
  
  return (
    <div style={styles}>
      <span>{displayText}</span>
    </div>
  )
})

/**
 * Memoized Image Layer component
 * Only re-renders when image-specific props change
 */
const MemoizedImageLayer = memo(function ImageLayer({ layer }) {
  const containerStyle = {
    borderRadius: layer.borderRadius ? `${layer.borderRadius}px` : 0,
    border: layer.border ? 
      `${layer.border.width}px ${layer.border.style} ${layer.border.color}` : 
      undefined,
  }
  
  return (
    <div 
      className="w-full h-full bg-slate-300 flex items-center justify-center"
      style={containerStyle}
    >
      {layer.field === 'photo' ? (
        <div className="w-full h-full bg-gradient-to-br from-slate-200 to-slate-400 flex items-center justify-center">
          <span className="text-slate-500 text-sm">Photo</span>
        </div>
      ) : layer.src ? (
        <img 
          src={layer.src} 
          alt="" 
          className="w-full h-full"
          style={{ objectFit: layer.objectFit || 'cover' }}
        />
      ) : (
        <span className="text-slate-500 text-sm">Image</span>
      )}
    </div>
  )
})

/**
 * Memoized Shape Layer component
 * Only re-renders when shape-specific props change
 */
const MemoizedShapeLayer = memo(function ShapeLayer({ layer, scaledWidth, scaledHeight }) {
  return (
    <svg width="100%" height="100%" className="overflow-visible">
      {layer.shape === 'rectangle' && (
        <rect
          x={layer.strokeWidth ? layer.strokeWidth / 2 : 0}
          y={layer.strokeWidth ? layer.strokeWidth / 2 : 0}
          width={scaledWidth - (layer.strokeWidth || 0)}
          height={scaledHeight - (layer.strokeWidth || 0)}
          fill={layer.fill || 'transparent'}
          stroke={layer.stroke}
          strokeWidth={layer.strokeWidth}
          rx={layer.borderRadius || 0}
        />
      )}
      {layer.shape === 'circle' && (
        <ellipse
          cx={scaledWidth / 2}
          cy={scaledHeight / 2}
          rx={scaledWidth / 2 - (layer.strokeWidth || 0) / 2}
          ry={scaledHeight / 2 - (layer.strokeWidth || 0) / 2}
          fill={layer.fill || 'transparent'}
          stroke={layer.stroke}
          strokeWidth={layer.strokeWidth}
        />
      )}
      {layer.shape === 'line' && (
        <line
          x1={0}
          y1={0}
          x2={scaledWidth}
          y2={scaledHeight}
          stroke={layer.stroke || layer.fill || '#000'}
          strokeWidth={layer.strokeWidth || 1}
        />
      )}
    </svg>
  )
})

/**
 * Memoized QR Code Layer component
 */
const MemoizedQRCodeLayer = memo(function QRCodeLayer({ layer }) {
  return (
    <div 
      className="w-full h-full flex items-center justify-center"
      style={{ backgroundColor: layer.backgroundColor || '#fff' }}
    >
      <div 
        className="w-4/5 h-4/5 bg-slate-800 flex items-center justify-center text-white text-xs"
        style={{ color: layer.foregroundColor || '#000' }}
      >
        QR: {layer.field}
      </div>
    </div>
  )
})

/**
 * Memoized Resize Handles component
 */
const MemoizedResizeHandles = memo(function ResizeHandles() {
  return (
    <>
      {/* Corner handles */}
      {['nw', 'ne', 'sw', 'se'].map((pos) => (
        <div
          key={pos}
          data-resize={pos}
          className={`
            absolute w-3 h-3 bg-blue-500 border border-white rounded-sm
            ${pos.includes('n') ? 'top-0 -translate-y-1/2' : 'bottom-0 translate-y-1/2'}
            ${pos.includes('w') ? 'left-0 -translate-x-1/2' : 'right-0 translate-x-1/2'}
            cursor-${pos}-resize
          `}
        />
      ))}
      {/* Edge handles */}
      {['n', 's', 'e', 'w'].map((pos) => (
        <div
          key={pos}
          data-resize={pos}
          className={`
            absolute bg-blue-500 border border-white
            ${pos === 'n' || pos === 's' ? 'w-6 h-2 left-1/2 -translate-x-1/2' : 'h-6 w-2 top-1/2 -translate-y-1/2'}
            ${pos === 'n' ? 'top-0 -translate-y-1/2 cursor-n-resize' : ''}
            ${pos === 's' ? 'bottom-0 translate-y-1/2 cursor-s-resize' : ''}
            ${pos === 'e' ? 'right-0 translate-x-1/2 cursor-e-resize' : ''}
            ${pos === 'w' ? 'left-0 -translate-x-1/2 cursor-w-resize' : ''}
            rounded-sm
          `}
        />
      ))}
    </>
  )
})
