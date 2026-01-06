import { useState, useEffect, useCallback, useMemo } from 'react'
import { useToast } from '../contexts/ToastContext'
import LayerBasedCanvas from '../components/editor/LayerBasedCanvas'
import EnhancedLayersPanel from '../components/editor/EnhancedLayersPanel'
import EnhancedPropertiesPanel from '../components/editor/EnhancedPropertiesPanel'
import TemplateLibrarySidebar from '../components/editor/TemplateLibrarySidebar'
import { templateAPI, layoutAPI } from '../services/api'

// Default layer-based template structure
const createDefaultTemplate = (type = 'student') => ({
  id: null,
  name: 'New Template',
  template_type: type,
  school_level: 'junior_high',
  is_active: false,
  canvas: {
    width: 591,
    height: 1004,
    backgroundColor: '#FFFFFF',
  },
  front: {
    backgroundImage: null,
    layers: [
      {
        id: 'photo-1',
        type: 'image',
        name: 'Photo',
        field: 'photo',
        x: 196,
        y: 180,
        width: 200,
        height: 250,
        zIndex: 1,
        visible: true,
        locked: false,
        objectFit: 'cover',
        borderRadius: 8,
      },
      {
        id: 'name-1',
        type: 'text',
        name: 'Full Name',
        field: 'full_name',
        text: 'STUDENT NAME',
        x: 50,
        y: 460,
        width: 491,
        height: 40,
        zIndex: 2,
        visible: true,
        locked: false,
        fontSize: 28,
        fontFamily: 'Arial',
        fontWeight: 'bold',
        color: '#000000',
        textAlign: 'center',
        wordWrap: false,
        uppercase: true,
      },
      {
        id: 'id-1',
        type: 'text',
        name: 'ID Number',
        field: 'id_number',
        text: '2024-001',
        x: 50,
        y: 510,
        width: 491,
        height: 30,
        zIndex: 3,
        visible: true,
        locked: false,
        fontSize: 22,
        fontFamily: 'Arial',
        fontWeight: 'normal',
        color: '#333333',
        textAlign: 'center',
        wordWrap: false,
      },
      {
        id: 'grade-1',
        type: 'text',
        name: 'Grade & Section',
        field: 'grade_level',
        text: 'Grade 7 - Einstein',
        x: 50,
        y: 550,
        width: 491,
        height: 25,
        zIndex: 4,
        visible: true,
        locked: false,
        fontSize: 18,
        fontFamily: 'Arial',
        fontWeight: 'normal',
        color: '#555555',
        textAlign: 'center',
        wordWrap: false,
      },
    ],
  },
  back: {
    backgroundImage: null,
    layers: [
      {
        id: 'lrn-1',
        type: 'text',
        name: 'LRN',
        field: 'lrn',
        text: 'LRN: 123456789012',
        x: 50,
        y: 100,
        width: 491,
        height: 30,
        zIndex: 1,
        visible: true,
        locked: false,
        fontSize: 16,
        fontFamily: 'Arial',
        fontWeight: 'normal',
        color: '#000000',
        textAlign: 'left',
        wordWrap: false,
      },
      {
        id: 'guardian-1',
        type: 'text',
        name: 'Guardian',
        field: 'guardian_name',
        text: 'Guardian: PARENT NAME',
        x: 50,
        y: 140,
        width: 491,
        height: 30,
        zIndex: 2,
        visible: true,
        locked: false,
        fontSize: 14,
        fontFamily: 'Arial',
        fontWeight: 'normal',
        color: '#333333',
        textAlign: 'left',
        wordWrap: true,
      },
      {
        id: 'address-1',
        type: 'text',
        name: 'Address',
        field: 'address',
        text: 'Address Line Here',
        x: 50,
        y: 180,
        width: 491,
        height: 50,
        zIndex: 3,
        visible: true,
        locked: false,
        fontSize: 12,
        fontFamily: 'Arial',
        fontWeight: 'normal',
        color: '#333333',
        textAlign: 'left',
        wordWrap: true,
      },
      {
        id: 'contact-1',
        type: 'text',
        name: 'Emergency Contact',
        field: 'emergency_contact',
        text: 'Emergency: 09171234567',
        x: 50,
        y: 240,
        width: 491,
        height: 25,
        zIndex: 4,
        visible: true,
        locked: false,
        fontSize: 14,
        fontFamily: 'Arial',
        fontWeight: 'normal',
        color: '#333333',
        textAlign: 'left',
        wordWrap: false,
      },
      {
        id: 'qr-1',
        type: 'qr_code',
        name: 'QR Code',
        field: 'id_number',
        x: 220,
        y: 700,
        width: 150,
        height: 150,
        zIndex: 5,
        visible: true,
        locked: false,
        backgroundColor: '#FFFFFF',
        foregroundColor: '#000000',
      },
    ],
  },
})

