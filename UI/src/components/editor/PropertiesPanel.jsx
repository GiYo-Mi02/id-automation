import { clsx } from 'clsx'
import { Cursor, Image, TextT, ArrowCounterClockwise, FloppyDisk } from '@phosphor-icons/react'
import { Button, Input, Slider } from '../shared'

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

export default function PropertiesPanel({
  selectedElement,
  elementData,
  onUpdate,
  onReset,
  onSave,
  isSaving,
}) {
  const isPhoto = selectedElement === 'photo'
  const label = selectedElement ? elementLabels[selectedElement] || selectedElement : null

  return (
    <aside className="w-[280px] h-full bg-navy-900 border-l border-navy-700 flex flex-col shrink-0">
      {/* Header */}
      <div className="h-12 px-5 flex items-center border-b border-navy-700">
        <h3 className="text-xs font-bold uppercase text-slate-500 tracking-widest">
          Properties
        </h3>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-5">
        {selectedElement && elementData ? (
          <div className="space-y-6">
            {/* Element Name Badge */}
            <div className="flex items-center gap-2 px-3 py-2 bg-blue-600/20 border border-blue-500/30 rounded-lg">
              {isPhoto ? (
                <Image size={20} className="text-blue-400" />
              ) : (
                <TextT size={20} className="text-blue-400" />
              )}
              <span className="text-sm font-bold uppercase text-slate-100">{label}</span>
            </div>

            {/* Position */}
            <div>
              <h4 className="text-xs font-bold uppercase text-slate-500 mb-3">Position</h4>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-slate-600 uppercase mb-1 block">X</label>
                  <input
                    type="number"
                    value={Math.round(elementData.x || 0)}
                    onChange={(e) => onUpdate({ x: Number(e.target.value) })}
                    className="w-full h-10 px-3 bg-navy-950 border border-navy-700 rounded-md text-sm tabular-nums text-slate-200 focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-600 uppercase mb-1 block">Y</label>
                  <input
                    type="number"
                    value={Math.round(elementData.y || 0)}
                    onChange={(e) => onUpdate({ y: Number(e.target.value) })}
                    className="w-full h-10 px-3 bg-navy-950 border border-navy-700 rounded-md text-sm tabular-nums text-slate-200 focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>
            </div>

            {/* Dimensions (Photo only) */}
            {isPhoto && (
              <div>
                <h4 className="text-xs font-bold uppercase text-slate-500 mb-3">Dimensions</h4>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs text-slate-600 uppercase mb-1 block">Width</label>
                    <input
                      type="number"
                      value={Math.round(elementData.width || 200)}
                      onChange={(e) => onUpdate({ width: Number(e.target.value) })}
                      className="w-full h-10 px-3 bg-navy-950 border border-navy-700 rounded-md text-sm tabular-nums text-slate-200 focus:outline-none focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-slate-600 uppercase mb-1 block">Height</label>
                    <input
                      type="number"
                      value={Math.round(elementData.height || 250)}
                      onChange={(e) => onUpdate({ height: Number(e.target.value) })}
                      className="w-full h-10 px-3 bg-navy-950 border border-navy-700 rounded-md text-sm tabular-nums text-slate-200 focus:outline-none focus:border-blue-500"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Typography (Text fields only) */}
            {!isPhoto && (
              <div>
                <h4 className="text-xs font-bold uppercase text-slate-500 mb-3">Typography</h4>
                
                {/* Font Size */}
                <div className="mb-4">
                  <Slider
                    label="Font Size"
                    value={elementData.fontSize || 16}
                    onChange={(v) => onUpdate({ fontSize: v })}
                    min={8}
                    max={72}
                    step={1}
                  />
                </div>

                {/* Color */}
                <div className="mb-4">
                  <label className="text-xs text-slate-600 uppercase mb-2 block">Color</label>
                  <div className="flex items-center gap-3">
                    <input
                      type="color"
                      value={elementData.color || '#000000'}
                      onChange={(e) => onUpdate({ color: e.target.value })}
                      className="w-10 h-10 rounded-md border border-navy-700 cursor-pointer"
                    />
                    <input
                      type="text"
                      value={elementData.color || '#000000'}
                      onChange={(e) => onUpdate({ color: e.target.value })}
                      className="flex-1 h-10 px-3 bg-navy-950 border border-navy-700 rounded-md text-sm text-slate-200 uppercase focus:outline-none focus:border-blue-500"
                    />
                  </div>
                </div>

                {/* Font Weight */}
                <div>
                  <label className="text-xs text-slate-600 uppercase mb-2 block">Font Weight</label>
                  <div className="flex gap-2">
                    <button
                      onClick={() => onUpdate({ fontWeight: 'normal' })}
                      className={clsx(
                        'flex-1 h-9 rounded-md text-xs font-medium transition-colors',
                        elementData.fontWeight !== 'bold'
                          ? 'bg-blue-600 text-white'
                          : 'bg-navy-800 text-slate-400 hover:bg-navy-700'
                      )}
                    >
                      Normal
                    </button>
                    <button
                      onClick={() => onUpdate({ fontWeight: 'bold' })}
                      className={clsx(
                        'flex-1 h-9 rounded-md text-xs font-bold transition-colors',
                        elementData.fontWeight === 'bold'
                          ? 'bg-blue-600 text-white'
                          : 'bg-navy-800 text-slate-400 hover:bg-navy-700'
                      )}
                    >
                      Bold
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <EmptyState />
        )}
      </div>

      {/* Footer */}
      <div className="p-5 border-t border-navy-700 space-y-3">
        <Button
          variant="secondary"
          icon={ArrowCounterClockwise}
          onClick={onReset}
          disabled={!selectedElement}
          className="w-full"
        >
          Reset Position
        </Button>
        <Button
          variant="success"
          icon={FloppyDisk}
          loading={isSaving}
          onClick={onSave}
          className="w-full h-12 shadow-lg shadow-green-600/30"
        >
          SAVE LAYOUT
        </Button>
      </div>
    </aside>
  )
}

function EmptyState() {
  return (
    <div className="py-10 text-center">
      <Cursor size={48} className="mx-auto text-slate-700" weight="thin" />
      <p className="mt-4 text-sm font-medium text-slate-400">Click any element</p>
      <p className="text-xs text-slate-600">to edit properties</p>
    </div>
  )
}
