/**
 * Template Library Sidebar
 * Displays saved templates from the database for quick switching
 * Allows activating templates with a single click
 */

import { useState, useEffect, useRef } from 'react'
import { clsx } from 'clsx'
import { 
  Folder, 
  Plus, 
  Check, 
  CircleNotch, 
  Copy, 
  Trash,
  Star,
  Student,
  Chalkboard,
  UserCircle,
  CaretDown,
  CaretRight,
  Download,
  Upload
} from '@phosphor-icons/react'
import { useToast } from '../../contexts/ToastContext'
import { templateAPI } from '../../services/api'

export default function TemplateLibrarySidebar({
  currentTemplateId,
  templateType,
  onSelectTemplate,
  onNewTemplate,
  onDuplicateTemplate,
  onImportBackground,
}) {
  const toast = useToast()
  const [templates, setTemplates] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [expandedSections, setExpandedSections] = useState({
    student: true,
    teacher: true,
    staff: true,
  })
  const [activatingId, setActivatingId] = useState(null)
  const fileInputRef = useRef(null)

  // Fetch templates on mount and when type changes
  useEffect(() => {
    loadTemplates()
  }, [])

  const loadTemplates = async () => {
    setIsLoading(true)
    try {
      // Fetch all template types - handle each individually
      let studentRes = { templates: [] }
      let teacherRes = { templates: [] }
      let staffRes = { templates: [] }
      
      try {
        studentRes = await templateAPI.list({ templateType: 'student' })
      } catch (e) {
        console.warn('Student templates not available:', e.message)
      }
      
      try {
        teacherRes = await templateAPI.list({ templateType: 'teacher' })
      } catch (e) {
        console.warn('Teacher templates not available:', e.message)
      }
      
      try {
        staffRes = await templateAPI.list({ templateType: 'staff' })
      } catch (e) {
        console.warn('Staff templates not available:', e.message)
      }
      
      setTemplates([
        ...(studentRes.templates || []).map(t => ({ ...t, category: 'student' })),
        ...(teacherRes.templates || []).map(t => ({ ...t, category: 'teacher' })),
        ...(staffRes.templates || []).map(t => ({ ...t, category: 'staff' })),
      ])
    } catch (err) {
      console.error('Failed to load templates:', err)
      toast.error('Load Failed', 'Could not load template library')
      setTemplates([]) // Set empty array on failure
    } finally {
      setIsLoading(false)
    }
  }

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section],
    }))
  }

  const handleActivate = async (template) => {
    setActivatingId(template.id)
    try {
      const response = await templateAPI.activate(template.id)
      const templateName = response.name || response.templateName || template.name || template.template_name || 'Template'
      toast.success('Activated', `${templateName} is now active`)
      loadTemplates() // Refresh to show new active status
    } catch (err) {
      console.error('Failed to activate template:', err)
      toast.error('Activation Failed', 'Could not activate template')
    } finally {
      setActivatingId(null)
    }
  }

  const handleDelete = async (template) => {
    if (!confirm(`Delete "${template.name || template.template_name}"? This cannot be undone.`)) {
      return
    }
    
    try {
      await templateAPI.delete(template.id)
      toast.success('Deleted', 'Template removed from library')
      loadTemplates()
    } catch (err) {
      console.error('Failed to delete template:', err)
      toast.error('Delete Failed', 'Could not delete template')
    }
  }

  const handleDuplicate = async (template) => {
    try {
      await templateAPI.duplicate(template.id, `${template.name || template.template_name} (Copy)`)
      toast.success('Duplicated', 'Template copied to library')
      loadTemplates()
    } catch (err) {
      console.error('Failed to duplicate template:', err)
      toast.error('Duplicate Failed', 'Could not duplicate template')
    }
  }

  // Group templates by category
  const groupedTemplates = {
    student: templates.filter(t => t.category === 'student' || t.template_type === 'student'),
    teacher: templates.filter(t => t.category === 'teacher' || t.template_type === 'teacher'),
    staff: templates.filter(t => t.category === 'staff' || t.template_type === 'staff'),
  }

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'student': return Student
      case 'teacher': return Chalkboard
      case 'staff': return UserCircle
      default: return Folder
    }
  }

  const getCategoryColor = (category) => {
    switch (category) {
      case 'student': return 'text-blue-400'
      case 'teacher': return 'text-green-400'
      case 'staff': return 'text-yellow-400'
      default: return 'text-slate-400'
    }
  }

  if (isLoading) {
    return (
      <aside className="w-[240px] bg-slate-900 border-r border-slate-700 flex items-center justify-center">
        <CircleNotch size={24} className="text-blue-400 animate-spin" />
      </aside>
    )
  }

  return (
    <aside className="w-[240px] bg-slate-900 border-r border-slate-700 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="p-3 border-b border-slate-700">
        <h2 className="text-xs font-bold uppercase text-slate-400 tracking-wide flex items-center gap-2">
          <Folder size={14} />
          Template Library
        </h2>
      </div>

      {/* New Template Button */}
      <div className="p-2 border-b border-slate-700">
        <button
          onClick={onNewTemplate}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors"
        >
          <Plus size={16} weight="bold" />
          New Template
        </button>
      </div>

      {/* Template List */}
      <div className="flex-1 overflow-y-auto">
        {['student', 'teacher', 'staff'].map((category) => {
          const CategoryIcon = getCategoryIcon(category)
          const categoryTemplates = groupedTemplates[category]
          const isExpanded = expandedSections[category]
          
          return (
            <div key={category} className="border-b border-slate-800">
              {/* Section Header */}
              <button
                onClick={() => toggleSection(category)}
                className="w-full flex items-center gap-2 px-3 py-2 hover:bg-slate-800 transition-colors"
              >
                {isExpanded ? (
                  <CaretDown size={12} className="text-slate-500" />
                ) : (
                  <CaretRight size={12} className="text-slate-500" />
                )}
                <CategoryIcon size={16} className={getCategoryColor(category)} />
                <span className="text-sm font-medium text-slate-300 capitalize">
                  {category}
                </span>
                <span className="ml-auto text-xs text-slate-500">
                  {categoryTemplates.length}
                </span>
              </button>

              {/* Template Items */}
              {isExpanded && (
                <div className="pb-2">
                  {categoryTemplates.length === 0 ? (
                    <p className="px-6 py-2 text-xs text-slate-500 italic">
                      No templates yet
                    </p>
                  ) : (
                    categoryTemplates.map((template) => (
                      <TemplateItem
                        key={template.id}
                        template={template}
                        isActive={template.is_active}
                        isSelected={template.id === currentTemplateId}
                        isActivating={activatingId === template.id}
                        onSelect={() => onSelectTemplate(template)}
                        onActivate={() => handleActivate(template)}
                        onDuplicate={() => handleDuplicate(template)}
                        onDelete={() => handleDelete(template)}
                      />
                    ))
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Footer Actions */}
      <div className="p-2 border-t border-slate-700 space-y-2">
        <input
          ref={fileInputRef}
          type="file"
          accept="image/png,image/jpeg,image/jpg"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file && onImportBackground) {
              onImportBackground(file, templateType)
            }
            e.target.value = '' // Reset input
          }}
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 text-sm text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg transition-colors"
          title="Import Background Image"
        >
          <Upload size={16} />
          Import Background
        </button>
      </div>
    </aside>
  )
}

function TemplateItem({ 
  template, 
  isActive, 
  isSelected, 
  isActivating,
  onSelect, 
  onActivate, 
  onDuplicate, 
  onDelete 
}) {
  const [showActions, setShowActions] = useState(false)

  return (
    <div
      onClick={onSelect}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
      className={clsx(
        'group relative flex items-center gap-2 px-4 py-2 cursor-pointer transition-colors',
        isSelected ? 'bg-blue-500/10 border-l-2 border-blue-500' : 'hover:bg-slate-800 border-l-2 border-transparent',
      )}
    >
      {/* Template Preview/Icon */}
      <div className={clsx(
        'w-8 h-10 rounded bg-slate-700 flex items-center justify-center text-xs font-bold',
        isActive ? 'ring-2 ring-green-500' : ''
      )}>
        {template.canvas?.backgroundImage ? (
          <img 
            src={template.canvas.backgroundImage} 
            alt="" 
            className="w-full h-full object-cover rounded"
          />
        ) : (
          <span className="text-slate-400">ID</span>
        )}
      </div>

      {/* Template Info */}
      <div className="flex-1 min-w-0">
        <p className={clsx(
          'text-sm font-medium truncate',
          isSelected ? 'text-blue-400' : 'text-slate-300'
        )}>
          {template.name || template.template_name}
        </p>
        <div className="flex items-center gap-1.5">
          {isActive && (
            <span className="flex items-center gap-0.5 text-[10px] text-green-400 font-medium">
              <Star size={10} weight="fill" />
              Active
            </span>
          )}
          <span className="text-[10px] text-slate-500">
            {template.school_level?.replace(/_/g, ' ')}
          </span>
        </div>
      </div>

      {/* Actions (show on hover) */}
      {showActions && !isActivating && (
        <div className="absolute right-2 flex items-center gap-1">
          {!isActive && (
            <button
              onClick={(e) => { e.stopPropagation(); onActivate() }}
              className="p-1 bg-green-600 hover:bg-green-700 text-white rounded transition-colors"
              title="Set as Active"
            >
              <Check size={12} weight="bold" />
            </button>
          )}
          <button
            onClick={(e) => { e.stopPropagation(); onDuplicate() }}
            className="p-1 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded transition-colors"
            title="Duplicate"
          >
            <Copy size={12} />
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); onDelete() }}
            className="p-1 bg-red-600/80 hover:bg-red-600 text-white rounded transition-colors"
            title="Delete"
          >
            <Trash size={12} />
          </button>
        </div>
      )}

      {/* Activating Spinner */}
      {isActivating && (
        <CircleNotch size={16} className="text-blue-400 animate-spin" />
      )}
    </div>
  )
}
