/**
 * Enhanced Layers Panel
 * Provides a drag-and-drop layer management panel with:
 * - Visual layer list with thumbnails
 * - Drag-to-reorder functionality
 * - Visibility and lock toggles
 * - Layer type icons
 * - Add new layer button
 */

import { useState, useRef } from 'react'
import {
  TextT,
  Image,
  Square,
  QrCode,
  Eye,
  EyeSlash,
  Lock,
  LockOpen,
  Plus,
  DotsSixVertical,
  CaretDown,
  CaretRight,
  UploadSimple,
} from '@phosphor-icons/react'

const LAYER_TYPE_ICONS = {
  text: TextT,
  image: Image,
  shape: Square,
  qr_code: QrCode,
}

const LAYER_TYPE_COLORS = {
  text: 'text-blue-400',
  image: 'text-purple-400',
  shape: 'text-green-400',
  qr_code: 'text-amber-400',
}

export default function EnhancedLayersPanel({
  layers = [],
  selectedLayerId,
  onSelectLayer,
  onLayerUpdate,
  onReorderLayers,
  onAddLayer,
  onUploadImage,
  activeView,
}) {
  const [draggedId, setDraggedId] = useState(null)
  const [dragOverId, setDragOverId] = useState(null)
  const [isAddMenuOpen, setIsAddMenuOpen] = useState(false)
  const fileInputRef = useRef(null)
  
  // Sort layers by zIndex (highest first for visual representation)
  const sortedLayers = [...layers].sort((a, b) => (b.zIndex || 0) - (a.zIndex || 0))

  const handleDragStart = (e, layerId) => {
    setDraggedId(layerId)
    e.dataTransfer.effectAllowed = 'move'
  }

  const handleDragOver = (e, layerId) => {
    e.preventDefault()
    if (layerId !== draggedId) {
      setDragOverId(layerId)
    }
  }

  const handleDragLeave = () => {
    setDragOverId(null)
  }

  const handleDrop = (e, targetId) => {
    e.preventDefault()
    setDragOverId(null)
    
    if (draggedId && targetId && draggedId !== targetId) {
      // Calculate new z-index order
      const draggedLayer = layers.find(l => l.id === draggedId)
      const targetLayer = layers.find(l => l.id === targetId)
      
      if (draggedLayer && targetLayer) {
        // Swap z-indices
        const newLayers = layers.map(layer => {
          if (layer.id === draggedId) {
            return { ...layer, zIndex: targetLayer.zIndex }
          }
          if (layer.id === targetId) {
            return { ...layer, zIndex: draggedLayer.zIndex }
          }
          return layer
        })
        
        onReorderLayers(newLayers)
      }
    }
    
    setDraggedId(null)
  }

  const handleDragEnd = () => {
    setDraggedId(null)
    setDragOverId(null)
  }

  const handleToggleVisibility = (e, layerId) => {
    e.stopPropagation()
    const layer = layers.find(l => l.id === layerId)
    if (layer) {
      onLayerUpdate(layerId, { visible: !layer.visible })
    }
  }

  const handleToggleLock = (e, layerId) => {
    e.stopPropagation()
    const layer = layers.find(l => l.id === layerId)
    if (layer) {
      onLayerUpdate(layerId, { locked: !layer.locked })
    }
  }

  const handleAddLayer = (type) => {
    onAddLayer(type)
    setIsAddMenuOpen(false)
  }

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0]
    if (file && onUploadImage) {
      onUploadImage(file)
      setIsAddMenuOpen(false)
    }
    // Reset input so same file can be selected again
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleUploadClick = () => {
    fileInputRef.current?.click()
    setIsAddMenuOpen(false)
  }

  const getLayerName = (layer) => {
    if (layer.name) return layer.name
    
    // Generate name based on type and field
    if (layer.type === 'text') {
      if (layer.field === 'static') return layer.text || 'Static Text'
      return layer.field?.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) || 'Text Layer'
    }
    if (layer.type === 'image') {
      if (layer.field === 'photo') return 'Photo'
      return 'Image'
    }
    if (layer.type === 'shape') {
      return layer.shape?.charAt(0).toUpperCase() + layer.shape?.slice(1) || 'Shape'
    }
    if (layer.type === 'qr_code') return 'QR Code'
    
    return layer.id
  }

  return (
    <aside className="w-[260px] h-full bg-slate-950 border-r border-slate-800 flex flex-col shrink-0">
      {/* Header */}
      <div className="px-4 py-3 border-b border-slate-800 bg-slate-900/30">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-white">Layers</h3>
          <span className="text-xs text-slate-500 capitalize">{activeView} Side</span>
        </div>
      </div>

      {/* Add Layer Button */}
      <div className="px-3 py-2 border-b border-slate-800">
        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          className="hidden"
        />
        
        <div className="relative">
          <button
            onClick={() => setIsAddMenuOpen(!isAddMenuOpen)}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-blue-500/10 border border-blue-500/30 rounded-lg text-sm font-medium text-blue-400 hover:bg-blue-500/20 transition-colors"
          >
            <Plus size={16} weight="bold" />
            Add Layer
            <CaretDown size={12} className={`transform transition-transform ${isAddMenuOpen ? 'rotate-180' : ''}`} />
          </button>
          
          {isAddMenuOpen && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-slate-900 border border-slate-700 rounded-lg shadow-xl z-50 overflow-hidden">
              <button
                onClick={() => handleAddLayer('text')}
                className="w-full flex items-center gap-3 px-3 py-2.5 hover:bg-slate-800 transition-colors"
              >
                <TextT size={18} className="text-blue-400" />
                <span className="text-sm text-slate-300">Text Layer</span>
              </button>
              <button
                onClick={() => handleAddLayer('image')}
                className="w-full flex items-center gap-3 px-3 py-2.5 hover:bg-slate-800 transition-colors"
              >
                <Image size={18} className="text-purple-400" />
                <span className="text-sm text-slate-300">Image Layer</span>
              </button>
              <button
                onClick={handleUploadClick}
                className="w-full flex items-center gap-3 px-3 py-2.5 hover:bg-slate-800 transition-colors border-t border-slate-800"
              >
                <UploadSimple size={18} className="text-emerald-400" />
                <span className="text-sm text-slate-300">Upload Image</span>
              </button>
              <button
                onClick={() => handleAddLayer('shape')}
                className="w-full flex items-center gap-3 px-3 py-2.5 hover:bg-slate-800 transition-colors border-t border-slate-800"
              >
                <Square size={18} className="text-green-400" />
                <span className="text-sm text-slate-300">Shape Layer</span>
              </button>
              <button
                onClick={() => handleAddLayer('qr_code')}
                className="w-full flex items-center gap-3 px-3 py-2.5 hover:bg-slate-800 transition-colors"
              >
                <QrCode size={18} className="text-amber-400" />
                <span className="text-sm text-slate-300">QR Code Layer</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Layer List */}
      <div className="flex-1 overflow-y-auto py-2">
        {sortedLayers.length === 0 ? (
          <div className="px-4 py-8 text-center">
            <p className="text-sm text-slate-600">No layers yet</p>
            <p className="text-xs text-slate-700 mt-1">Add a layer to get started</p>
          </div>
        ) : (
          <div className="space-y-1 px-2">
            {sortedLayers.map((layer) => {
              const Icon = LAYER_TYPE_ICONS[layer.type] || Square
              const colorClass = LAYER_TYPE_COLORS[layer.type] || 'text-slate-400'
              const isSelected = layer.id === selectedLayerId
              const isDragging = layer.id === draggedId
              const isDragOver = layer.id === dragOverId
              
              return (
                <div
                  key={layer.id}
                  draggable={!layer.locked}
                  onDragStart={(e) => handleDragStart(e, layer.id)}
                  onDragOver={(e) => handleDragOver(e, layer.id)}
                  onDragLeave={handleDragLeave}
                  onDrop={(e) => handleDrop(e, layer.id)}
                  onDragEnd={handleDragEnd}
                  onClick={() => onSelectLayer(layer.id)}
                  className={`
                    group flex items-center gap-2 px-2 py-2 rounded-lg cursor-pointer transition-all
                    ${isSelected 
                      ? 'bg-blue-500/20 border border-blue-500/50' 
                      : 'bg-slate-900/50 border border-transparent hover:bg-slate-800'
                    }
                    ${isDragging ? 'opacity-50' : ''}
                    ${isDragOver ? 'border-blue-400 border-dashed' : ''}
                    ${!layer.visible ? 'opacity-50' : ''}
                  `}
                >
                  {/* Drag Handle */}
                  <div className={`cursor-grab active:cursor-grabbing ${layer.locked ? 'opacity-30' : ''}`}>
                    <DotsSixVertical size={16} className="text-slate-600" />
                  </div>
                  
                  {/* Layer Type Icon */}
                  <div className={`p-1.5 rounded ${isSelected ? 'bg-blue-500/20' : 'bg-slate-800'}`}>
                    <Icon size={14} className={colorClass} weight="duotone" />
                  </div>
                  
                  {/* Layer Name */}
                  <div className="flex-1 min-w-0">
                    <p className={`text-sm truncate ${isSelected ? 'text-white font-medium' : 'text-slate-300'}`}>
                      {getLayerName(layer)}
                    </p>
                    <p className="text-xs text-slate-600 truncate">
                      z: {layer.zIndex || 0}
                    </p>
                  </div>
                  
                  {/* Actions */}
                  <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={(e) => handleToggleVisibility(e, layer.id)}
                      className="p-1 rounded hover:bg-slate-700 transition-colors"
                      title={layer.visible ? 'Hide' : 'Show'}
                    >
                      {layer.visible ? (
                        <Eye size={14} className="text-slate-400" />
                      ) : (
                        <EyeSlash size={14} className="text-slate-600" />
                      )}
                    </button>
                    <button
                      onClick={(e) => handleToggleLock(e, layer.id)}
                      className="p-1 rounded hover:bg-slate-700 transition-colors"
                      title={layer.locked ? 'Unlock' : 'Lock'}
                    >
                      {layer.locked ? (
                        <Lock size={14} className="text-amber-400" />
                      ) : (
                        <LockOpen size={14} className="text-slate-600" />
                      )}
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Layer Count Footer */}
      <div className="px-4 py-2 border-t border-slate-800 bg-slate-900/30">
        <p className="text-xs text-slate-600">
          {sortedLayers.length} layer{sortedLayers.length !== 1 ? 's' : ''}
          {sortedLayers.filter(l => !l.visible).length > 0 && (
            <span className="ml-1">
              ({sortedLayers.filter(l => !l.visible).length} hidden)
            </span>
          )}
        </p>
      </div>
    </aside>
  )
}
