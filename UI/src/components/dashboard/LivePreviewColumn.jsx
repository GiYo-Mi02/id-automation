import { useState } from 'react'
import { Eye, ArrowsClockwise, Image, Check, CircleNotch } from '@phosphor-icons/react'
import { Card, Button } from '../shared'
import { formatDistanceToNow } from '../utils/formatTime'
import { useToast } from '../../contexts/ToastContext'
import { api } from '../../services/api'
import { clsx } from 'clsx'

export default function LivePreviewColumn({ 
  latestOutput, 
  templates, 
  activeTemplate, 
  onTemplateSelect, 
  onRegenerate, 
  onView,
  onTemplatesRefresh, // New prop for refreshing template list
}) {
  const toast = useToast()
  const [activatingId, setActivatingId] = useState(null)

  // Handle template activation - persists to database
  const handleTemplateActivate = async (type, template) => {
    // Optimistic update first
    onTemplateSelect(type, template)
    
    // If template has a numeric ID, persist activation to database
    const templateId = parseInt(template.id)
    if (templateId && !isNaN(templateId)) {
      setActivatingId(templateId)
      try {
        const response = await api.post(`/api/templates/db/${templateId}/activate`)
        const templateName = response.name || response.templateName || template.name || template.template_name || 'Template'
        toast.success('Template Activated', `${templateName} is now active`)
        
        // Refresh template list after successful activation
        if (onTemplatesRefresh) {
          onTemplatesRefresh()
        }
      } catch (err) {
        console.error('Failed to activate template:', err.message || JSON.stringify(err))
        toast.error('Activation Failed', 'Could not save template selection')
      } finally {
        setActivatingId(null)
      }
    } else {
      console.warn('Template activation skipped: template.id is not numeric:', template.id)
      toast.info('Info', 'This template cannot be activated (legacy format)')
    }
  }

  return (
    <div className="flex flex-col gap-4 h-full">
      {/* Live Preview Card */}
      <Card className="flex-1 flex flex-col min-h-[300px]">
        <div className="px-4 py-3 border-b border-slate-800 flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-300">LIVE PREVIEW</h3>
          <div className="flex gap-2">
             <button onClick={onRegenerate} className="text-slate-400 hover:text-white transition-colors">
                <ArrowsClockwise size={16} />
             </button>
          </div>
        </div>
        
        <div className="flex-1 p-4 flex flex-col items-center justify-center bg-slate-950/30 relative overflow-hidden">
            {/* Dot Grid Background */}
            <div className="absolute inset-0 opacity-10" 
                style={{ backgroundImage: 'radial-gradient(#475569 1px, transparent 1px)', backgroundSize: '20px 20px' }}>
            </div>

            {latestOutput ? (
                <div className="relative z-10 flex flex-col items-center gap-4">
                    <div className="flex gap-4">
                        {/* Front ID */}
                        <div className="flex flex-col items-center gap-2">
                            <div className="relative group cursor-pointer" onClick={onView}>
                                <img 
                                    src={latestOutput.front_image} 
                                    alt="Front ID" 
                                    className="h-48 w-auto rounded-lg shadow-2xl border border-slate-700 transition-transform group-hover:scale-105"
                                />
                                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center rounded-lg">
                                    <Eye size={24} className="text-white" />
                                </div>
                            </div>
                            <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Front</span>
                        </div>
                        
                        {/* Back ID */}
                        {latestOutput.back_image && (
                            <div className="flex flex-col items-center gap-2">
                                <div className="relative group cursor-pointer" onClick={onView}>
                                    <img 
                                        src={latestOutput.back_image} 
                                        alt="Back ID" 
                                        className="h-48 w-auto rounded-lg shadow-2xl border border-slate-700 transition-transform group-hover:scale-105"
                                    />
                                    <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center rounded-lg">
                                        <Eye size={24} className="text-white" />
                                    </div>
                                </div>
                                <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Back</span>
                            </div>
                        )}
                    </div>
                    <div className="text-center">
                        <p className="text-sm font-medium text-white">{latestOutput.full_name}</p>
                        <p className="text-xs text-slate-500">{latestOutput.id_number}</p>
                    </div>
                </div>
                
            ) : (
                <div className="text-center text-slate-600 z-10">
                    <Image size={48} className="mx-auto mb-2 opacity-50" />
                    <p className="text-sm">Waiting for input...</p>
                </div>
            )}
        </div>
      </Card>

      {/* Quick Template Switcher */}
      <Card className="h-[300px] flex flex-col">
        <div className="px-4 py-3 border-b border-slate-800">
            <h3 className="text-sm font-bold text-slate-300">QUICK TEMPLATES</h3>
            <p className="text-xs text-slate-500 mt-1">Click to activate</p>
        </div>
        <div className="flex-1 overflow-y-auto p-2 space-y-2">
            {/* Check if we have any templates */}
            {(templates?.front?.length === 0 && templates?.back?.length === 0) ? (
              <div className="text-center py-8 text-slate-600">
                <p className="text-sm mb-2">No templates available</p>
                <p className="text-xs">Create a template in the Editor</p>
              </div>
            ) : (
              <>
                {/* Front Templates */}
                {templates?.front?.length > 0 && (
                  <>
                    <div className="px-2 py-1 text-xs font-bold text-slate-500 uppercase tracking-wider">Active Templates</div>
                    {templates.front.map(t => {
                      // Only show templates with numeric IDs (database templates)
                      const numericId = parseInt(t.id)
                      if (!numericId || isNaN(numericId)) return null
                      
                      return (
                        <TemplateItem 
                          key={t.id} 
                          template={t} 
                          isActive={activeTemplate.front?.id === t.id || t.is_active}
                          isActivating={activatingId === numericId}
                          onClick={() => handleTemplateActivate('front', t)}
                        />
                      )
                    })}
                  </>
                )}
                
                {/* Back Templates (if any) */}
                {templates?.back?.length > 0 && (
                  <>
                    <div className="px-2 py-1 text-xs font-bold text-slate-500 uppercase tracking-wider mt-4">Back Templates</div>
                    {templates.back.map(t => {
                      const numericId = parseInt(t.id)
                      if (!numericId || isNaN(numericId)) return null
                      
                      return (
                        <TemplateItem 
                          key={t.id} 
                          template={t} 
                          isActive={activeTemplate.back?.id === t.id || t.is_active}
                          isActivating={activatingId === numericId}
                          onClick={() => handleTemplateActivate('back', t)}
                        />
                      )
                    })}
                  </>
                )}
              </>
            )}
        </div>
      </Card>
    </div>
  )
}