export default function EditorPage() {
  const toast = useToast()
  
  // Template state
  const [currentSide, setCurrentSide] = useState('front')
  const [template, setTemplate] = useState(createDefaultTemplate())
  const [templateList, setTemplateList] = useState([])
  const [templateType, setTemplateType] = useState('student')
  const [selectedLayerId, setSelectedLayerId] = useState(null)
  
  // Editor state
  const [zoom, setZoom] = useState(100)
  const [showGrid, setShowGrid] = useState(true)
  const [snapToGrid, setSnapToGrid] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)

  // Undo/Redo history
  const [history, setHistory] = useState([])
  const [historyIndex, setHistoryIndex] = useState(-1)

  // Load templates from database on mount
  useEffect(() => {
    loadTemplates()
  }, [templateType])

  const loadTemplates = async () => {
    setIsLoading(true)
    try {
      // Try to load from database first
      const response = await templateAPI.list({ templateType: templateType })
      if (response.templates && response.templates.length > 0) {
        setTemplateList(response.templates)
        // Load active template or first available
        const active = response.templates.find(t => t.is_active) || response.templates[0]
        if (active) {
          await loadTemplate(active.id)
        }
      } else {
        // Fall back to legacy layout.json
        await loadLegacyLayout()
      }
    } catch (err) {
      console.error('Failed to load templates:', err)
      // Fall back to legacy layout
      await loadLegacyLayout()
    } finally {
      setIsLoading(false)
    }
  }

  const loadTemplate = async (templateId) => {
    try {
      const data = await templateAPI.get(templateId)
      if (data) {
        console.log('Loaded template from API:', data)
        setTemplate({
          id: data.id,
          name: data.templateName,
          template_type: data.templateType,
          school_level: data.schoolLevel,
          is_active: data.isActive,
          canvas: {
            width: data.canvas?.width || 591,
            height: data.canvas?.height || 1004,
            backgroundColor: data.canvas?.backgroundColor || '#FFFFFF',
          },
          front: { 
            backgroundImage: data.front?.backgroundImage || null,
            layers: data.front?.layers || [] 
          },
          back: { 
            backgroundImage: data.back?.backgroundImage || null,
            layers: data.back?.layers || [] 
          },
        })
        console.log('Set template state - Front layers:', data.front?.layers?.length, 'Back layers:', data.back?.layers?.length)
        setHasUnsavedChanges(false)
        pushToHistory({
          id: data.id,
          name: data.templateName,
          template_type: data.templateType,
          school_level: data.schoolLevel,
          is_active: data.isActive,
          canvas: {
            width: data.canvas?.width || 591,
            height: data.canvas?.height || 1004,
            backgroundColor: data.canvas?.backgroundColor || '#FFFFFF',
          },
          front: { 
            backgroundImage: data.front?.backgroundImage || null,
            layers: data.front?.layers || [] 
          },
          back: { 
            backgroundImage: data.back?.backgroundImage || null,
            layers: data.back?.layers || [] 
          },
        })
      }
    } catch (err) {
      console.error('Failed to load template:', err)
      toast.error('Load Failed', 'Could not load template from database')
    }
  }

  const loadLegacyLayout = async () => {
    try {
      const data = await layoutAPI.get()
      // Convert legacy layout to layer-based format
      const converted = convertLegacyToLayers(data)
      setTemplate(converted)
      pushToHistory(converted)
    } catch (err) {
      console.error('Failed to load legacy layout:', err)
      // Use default template
      setTemplate(createDefaultTemplate(templateType))
    }
  }

  // Convert old layout format to new layer-based format
  const convertLegacyToLayers = (legacyLayout) => {
    const newTemplate = createDefaultTemplate(templateType)
    
    if (legacyLayout.front) {
      newTemplate.front.layers = Object.entries(legacyLayout.front).map(([key, value], index) => ({
        id: `legacy-front-${key}`,
        type: key === 'photo' ? 'image' : 'text',
        name: key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' '),
        field: key,
        x: value.x || 0,
        y: value.y || 0,
        width: value.width || 200,
        height: value.height || 30,
        zIndex: index + 1,
        visible: true,
        locked: false,
        ...(key !== 'photo' && {
          fontSize: value.fontSize || 16,
          fontWeight: value.fontWeight || 'normal',
          color: value.color || '#000000',
          textAlign: 'left',
          wordWrap: false,
        }),
        ...(key === 'photo' && {
          objectFit: 'cover',
          borderRadius: 0,
        }),
      }))
    }
    
    if (legacyLayout.back) {
      newTemplate.back.layers = Object.entries(legacyLayout.back).map(([key, value], index) => ({
        id: `legacy-back-${key}`,
        type: 'text',
        name: key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' '),
        field: key,
        x: value.x || 0,
        y: value.y || 0,
        width: 200,
        height: value.height || 30,
        zIndex: index + 1,
        visible: true,
        locked: false,
        fontSize: value.fontSize || 16,
        fontWeight: value.fontWeight || 'normal',
        color: value.color || '#000000',
        textAlign: 'left',
        wordWrap: false,
      }))
    }
    
    return newTemplate
  }

  // Push state to history for undo/redo
  const pushToHistory = (state) => {
    const newHistory = history.slice(0, historyIndex + 1)
    newHistory.push(JSON.parse(JSON.stringify(state)))
    if (newHistory.length > 50) newHistory.shift() // Limit history
    setHistory(newHistory)
    setHistoryIndex(newHistory.length - 1)
  }

  const handleUndo = () => {
    if (historyIndex > 0) {
      setHistoryIndex(historyIndex - 1)
      setTemplate(JSON.parse(JSON.stringify(history[historyIndex - 1])))
      setHasUnsavedChanges(true)
    }
  }

  const handleRedo = () => {
    if (historyIndex < history.length - 1) {
      setHistoryIndex(historyIndex + 1)
      setTemplate(JSON.parse(JSON.stringify(history[historyIndex + 1])))
      setHasUnsavedChanges(true)
    }
  }

  // Get current layers for the active side
  const currentLayers = useMemo(() => {
    return template[currentSide]?.layers || []
  }, [template, currentSide])

  // Get selected layer
  const selectedLayer = useMemo(() => {
    return currentLayers.find(l => l.id === selectedLayerId)
  }, [currentLayers, selectedLayerId])

  // Update a layer
  const updateLayer = useCallback((layerId, updates) => {
    setTemplate(prev => {
      const newTemplate = { ...prev }
      const layers = [...(newTemplate[currentSide]?.layers || [])]
      const layerIndex = layers.findIndex(l => l.id === layerId)
      
      if (layerIndex !== -1) {
        layers[layerIndex] = { ...layers[layerIndex], ...updates }
        newTemplate[currentSide] = { ...newTemplate[currentSide], layers }
      }
      
      return newTemplate
    })
    setHasUnsavedChanges(true)
  }, [currentSide])

  // Handle layer position change from canvas drag
  const handleLayerMove = useCallback((layerId, x, y) => {
    updateLayer(layerId, { x: Math.round(x), y: Math.round(y) })
  }, [updateLayer])

  // Handle layer resize from canvas handles
  const handleLayerResize = useCallback((layerId, x, y, width, height) => {
    updateLayer(layerId, { 
      x: Math.round(x), 
      y: Math.round(y), 
      width: Math.round(width), 
      height: Math.round(height) 
    })
  }, [updateLayer])

  // Reorder layers (update z-index)
  const handleReorderLayers = useCallback((newLayers) => {
    setTemplate(prev => ({
      ...prev,
      [currentSide]: {
        ...prev[currentSide],
        layers: newLayers.map((layer, index) => ({
          ...layer,
          zIndex: index + 1,
        })),
      },
    }))
    setHasUnsavedChanges(true)
  }, [currentSide])

  // Add a new layer
  const handleAddLayer = useCallback((type) => {
    const newLayer = {
      id: `${type}-${Date.now()}`,
      type,
      name: `New ${type.charAt(0).toUpperCase() + type.slice(1)}`,
      field: type === 'text' ? 'static' : type === 'image' ? 'photo' : type === 'qr_code' ? 'id_number' : null,
      x: 100,
      y: 100,
      width: type === 'text' ? 200 : type === 'qr_code' ? 100 : 150,
      height: type === 'text' ? 30 : type === 'qr_code' ? 100 : 150,
      zIndex: currentLayers.length + 1,
      visible: true,
      locked: false,
      ...(type === 'text' && {
        text: 'New Text',
        fontSize: 16,
        fontFamily: 'Arial',
        fontWeight: 'normal',
        color: '#000000',
        textAlign: 'left',
        wordWrap: false,
      }),
      ...(type === 'image' && {
        objectFit: 'cover',
        borderRadius: 0,
      }),
      ...(type === 'shape' && {
        shape: 'rectangle',
        fill: '#3B82F6',
        stroke: null,
        strokeWidth: 0,
        borderRadius: 0,
      }),
      ...(type === 'qr_code' && {
        backgroundColor: '#FFFFFF',
        foregroundColor: '#000000',
      }),
    }

    setTemplate(prev => ({
      ...prev,
      [currentSide]: {
        ...prev[currentSide],
        layers: [...(prev[currentSide]?.layers || []), newLayer],
      },
    }))
    setSelectedLayerId(newLayer.id)
    setHasUnsavedChanges(true)
  }, [currentSide, currentLayers.length])

  // Handle image upload
  const handleUploadImage = useCallback(async (file) => {
    if (!file) return
    
    // Validate file type
    if (!file.type.startsWith('image/')) {
      toast.error('Invalid File', 'Please select an image file')
      return
    }
    
    try {
      toast.info('Uploading', 'Uploading image...')
      
      // Create FormData
      const formData = new FormData()
      formData.append('file', file)
      
      // Upload to server
      const response = await fetch('http://localhost:8000/api/upload/image', {
        method: 'POST',
        body: formData,
      })
      
      if (!response.ok) {
        throw new Error('Upload failed')
      }
      
      const data = await response.json()
      
      // Calculate reasonable size while maintaining aspect ratio
      const maxSize = 200
      const aspectRatio = data.width / data.height
      let width, height
      
      if (aspectRatio > 1) {
        width = Math.min(maxSize, data.width)
        height = width / aspectRatio
      } else {
        height = Math.min(maxSize, data.height)
        width = height * aspectRatio
      }
      
      // Convert relative URL to absolute URL (fix port mismatch)
      const API_BASE_URL = 'http://localhost:8000'
      const imageUrl = data.url.startsWith('http') ? data.url : `${API_BASE_URL}${data.url}`
      
      // Create new image layer with uploaded image
      const newLayer = {
        id: `image-${Date.now()}`,
        type: 'image',
        name: file.name.replace(/\.[^/.]+$/, ''), // Remove extension
        src: imageUrl, // Use the FULL URL (with correct port)
        field: null, // Static image, not a data field
        x: 100,
        y: 100,
        width: Math.round(width),
        height: Math.round(height),
        zIndex: currentLayers.length + 1,
        visible: true,
        locked: false,
        objectFit: 'contain',
        borderRadius: 0,
      }
      
      setTemplate(prev => ({
        ...prev,
        [currentSide]: {
          ...prev[currentSide],
          layers: [...(prev[currentSide]?.layers || []), newLayer],
        },
      }))
      setSelectedLayerId(newLayer.id)
      setHasUnsavedChanges(true)
      
      toast.success('Image Added', 'Image uploaded and added to canvas')
    } catch (err) {
      console.error('Upload error:', err)
      toast.error('Upload Failed', 'Could not upload image')
    }
  }, [currentLayers.length, currentSide, toast])

  // Delete a layer
  const handleDeleteLayer = useCallback((layerId) => {
    setTemplate(prev => ({
      ...prev,
      [currentSide]: {
        ...prev[currentSide],
        layers: (prev[currentSide]?.layers || []).filter(l => l.id !== layerId),
      },
    }))
    if (selectedLayerId === layerId) {
      setSelectedLayerId(null)
    }
    setHasUnsavedChanges(true)
  }, [currentSide, selectedLayerId])

  // Duplicate a layer
  const handleDuplicateLayer = useCallback((layerId) => {
    const layer = currentLayers.find(l => l.id === layerId)
    if (!layer) return

    const newLayer = {
      ...JSON.parse(JSON.stringify(layer)),
      id: `${layer.type}-${Date.now()}`,
      name: `${layer.name} (Copy)`,
      x: layer.x + 20,
      y: layer.y + 20,
      zIndex: currentLayers.length + 1,
    }

    setTemplate(prev => ({
      ...prev,
      [currentSide]: {
        ...prev[currentSide],
        layers: [...(prev[currentSide]?.layers || []), newLayer],
      },
    }))
    setSelectedLayerId(newLayer.id)
    setHasUnsavedChanges(true)
  }, [currentSide, currentLayers])

  // Save template to database
  const handleSave = async () => {
    setIsSaving(true)
    try {
      const templateData = {
        templateName: template.name,
        templateType: templateType,
        schoolLevel: template.school_level || 'junior_high',
        isActive: template.is_active || false,
        canvas: {
          width: template.canvas?.width || 591,
          height: template.canvas?.height || 1004,
          backgroundColor: template.canvas?.backgroundColor || '#FFFFFF',
        },
        front: {
          backgroundImage: template.front?.backgroundImage || null,
          layers: template.front?.layers || [],
        },
        back: {
          backgroundImage: template.back?.backgroundImage || null,
          layers: template.back?.layers || [],
        },
        metadata: {
          version: '1.0.0',
          updatedAt: new Date().toISOString(),
        },
      }

      let savedTemplate
      if (template.id) {
        try {
          // Update existing template
          savedTemplate = await templateAPI.update(template.id, templateData)
        } catch (updateErr) {
          // If 404, template doesn't exist - create instead
          if (updateErr.message?.includes('404') || updateErr.message?.includes('not found')) {
            console.warn('Template ID', template.id, 'not found. Creating new template instead.')
            savedTemplate = await templateAPI.create(templateData)
            setTemplate(prev => ({ ...prev, id: savedTemplate.id }))
          } else {
            throw updateErr
          }
        }
      } else {
        // Create new template
        savedTemplate = await templateAPI.create(templateData)
        setTemplate(prev => ({ ...prev, id: savedTemplate.id }))
      }

      // Also save to legacy layout.json for backward compatibility
      await layoutAPI.save(convertLayersToLegacy(template))

      pushToHistory(template)
      setHasUnsavedChanges(false)
      
      // Refresh template list to show updated template
      await loadTemplates()
      
      toast.success('Template Saved', 'Your template changes have been saved to the database')
    } catch (err) {
      console.error('Save failed:', err.message || JSON.stringify(err))
      const errorMsg = err.message || 'Could not save template. Check console for details.'
      toast.error('Save Failed', errorMsg)
    } finally {
      setIsSaving(false)
    }
  }

  // Convert layer-based format back to legacy for backward compatibility
  const convertLayersToLegacy = (tmpl) => {
    const legacy = { front: {}, back: {} }
    
    const processLayers = (layers, side) => {
      layers.forEach(layer => {
        const key = layer.field || layer.name.toLowerCase().replace(/\s+/g, '_')
        legacy[side][key] = {
          x: layer.x,
          y: layer.y,
          width: layer.width,
          height: layer.height,
          ...(layer.type === 'text' && {
            fontSize: layer.fontSize,
            fontWeight: layer.fontWeight,
            color: layer.color,
          }),
        }
      })
    }
    
    if (tmpl.front?.layers) processLayers(tmpl.front.layers, 'front')
    if (tmpl.back?.layers) processLayers(tmpl.back.layers, 'back')
    
    return legacy
  }

  // Template type change
  const handleTemplateTypeChange = (newType) => {
    if (hasUnsavedChanges) {
      if (!confirm('You have unsaved changes. Switch template type anyway?')) {
        return
      }
    }
    setTemplateType(newType)
    setSelectedLayerId(null)
  }

  // New template
  const handleNewTemplate = () => {
    if (hasUnsavedChanges) {
      if (!confirm('You have unsaved changes. Create new template anyway?')) {
        return
      }
    }
    setTemplate(createDefaultTemplate(templateType))
    setSelectedLayerId(null)
    setHasUnsavedChanges(false)
  }

  // Import background image
  const handleImportBackground = async (file, category) => {
    try {
      // Upload the background image
      const formData = new FormData()
      formData.append('file', file)
      formData.append('category', category || templateType)
      
      const response = await fetch('/api/templates/db/upload-background', {
        method: 'POST',
        body: formData,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      })
      
      if (!response.ok) {
        throw new Error('Upload failed')
      }
      
      const data = await response.json()
      const backgroundUrl = data.url || `/api/templates/backgrounds/${data.filename}`
      
      // Update ONLY the current side's background (front or back)
      // IMPORTANT: Preserve existing layers for this side
      setTemplate(prev => ({
        ...prev,
        [currentSide]: {
          ...prev[currentSide],
          backgroundImage: backgroundUrl,
        },
      }))
      
      setHasUnsavedChanges(true)
      toast.success('Background Imported', `${currentSide === 'front' ? 'Front' : 'Back'} background updated. Layers preserved.`)
    } catch (err) {
      console.error('Failed to import background:', err)
      toast.error('Import Failed', 'Could not upload background image')
    }
  }

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center bg-slate-950">
        <div className="text-white">Loading editor...</div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col bg-slate-950">
      {/* Top Bar */}
      <div className="h-14 bg-slate-900 border-b border-slate-700 flex items-center justify-between px-4">
        {/* Left: Template Info */}
        <div className="flex items-center gap-4">
          <input
            type="text"
            value={template.name || ""}
            onChange={(e) => {
              setTemplate(prev => ({ ...prev, name: e.target.value }))
              setHasUnsavedChanges(true)
            }}
            className="bg-slate-800 text-white px-3 py-1.5 rounded border border-slate-600 focus:border-blue-500 focus:outline-none"
          />
          
          <select
            value={templateType || "student"}
            onChange={(e) => handleTemplateTypeChange(e.target.value)}
            className="bg-slate-800 text-white px-3 py-1.5 rounded border border-slate-600 focus:border-blue-500 focus:outline-none"
          >
            <option value="student">Student ID</option>
            <option value="teacher">Teacher ID</option>
            <option value="staff">Staff ID</option>
          </select>

          {hasUnsavedChanges && (
            <span className="text-amber-400 text-sm">● Unsaved changes</span>
          )}
        </div>

        {/* Center: Side Toggle */}
        <div className="flex items-center bg-slate-800 rounded-lg p-1">
          <button
            onClick={() => setCurrentSide('front')}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
              currentSide === 'front'
                ? 'bg-blue-600 text-white'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Front
          </button>
          <button
            onClick={() => setCurrentSide('back')}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
              currentSide === 'back'
                ? 'bg-blue-600 text-white'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Back
          </button>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleUndo}
            disabled={historyIndex <= 0}
            className="p-2 text-slate-400 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
            title="Undo (Ctrl+Z)"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
            </svg>
          </button>
          <button
            onClick={handleRedo}
            disabled={historyIndex >= history.length - 1}
            className="p-2 text-slate-400 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
            title="Redo (Ctrl+Y)"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 10h-10a8 8 0 00-8 8v2M21 10l-6 6m6-6l-6-6" />
            </svg>
          </button>

          <div className="w-px h-6 bg-slate-700 mx-2" />

          <button
            onClick={handleNewTemplate}
            className="px-3 py-1.5 text-sm text-slate-300 hover:text-white border border-slate-600 rounded hover:border-slate-500"
          >
            New
          </button>
          
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="px-4 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isSaving ? (
              <>
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Saving...
              </>
            ) : (
              'Save Template'
            )}
          </button>
        </div>
      </div>

      {/* Main Editor Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Far Left: Template Library */}
        <TemplateLibrarySidebar
          currentTemplateId={template.id}
          templateType={templateType}
          onSelectTemplate={(t) => loadTemplate(t.id)}
          onNewTemplate={handleNewTemplate}
          onImportBackground={handleImportBackground}
          onDuplicateTemplate={async (t) => {
            try {
              await templateAPI.duplicate(t.id, `${t.name} (Copy)`)
              toast.success('Duplicated', 'Template copied')
            } catch (err) {
              toast.error('Failed', 'Could not duplicate template')
            }
          }}
        />

        {/* Left Panel: Layers */}
        <EnhancedLayersPanel
          layers={currentLayers}
          selectedLayerId={selectedLayerId}
          onSelectLayer={setSelectedLayerId}
          onReorderLayers={handleReorderLayers}
          onAddLayer={handleAddLayer}
          onUploadImage={handleUploadImage}
          onDeleteLayer={handleDeleteLayer}
          onToggleVisibility={(id) => {
            const layer = currentLayers.find(l => l.id === id)
            if (layer) updateLayer(id, { visible: !layer.visible })
          }}
          onToggleLock={(id) => {
            const layer = currentLayers.find(l => l.id === id)
            if (layer) updateLayer(id, { locked: !layer.locked })
          }}
        />

        {/* Canvas Area */}
        <LayerBasedCanvas
          template={template}
          currentSide={currentSide}
          templateType={templateType}
          selectedLayerId={selectedLayerId}
          onSelectLayer={setSelectedLayerId}
          onLayerMove={handleLayerMove}
          onLayerResize={handleLayerResize}
          zoom={zoom}
          showGrid={showGrid}
          snapToGrid={snapToGrid}
        />

        {/* Floating Zoom Controls */}
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-2 bg-slate-800 rounded-lg px-3 py-2 shadow-lg border border-slate-700">
          <button
            onClick={() => setZoom(Math.max(25, zoom - 25))}
            className="p-1 text-slate-400 hover:text-white"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
            </svg>
          </button>
          <span className="text-white text-sm w-14 text-center">{zoom}%</span>
          <button
            onClick={() => setZoom(Math.min(200, zoom + 25))}
            className="p-1 text-slate-400 hover:text-white"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
          </button>
          <div className="w-px h-4 bg-slate-600 mx-1" />
          <button
            onClick={() => setShowGrid(!showGrid)}
            className={`p-1 ${showGrid ? 'text-blue-400' : 'text-slate-400'} hover:text-white`}
            title="Toggle Grid"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v14a1 1 0 01-1 1H5a1 1 0 01-1-1V5z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 9h16M4 15h16M9 4v16M15 4v16" />
            </svg>
          </button>
          <button
            onClick={() => setSnapToGrid(!snapToGrid)}
            className={`p-1 ${snapToGrid ? 'text-blue-400' : 'text-slate-400'} hover:text-white`}
            title="Snap to Grid"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </button>
        </div>

        {/* Right Panel: Properties */}
        <EnhancedPropertiesPanel
          selectedLayer={selectedLayer}
          onLayerUpdate={(layerId, updates) => updateLayer(layerId, updates)}
          onLayerDelete={() => selectedLayerId && handleDeleteLayer(selectedLayerId)}
          onLayerDuplicate={() => selectedLayerId && handleDuplicateLayer(selectedLayerId)}
          onLayerMoveUp={() => {
            if (!selectedLayerId) return
            const currentIndex = currentLayers.findIndex(l => l.id === selectedLayerId)
            if (currentIndex > 0) {
              const newLayers = [...currentLayers]
              ;[newLayers[currentIndex], newLayers[currentIndex - 1]] = [newLayers[currentIndex - 1], newLayers[currentIndex]]
              handleReorderLayers(newLayers)
            }
          }}
          onLayerMoveDown={() => {
            if (!selectedLayerId) return
            const currentIndex = currentLayers.findIndex(l => l.id === selectedLayerId)
            if (currentIndex < currentLayers.length - 1) {
              const newLayers = [...currentLayers]
              ;[newLayers[currentIndex], newLayers[currentIndex + 1]] = [newLayers[currentIndex + 1], newLayers[currentIndex]]
              handleReorderLayers(newLayers)
            }
          }}
          templateType={templateType}
        />
      </div>
    </div>
  )
}
