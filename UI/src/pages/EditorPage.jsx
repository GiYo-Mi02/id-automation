import { useState, useEffect, useCallback } from 'react'
import { useToast } from '../contexts/ToastContext'
import EditorTopBar from '../components/editor/EditorTopBar'
import LayersPanel from '../components/editor/LayersPanel'
import EditorCanvas from '../components/editor/EditorCanvas'
import PropertiesPanel from '../components/editor/PropertiesPanel'

const defaultLayout = {
  front: {
    photo: { x: 50, y: 100, width: 200, height: 250 },
    name: { x: 50, y: 380, fontSize: 24, fontWeight: 'bold', color: '#000000' },
    id_number: { x: 50, y: 420, fontSize: 18, fontWeight: 'normal', color: '#333333' },
    grade_section: { x: 50, y: 455, fontSize: 16, fontWeight: 'normal', color: '#555555' },
  },
  back: {
    lrn: { x: 50, y: 100, fontSize: 18, fontWeight: 'normal', color: '#000000' },
    guardian: { x: 50, y: 140, fontSize: 16, fontWeight: 'normal', color: '#333333' },
    address: { x: 50, y: 180, fontSize: 14, fontWeight: 'normal', color: '#333333' },
    contact: { x: 50, y: 220, fontSize: 14, fontWeight: 'normal', color: '#333333' },
  },
}

export default function EditorPage() {
  const toast = useToast()
  
  const [activeView, setActiveView] = useState('front') // 'front' | 'back'
  const [templates, setTemplates] = useState({ front: [], back: [] })
  const [selectedTemplate, setSelectedTemplate] = useState({ front: null, back: null })
  const [layout, setLayout] = useState(defaultLayout)
  const [selectedElement, setSelectedElement] = useState(null)
  const [zoom, setZoom] = useState(100)
  const [showGrid, setShowGrid] = useState(true)
  const [snapToGrid, setSnapToGrid] = useState(true)
  const [isSaving, setIsSaving] = useState(false)

  // Fetch templates and layout on mount
  useEffect(() => {
    fetchTemplates()
    fetchLayout()
  }, [])

  const fetchTemplates = async () => {
    try {
      const res = await fetch('/api/templates')
      if (res.ok) {
        const data = await res.json()
        setTemplates(data)
        if (data.front?.length > 0) {
          setSelectedTemplate(prev => ({ ...prev, front: data.front[0] }))
        }
        if (data.back?.length > 0) {
          setSelectedTemplate(prev => ({ ...prev, back: data.back[0] }))
        }
      }
    } catch (err) {
      console.error('Failed to fetch templates:', err)
    }
  }

  const fetchLayout = async () => {
    try {
      const res = await fetch('/api/layout')
      if (res.ok) {
        const data = await res.json()
        setLayout(prev => ({ ...prev, ...data }))
      }
    } catch (err) {
      console.error('Failed to fetch layout:', err)
    }
  }

  const handleElementSelect = (elementKey) => {
    setSelectedElement(elementKey)
  }

  const handleElementUpdate = useCallback((elementKey, updates) => {
    setLayout(prev => ({
      ...prev,
      [activeView]: {
        ...prev[activeView],
        [elementKey]: {
          ...prev[activeView][elementKey],
          ...updates,
        },
      },
    }))
  }, [activeView])

  const handlePositionChange = useCallback((elementKey, x, y) => {
    handleElementUpdate(elementKey, { x, y })
  }, [handleElementUpdate])

  const handleSizeChange = useCallback((elementKey, width, height) => {
    handleElementUpdate(elementKey, { width, height })
  }, [handleElementUpdate])

  const handleSaveLayout = async () => {
    setIsSaving(true)
    try {
      const res = await fetch('/api/layout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(layout),
      })

      if (res.ok) {
        toast.success('Layout Saved', 'Your layout changes have been saved')
      } else {
        throw new Error('Save failed')
      }
    } catch (err) {
      toast.error('Save Failed', 'Could not save layout changes')
    } finally {
      setIsSaving(false)
    }
  }

  const handleResetPosition = () => {
    if (!selectedElement) return
    
    const defaults = defaultLayout[activeView][selectedElement]
    if (defaults) {
      handleElementUpdate(selectedElement, { x: defaults.x, y: defaults.y })
    }
  }

  const currentLayout = layout[activeView] || {}
  const currentTemplate = selectedTemplate[activeView]

  return (
    <div className="h-full flex flex-col bg-navy-950">
      <EditorTopBar
        activeView={activeView}
        onViewChange={setActiveView}
        templates={templates[activeView]}
        selectedTemplate={currentTemplate}
        onTemplateChange={(t) => setSelectedTemplate(prev => ({ ...prev, [activeView]: t }))}
      />

      <div className="flex-1 flex overflow-hidden">
        {/* Layers Panel */}
        <LayersPanel
          elements={currentLayout}
          selectedElement={selectedElement}
          onSelect={handleElementSelect}
          activeView={activeView}
        />

        {/* Canvas Area */}
        <EditorCanvas
          template={currentTemplate}
          layout={currentLayout}
          selectedElement={selectedElement}
          onElementSelect={handleElementSelect}
          onPositionChange={handlePositionChange}
          onSizeChange={handleSizeChange}
          zoom={zoom}
          onZoomChange={setZoom}
          showGrid={showGrid}
          onShowGridChange={setShowGrid}
          snapToGrid={snapToGrid}
          onSnapToGridChange={setSnapToGrid}
        />

        {/* Properties Panel */}
        <PropertiesPanel
          selectedElement={selectedElement}
          elementData={selectedElement ? currentLayout[selectedElement] : null}
          onUpdate={(updates) => selectedElement && handleElementUpdate(selectedElement, updates)}
          onReset={handleResetPosition}
          onSave={handleSaveLayout}
          isSaving={isSaving}
        />
      </div>
    </div>
  )
}
