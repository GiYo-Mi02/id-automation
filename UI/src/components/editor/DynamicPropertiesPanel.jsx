import { Image, TextT, ArrowCounterClockwise } from '@phosphor-icons/react'
import { Card, Button, Input } from '../shared'

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

export default function DynamicPropertiesPanel({
  selectedElement,
  elementData,
  onUpdate,
  onReset,
}) {
  const isPhoto = selectedElement === 'photo'
  const label = selectedElement ? elementLabels[selectedElement] || selectedElement : null

  return (
    <aside className="w-[320px] h-full bg-slate-950 border-l border-slate-800 flex flex-col shrink-0">
      {selectedElement && elementData ? (
        <>
          {/* Header */}
          <div className="px-5 py-4 border-b border-slate-800 bg-slate-900/30">
            <div className="flex items-center gap-3 mb-1">
              {isPhoto ? (
                <div className="p-2 bg-purple-500/10 rounded-lg">
                  <Image size={20} className="text-purple-400" weight="duotone" />
                </div>
              ) : (
                <div className="p-2 bg-blue-500/10 rounded-lg">
                  <TextT size={20} className="text-blue-400" weight="duotone" />
                </div>
              )}
              <div>
                <h3 className="text-sm font-bold text-white">{label}</h3>
                <p className="text-xs text-slate-500">Element Properties</p>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-5 space-y-6">
            {/* Position */}
            <div>
              <h4 className="text-xs font-bold uppercase text-slate-500 tracking-wider mb-3">Position</h4>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-slate-500 mb-1.5 block">X Axis</label>
                  <input
                    type="number"
                    value={Math.round(elementData.x || 0)}
                    onChange={(e) => onUpdate({ x: Number(e.target.value) })}
                    className="w-full h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm tabular-nums text-slate-200 focus:outline-none focus:border-blue-500 transition-colors"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-500 mb-1.5 block">Y Axis</label>
                  <input
                    type="number"
                    value={Math.round(elementData.y || 0)}
                    onChange={(e) => onUpdate({ y: Number(e.target.value) })}
                    className="w-full h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm tabular-nums text-slate-200 focus:outline-none focus:border-blue-500 transition-colors"
                  />
                </div>
              </div>
            </div>

            {/* Dimensions (Photo only) */}
            {isPhoto && (
              <div>
                <h4 className="text-xs font-bold uppercase text-slate-500 tracking-wider mb-3">Dimensions</h4>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs text-slate-500 mb-1.5 block">Width</label>
                    <input
                      type="number"
                      value={Math.round(elementData.width || 200)}
                      onChange={(e) => onUpdate({ width: Number(e.target.value) })}
                      className="w-full h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm tabular-nums text-slate-200 focus:outline-none focus:border-blue-500 transition-colors"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-slate-500 mb-1.5 block">Height</label>
                    <input
                      type="number"
                      value={Math.round(elementData.height || 250)}
                      onChange={(e) => onUpdate({ height: Number(e.target.value) })}
                      className="w-full h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm tabular-nums text-slate-200 focus:outline-none focus:border-blue-500 transition-colors"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Typography (Text only) */}
            {!isPhoto && (
              <>
                <div>
                  <h4 className="text-xs font-bold uppercase text-slate-500 tracking-wider mb-3">Typography</h4>
                  <div className="space-y-3">
                    <div>
                      <label className="text-xs text-slate-500 mb-1.5 block">Font Size</label>
                      <input
                        type="number"
                        value={elementData.fontSize || 16}
                        onChange={(e) => onUpdate({ fontSize: Number(e.target.value) })}
                        className="w-full h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm tabular-nums text-slate-200 focus:outline-none focus:border-blue-500 transition-colors"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-slate-500 mb-1.5 block">Font Weight</label>
                      <select
                        value={elementData.fontWeight || 'normal'}
                        onChange={(e) => onUpdate({ fontWeight: e.target.value })}
                        className="w-full h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-blue-500 transition-colors"
                      >
                        <option value="normal">Normal</option>
                        <option value="bold">Bold</option>
                        <option value="600">Semi-Bold</option>
                        <option value="300">Light</option>
                      </select>
                    </div>
                    <div>
                      <label className="text-xs text-slate-500 mb-1.5 block">Color</label>
                      <div className="flex gap-2">
                        <input
                          type="color"
                          value={elementData.color || '#000000'}
                          onChange={(e) => onUpdate({ color: e.target.value })}
                          className="w-12 h-9 bg-slate-900 border border-slate-800 rounded-lg cursor-pointer"
                        />
                        <input
                          type="text"
                          value={elementData.color || '#000000'}
                          onChange={(e) => onUpdate({ color: e.target.value })}
                          className="flex-1 h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm font-mono text-slate-200 focus:outline-none focus:border-blue-500 transition-colors"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </>
            )}

            {/* Reset Button */}
            <button
              onClick={onReset}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-slate-900 border border-slate-800 rounded-lg text-sm font-medium text-slate-400 hover:text-white hover:border-slate-700 transition-all duration-200"
            >
              <ArrowCounterClockwise size={16} />
              Reset to Default
            </button>
          </div>
        </>
      ) : (
        // Global Settings (Nothing Selected)
        <>
          <div className="px-5 py-4 border-b border-slate-800 bg-slate-900/30">
            <h3 className="text-sm font-bold text-white">Global Settings</h3>
            <p className="text-xs text-slate-500">Card configuration</p>
          </div>

          <div className="flex-1 overflow-y-auto p-5 space-y-6">
            <div>
              <h4 className="text-xs font-bold uppercase text-slate-500 tracking-wider mb-3">Card Size</h4>
              <div className="space-y-2">
                <button className="w-full px-4 py-3 bg-blue-500/10 border border-blue-500/50 rounded-lg text-left hover:bg-blue-500/20 transition-colors">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-white">CR80 Standard</p>
                      <p className="text-xs text-slate-500">85.6 × 53.98 mm</p>
                    </div>
                    <div className="w-2 h-2 rounded-full bg-blue-400" />
                  </div>
                </button>
                <button className="w-full px-4 py-3 bg-slate-900 border border-slate-800 rounded-lg text-left hover:bg-slate-800 transition-colors">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-slate-300">Custom Size</p>
                      <p className="text-xs text-slate-500">Define dimensions</p>
                    </div>
                  </div>
                </button>
              </div>
            </div>

            <div>
              <h4 className="text-xs font-bold uppercase text-slate-500 tracking-wider mb-3">Orientation</h4>
              <div className="grid grid-cols-2 gap-2">
                <button className="px-4 py-3 bg-blue-500/10 border border-blue-500/50 rounded-lg text-sm font-medium text-white hover:bg-blue-500/20 transition-colors">
                  Portrait
                </button>
                <button className="px-4 py-3 bg-slate-900 border border-slate-800 rounded-lg text-sm font-medium text-slate-300 hover:bg-slate-800 transition-colors">
                  Landscape
                </button>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-800">
              <p className="text-xs text-slate-600 leading-relaxed">
                Select an element on the canvas to edit its properties, or configure global card settings here.
              </p>
            </div>
          </div>
        </>
      )}
    </aside>
  )
}
