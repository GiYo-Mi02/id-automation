import { useState } from 'react'
import { clsx } from 'clsx'
import { Eye, EyeSlash, Image, TextT, CaretLeft, CaretRight } from '@phosphor-icons/react'

const elementIcons = {
  photo: Image,
  name: TextT,
  id_number: TextT,
  grade_section: TextT,
  lrn: TextT,
  guardian: TextT,
  address: TextT,
  contact: TextT,
}

const elementLabels = {
  photo: 'Photo Area',
  name: 'Name Field',
  id_number: 'ID Number',
  grade_section: 'Grade & Section',
  lrn: 'LRN Number',
  guardian: 'Guardian Name',
  address: 'Address',
  contact: 'Contact Number',
}

export default function LayersPanel({ elements, selectedElement, onSelect, activeView }) {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [hiddenLayers, setHiddenLayers] = useState(new Set())

  const toggleVisibility = (key, e) => {
    e.stopPropagation()
    setHiddenLayers(prev => {
      const next = new Set(prev)
      if (next.has(key)) {
        next.delete(key)
      } else {
        next.add(key)
      }
      return next
    })
  }

  const elementKeys = Object.keys(elements)

  return (
    <aside
      className={clsx(
        'h-full bg-navy-900 border-r border-navy-700 flex flex-col shrink-0 transition-all duration-200',
        isCollapsed ? 'w-[60px]' : 'w-[240px]'
      )}
    >
      {/* Header */}
      <div className="h-12 px-4 flex items-center border-b border-navy-700">
        {!isCollapsed && (
          <h3 className="text-xs font-bold uppercase text-slate-500 tracking-widest">
            Layers
          </h3>
        )}
      </div>

      {/* Layer List */}
      <div className="flex-1 overflow-y-auto p-3">
        <ul className="space-y-1">
          {elementKeys.map((key) => {
            const Icon = elementIcons[key] || TextT
            const label = elementLabels[key] || key
            const isHidden = hiddenLayers.has(key)
            const isSelected = selectedElement === key

            return (
              <li key={key}>
                <button
                  onClick={() => onSelect(key)}
                  className={clsx(
                    'w-full h-10 rounded-md flex items-center gap-3 px-3 transition-all duration-150',
                    'hover:bg-navy-800',
                    isSelected
                      ? 'bg-blue-600/20 border-l-2 border-blue-500 text-blue-200'
                      : 'text-slate-300 border-l-2 border-transparent'
                  )}
                >
                  <Icon
                    size={16}
                    className={isSelected ? 'text-blue-400' : 'text-slate-500'}
                  />
                  {!isCollapsed && (
                    <>
                      <span className="flex-1 text-sm truncate text-left">{label}</span>
                      <div
                        onClick={(e) => toggleVisibility(key, e)}
                        className={clsx(
                          'p-1 rounded hover:bg-navy-700 transition-colors cursor-pointer',
                          isHidden ? 'text-slate-700' : 'text-slate-500 hover:text-blue-400'
                        )}
                      >
                        {isHidden ? <EyeSlash size={16} /> : <Eye size={16} />}
                      </div>
                    </>
                  )}
                </button>
              </li>
            )
          })}
        </ul>
      </div>

      {/* Collapse Toggle */}
      <div className="p-3 border-t border-navy-700">
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="w-full h-10 flex items-center justify-center rounded-lg bg-navy-800 border border-navy-700 text-slate-400 hover:text-slate-200 hover:bg-navy-700 transition-colors"
        >
          {isCollapsed ? <CaretRight size={18} /> : <CaretLeft size={18} />}
        </button>
      </div>
    </aside>
  )
}
