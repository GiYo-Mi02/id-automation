import { clsx } from 'clsx'
import { PencilRuler, CaretDown, FloppyDisk } from '@phosphor-icons/react'
import { Dropdown, Button } from '../shared'

export default function EditorTopBar({
  activeView,
  onViewChange,
  templates,
  selectedTemplate,
  onTemplateChange,
  onSave,
  isSaving,
}) {
  const templateOptions = (Array.isArray(templates) ? templates : []).map((t, i) => ({
    value: t.path || i,
    label: t.name || `Template ${i + 1}`,
  }))

  return (
    <header className="h-16 px-6 bg-navy-900 border-b border-navy-700 flex items-center justify-between shrink-0">
      {/* Title */}
      <div className="flex items-center gap-3">
        <PencilRuler size={24} weight="bold" className="text-blue-500" />
        <span className="text-xl font-bold text-slate-100">Visual Layout Editor</span>
      </div>

      {/* View Switcher */}
      <div className="h-10 p-1 bg-navy-800 border border-navy-700 rounded-full flex">
        <button
          onClick={() => onViewChange('front')}
          className={clsx(
            'w-28 h-full rounded-full text-sm font-bold uppercase tracking-wide transition-all duration-200 ease-spring',
            activeView === 'front'
              ? 'bg-blue-600 text-white shadow-md'
              : 'text-slate-400 hover:text-slate-200'
          )}
        >
          Front
        </button>
        <button
          onClick={() => onViewChange('back')}
          className={clsx(
            'w-28 h-full rounded-full text-sm font-bold uppercase tracking-wide transition-all duration-200 ease-spring',
            activeView === 'back'
              ? 'bg-blue-600 text-white shadow-md'
              : 'text-slate-400 hover:text-slate-200'
          )}
        >
          Back
        </button>
      </div>

      {/* Right Side */}
      <div className="flex items-center gap-3">
        {/* Template Dropdown */}
        <Dropdown
          value={selectedTemplate?.path || ''}
          onChange={(value) => {
            const template = templates?.find(t => t.path === value)
            if (template) onTemplateChange(template)
          }}
          options={templateOptions}
          placeholder="Select template..."
          className="w-52"
        />
        
        {/* Save Button */}
        <Button
          variant="primary"
          icon={FloppyDisk}
          onClick={onSave}
          loading={isSaving}
          className="px-6"
        >
          SAVE LAYOUT
        </Button>
      </div>
    </header>
  )
}
