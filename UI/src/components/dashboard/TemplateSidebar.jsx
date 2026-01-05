import { useState, useRef } from 'react'
import { clsx } from 'clsx'
import { Check, UploadSimple, Image } from '@phosphor-icons/react'
import { useToast } from '../../contexts/ToastContext'

export default function TemplateSidebar({ templates, activeTemplate, onTemplateSelect, onUpload }) {
  return (
    <aside className="w-[280px] bg-navy-900 border-r border-navy-700 p-6 overflow-y-auto shrink-0">
      {/* Front Templates */}
      <TemplateSection
        title="FRONT TEMPLATES"
        templates={templates.front}
        active={activeTemplate.front}
        onSelect={(t) => onTemplateSelect('front', t)}
        type="front"
        onUpload={onUpload}
      />

      <div className="h-8" />

      {/* Back Templates */}
      <TemplateSection
        title="BACK TEMPLATES"
        templates={templates.back}
        active={activeTemplate.back}
        onSelect={(t) => onTemplateSelect('back', t)}
        type="back"
        onUpload={onUpload}
      />
    </aside>
  )
}

function TemplateSection({ title, templates, active, onSelect, type, onUpload }) {
  const toast = useToast()
  const fileInputRef = useRef(null)
  const [isDragging, setIsDragging] = useState(false)

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = async (e) => {
    e.preventDefault()
    setIsDragging(false)
    
    const files = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/'))
    if (files.length > 0) {
      await uploadFiles(files)
    }
  }

  const handleFileSelect = async (e) => {
    const files = Array.from(e.target.files)
    if (files.length > 0) {
      await uploadFiles(files)
    }
    e.target.value = ''
  }

  const uploadFiles = async (files) => {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))

    try {
      const res = await fetch('/api/templates/upload', {
        method: 'POST',
        body: formData,
      })

      if (res.ok) {
        toast.success('Upload Complete', `${files.length} template(s) uploaded`)
        onUpload()
      } else {
        throw new Error('Upload failed')
      }
    } catch (err) {
      console.error('Upload error:', err)
      toast.error('Upload Failed', 'Could not upload templates')
    }
  }

  return (
    <div>
      <h3 className="text-xs font-bold uppercase text-slate-500 tracking-widest pb-3 border-b border-navy-700 mb-4">
        {title}
      </h3>

      {/* Template Grid */}
      <div className="grid grid-cols-3 gap-3">
        {(Array.isArray(templates) ? templates : []).map((template, index) => (
          <button
            key={template.path || index}
            onClick={() => onSelect(template)}
            className={clsx(
              'aspect-[2/3] rounded-lg overflow-hidden border-2 transition-all duration-200',
              'hover:opacity-80 hover:-translate-y-0.5 hover:shadow-md',
              active?.path === template.path
                ? 'border-blue-500 opacity-100 ring-4 ring-blue-500/20 scale-[1.03]'
                : 'border-transparent opacity-50 grayscale-[50%]'
            )}
          >
            <div className="relative w-full h-full">
              <img
                src={template.thumbnail || template.path}
                alt=""
                className="w-full h-full object-cover"
                loading="lazy"
              />
              {active?.path === template.path && (
                <div className="absolute top-0 right-0 w-6 h-6 bg-blue-500 rounded-bl-lg flex items-center justify-center">
                  <Check size={14} weight="bold" className="text-white" />
                </div>
              )}
            </div>
          </button>
        ))}
      </div>

      {/* Upload Area */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={clsx(
          'mt-3 h-20 border-2 border-dashed rounded-lg cursor-pointer transition-all duration-200',
          'flex flex-col items-center justify-center gap-2',
          isDragging
            ? 'border-blue-400 bg-blue-500/10 scale-[1.02]'
            : 'border-navy-600 hover:border-blue-500 hover:bg-blue-500/5'
        )}
      >
        <UploadSimple size={28} className={isDragging ? 'text-blue-400' : 'text-slate-600'} />
        <span className={clsx('text-xs font-medium', isDragging ? 'text-blue-300' : 'text-slate-500')}>
          Add Template
        </span>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          multiple
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>

      {/* Empty State */}
      {(!templates || templates.length === 0) && (
        <div className="mt-4 py-6 text-center">
          <Image size={32} className="mx-auto text-slate-700 mb-2" weight="thin" />
          <p className="text-xs text-slate-600">No templates yet</p>
        </div>
      )}
    </div>
  )
}