function TemplateItem({ template, isActive, isActivating, onClick }) {
    // Get template name from either field
    const templateName = template.templateName || template.name || template.template_name || 'Untitled'
    
    // Get preview image - try background image or placeholder
    const previewSrc = template.front?.backgroundImage || 
                       template.canvas?.backgroundImage || 
                       template.preview || 
                       template.path || 
                       null
    
    return (
        <button 
            onClick={onClick}
            disabled={isActivating}
            className={clsx(
                "w-full flex items-center gap-3 p-2 rounded-lg transition-all text-left group",
                isActive ? "bg-blue-500/10 border border-blue-500/50" : "hover:bg-slate-800 border border-transparent",
                isActivating && "opacity-70 cursor-wait"
            )}
        >
            <div className="h-10 w-16 bg-slate-800 rounded overflow-hidden relative border border-slate-700">
                {previewSrc ? (
                  <img src={previewSrc} className="w-full h-full object-cover" alt="Template" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <Image size={20} className="text-slate-600" />
                  </div>
                )}
            </div>
            <div className="flex-1 min-w-0">
                <p className={clsx("text-sm font-medium truncate", isActive ? "text-blue-400" : "text-slate-300 group-hover:text-white")}>
                    {templateName}
                </p>
                <p className="text-xs text-slate-500 truncate">
                  {template.templateType || template.template_type || 'student'} • {template.schoolLevel || template.school_level || 'all'}
                </p>
            </div>
            {isActivating ? (
                <CircleNotch size={16} className="text-blue-400 animate-spin" />
            ) : isActive ? (
                <Check size={16} className="text-blue-400" />
            ) : null}
        </button>
    )
}
