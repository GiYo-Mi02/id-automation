/**
 * Enhanced Properties Panel
 * Provides comprehensive controls for layer editing including:
 * - Text alignment (left, center, right, justify)
 * - Word wrap toggle with max-width
 * - Font size, weight, color pickers
 * - Precise X/Y positioning inputs
 * - Layer visibility and lock controls
 */

import { useState, useEffect } from 'react'
import {
  Image,
  TextT,
  ArrowCounterClockwise,
  TextAlignLeft,
  TextAlignCenter,
  TextAlignRight,
  TextAlignJustify,
  TextAa,
  Eye,
  EyeSlash,
  Lock,
  LockOpen,
  Trash,
  Copy,
  CaretUp,
  CaretDown,
  ArrowsOut,
} from '@phosphor-icons/react'

// Field definitions for binding
const STUDENT_FIELDS = [
  { key: 'full_name', label: 'Full Name' },
  { key: 'id_number', label: 'ID Number' },
  { key: 'lrn', label: 'LRN' },
  { key: 'grade_level', label: 'Grade Level' },
  { key: 'section', label: 'Section' },
  { key: 'guardian_name', label: 'Guardian Name' },
  { key: 'guardian_contact', label: 'Guardian Contact' },
  { key: 'address', label: 'Address' },
  { key: 'birth_date', label: 'Birth Date' },
  { key: 'blood_type', label: 'Blood Type' },
  { key: 'emergency_contact', label: 'Emergency Contact' },
  { key: 'school_year', label: 'School Year' },
]

const TEACHER_FIELDS = [
  { key: 'full_name', label: 'Full Name' },
  { key: 'employee_id', label: 'Employee ID' },
  { key: 'department', label: 'Department' },
  { key: 'position', label: 'Position' },
  { key: 'specialization', label: 'Specialization' },
  { key: 'contact_number', label: 'Contact Number' },
  { key: 'emergency_contact_name', label: 'Emergency Contact Name' },
  { key: 'emergency_contact_number', label: 'Emergency Contact Number' },
  { key: 'address', label: 'Address' },
  { key: 'birth_date', label: 'Birth Date' },
  { key: 'blood_type', label: 'Blood Type' },
]

const SCHOOL_FIELDS = [
  { key: 'school_name', label: 'School Name' },
  { key: 'school_address', label: 'School Address' },
  { key: 'principal_name', label: 'Principal Name' },
  { key: 'school_year', label: 'School Year' },
]

const FONT_FAMILIES = [
  'Arial',
  'Times New Roman',
  'Calibri',
  'Verdana',
  'Tahoma',
  'Georgia',
  'Roboto',
]

const FONT_WEIGHTS = [
  { value: 'normal', label: 'Normal' },
  { value: '300', label: 'Light' },
  { value: '500', label: 'Medium' },
  { value: '600', label: 'Semi-Bold' },
  { value: 'bold', label: 'Bold' },
  { value: '800', label: 'Extra Bold' },
]

export default function EnhancedPropertiesPanel({
  selectedLayer,
  onLayerUpdate,
  onLayerDelete,
  onLayerDuplicate,
  onLayerMoveUp,
  onLayerMoveDown,
  templateType = 'student',
}) {
  // Get available fields based on template type
  // Deduplicate by key to prevent React duplicate key warnings
  const rawFields = templateType === 'teacher' 
    ? [...TEACHER_FIELDS, ...SCHOOL_FIELDS]
    : [...STUDENT_FIELDS, ...SCHOOL_FIELDS]
  
  const availableFields = Array.from(
    new Map(rawFields.map(field => [field.key, field])).values()
  )

  if (!selectedLayer) {
    return (
      <aside className="w-[320px] h-full bg-slate-950 border-l border-slate-800 flex flex-col shrink-0">
        <div className="px-5 py-4 border-b border-slate-800 bg-slate-900/30">
          <h3 className="text-sm font-bold text-white">Properties</h3>
          <p className="text-xs text-slate-500">Select a layer to edit</p>
        </div>
        <div className="flex-1 flex items-center justify-center">
          <p className="text-sm text-slate-600 text-center px-4">
            Click on a layer in the canvas or layers panel to edit its properties
          </p>
        </div>
      </aside>
    )
  }

  const isTextLayer = selectedLayer.type === 'text'
  const isImageLayer = selectedLayer.type === 'image'
  const isShapeLayer = selectedLayer.type === 'shape'
  const isQRLayer = selectedLayer.type === 'qr_code'

  const handleUpdate = (updates) => {
    onLayerUpdate(selectedLayer.id, updates)
  }

  return (
    <aside className="w-[320px] h-full bg-slate-950 border-l border-slate-800 flex flex-col shrink-0">
      {/* Header */}
      <div className="px-5 py-4 border-b border-slate-800 bg-slate-900/30">
        <div className="flex items-center justify-between mb-1">
          <div className="flex items-center gap-3">
            {isTextLayer && (
              <div className="p-2 bg-blue-500/10 rounded-lg">
                <TextT size={20} className="text-blue-400" weight="duotone" />
              </div>
            )}
            {isImageLayer && (
              <div className="p-2 bg-purple-500/10 rounded-lg">
                <Image size={20} className="text-purple-400" weight="duotone" />
              </div>
            )}
            <div>
              <h3 className="text-sm font-bold text-white">
                {selectedLayer.name || selectedLayer.id}
              </h3>
              <p className="text-xs text-slate-500 capitalize">{selectedLayer.type} Layer</p>
            </div>
          </div>
          
          {/* Quick Actions */}
          <div className="flex items-center gap-1">
            <button
              onClick={() => handleUpdate({ visible: !selectedLayer.visible })}
              className="p-1.5 rounded hover:bg-slate-800 transition-colors"
              title={selectedLayer.visible ? 'Hide Layer' : 'Show Layer'}
            >
              {selectedLayer.visible ? (
                <Eye size={16} className="text-slate-400" />
              ) : (
                <EyeSlash size={16} className="text-slate-600" />
              )}
            </button>
            <button
              onClick={() => handleUpdate({ locked: !selectedLayer.locked })}
              className="p-1.5 rounded hover:bg-slate-800 transition-colors"
              title={selectedLayer.locked ? 'Unlock Layer' : 'Lock Layer'}
            >
              {selectedLayer.locked ? (
                <Lock size={16} className="text-amber-400" />
              ) : (
                <LockOpen size={16} className="text-slate-400" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-5 space-y-6">
        
        {/* Position Section */}
        <section>
          <h4 className="text-xs font-bold uppercase text-slate-500 tracking-wider mb-3">
            Position
          </h4>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-slate-500 mb-1.5 block">X</label>
              <input
                type="number"
                value={Math.round(selectedLayer?.x ?? 0)}
                onChange={(e) => handleUpdate({ x: Number(e.target.value) })}
                disabled={selectedLayer?.locked}
                className="w-full h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm tabular-nums text-slate-200 focus:outline-none focus:border-blue-500 transition-colors disabled:opacity-50"
              />
            </div>
            <div>
              <label className="text-xs text-slate-500 mb-1.5 block">Y</label>
              <input
                type="number"
                value={Math.round(selectedLayer?.y ?? 0)}
                onChange={(e) => handleUpdate({ y: Number(e.target.value) })}
                disabled={selectedLayer?.locked}
                className="w-full h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm tabular-nums text-slate-200 focus:outline-none focus:border-blue-500 transition-colors disabled:opacity-50"
              />
            </div>
          </div>
        </section>

        {/* Dimensions Section */}
        <section>
          <h4 className="text-xs font-bold uppercase text-slate-500 tracking-wider mb-3">
            Dimensions
          </h4>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-slate-500 mb-1.5 block">Width</label>
              <input
                type="number"
                value={Math.round(selectedLayer?.width ?? 100)}
                onChange={(e) => handleUpdate({ width: Number(e.target.value) })}
                disabled={selectedLayer?.locked}
                className="w-full h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm tabular-nums text-slate-200 focus:outline-none focus:border-blue-500 transition-colors disabled:opacity-50"
              />
            </div>
            <div>
              <label className="text-xs text-slate-500 mb-1.5 block">Height</label>
              <input
                type="number"
                value={Math.round(selectedLayer?.height ?? 100)}
                onChange={(e) => handleUpdate({ height: Number(e.target.value) })}
                disabled={selectedLayer?.locked}
                className="w-full h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm tabular-nums text-slate-200 focus:outline-none focus:border-blue-500 transition-colors disabled:opacity-50"
              />
            </div>
          </div>
        </section>

        {/* Z-Index / Layer Order */}
        <section>
          <h4 className="text-xs font-bold uppercase text-slate-500 tracking-wider mb-3">
            Layer Order
          </h4>
          <div className="flex items-center gap-2">
            <input
              type="number"
              value={selectedLayer.zIndex || 1}
              onChange={(e) => handleUpdate({ zIndex: Number(e.target.value) })}
              disabled={selectedLayer.locked}
              min={0}
              max={100}
              className="w-20 h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm tabular-nums text-slate-200 focus:outline-none focus:border-blue-500 transition-colors disabled:opacity-50"
            />
            <button
              onClick={onLayerMoveUp}
              disabled={selectedLayer.locked}
              className="flex-1 h-9 flex items-center justify-center gap-1 bg-slate-900 border border-slate-800 rounded-lg text-sm text-slate-300 hover:bg-slate-800 disabled:opacity-50 transition-colors"
            >
              <CaretUp size={16} /> Up
            </button>
            <button
              onClick={onLayerMoveDown}
              disabled={selectedLayer.locked}
              className="flex-1 h-9 flex items-center justify-center gap-1 bg-slate-900 border border-slate-800 rounded-lg text-sm text-slate-300 hover:bg-slate-800 disabled:opacity-50 transition-colors"
            >
              <CaretDown size={16} /> Down
            </button>
          </div>
        </section>

        {/* Rotation */}
        <section>
          <h4 className="text-xs font-bold uppercase text-slate-500 tracking-wider mb-3">
            Rotation
          </h4>
          <div className="flex items-center gap-2">
            <input
              type="range"
              value={selectedLayer.rotation || 0}
              onChange={(e) => handleUpdate({ rotation: Number(e.target.value) })}
              disabled={selectedLayer.locked}
              min={0}
              max={360}
              step={1}
              className="flex-1 h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer disabled:opacity-50"
            />
            <input
              type="number"
              value={selectedLayer.rotation || 0}
              onChange={(e) => handleUpdate({ rotation: Number(e.target.value) })}
              disabled={selectedLayer.locked}
              min={0}
              max={360}
              className="w-20 h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm tabular-nums text-slate-200 focus:outline-none focus:border-blue-500 transition-colors disabled:opacity-50"
            />
            <span className="text-xs text-slate-500">°</span>
          </div>
        </section>

        {/* Text-specific controls */}
        {isTextLayer && (
          <>
            {/* Field Binding */}
            <section>
              <h4 className="text-xs font-bold uppercase text-slate-500 tracking-wider mb-3">
                Data Binding
              </h4>
              <select
                value={selectedLayer.field || 'static'}
                onChange={(e) => handleUpdate({ field: e.target.value })}
                disabled={selectedLayer.locked}
                className="w-full h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-blue-500 transition-colors disabled:opacity-50"
              >
                <option value="static">Static Text</option>
                <optgroup label="Data Fields">
                  {availableFields.map((field) => (
                    <option key={field.key} value={field.key}>
                      {field.label}
                    </option>
                  ))}
                </optgroup>
              </select>
              
              {selectedLayer.field === 'static' && (
                <div className="mt-3">
                  <label className="text-xs text-slate-500 mb-1.5 block">Text Content</label>
                  <input
                    type="text"
                    value={selectedLayer?.text ?? ''}
                    onChange={(e) => handleUpdate({ text: e.target.value })}
                    disabled={selectedLayer?.locked}
                    placeholder="Enter text..."
                    className="w-full h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-blue-500 transition-colors disabled:opacity-50"
                  />
                </div>
              )}
            </section>

            {/* Text Alignment */}
            <section>
              <h4 className="text-xs font-bold uppercase text-slate-500 tracking-wider mb-3">
                Text Alignment
              </h4>
              <div className="flex gap-1">
                {[
                  { value: 'left', icon: TextAlignLeft },
                  { value: 'center', icon: TextAlignCenter },
                  { value: 'right', icon: TextAlignRight },
                  { value: 'justify', icon: TextAlignJustify },
                ].map(({ value, icon: Icon }) => (
                  <button
                    key={value}
                    onClick={() => handleUpdate({ textAlign: value })}
                    disabled={selectedLayer.locked}
                    className={`flex-1 h-9 flex items-center justify-center rounded-lg transition-colors ${
                      selectedLayer.textAlign === value
                        ? 'bg-blue-500/20 border border-blue-500/50 text-blue-400'
                        : 'bg-slate-900 border border-slate-800 text-slate-400 hover:bg-slate-800'
                    } disabled:opacity-50`}
                  >
                    <Icon size={18} />
                  </button>
                ))}
              </div>
            </section>

            {/* Word Wrap */}
            <section>
              <h4 className="text-xs font-bold uppercase text-slate-500 tracking-wider mb-3">
                Text Wrapping
              </h4>
              <div className="flex items-center gap-3">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedLayer.wordWrap || false}
                    onChange={(e) => handleUpdate({ wordWrap: e.target.checked })}
                    disabled={selectedLayer.locked}
                    className="w-4 h-4 rounded border-slate-700 bg-slate-900 text-blue-500 focus:ring-blue-500 focus:ring-offset-slate-950"
                  />
                  <span className="text-sm text-slate-300">Enable Word Wrap</span>
                </label>
              </div>
              {selectedLayer.wordWrap && (
                <div className="mt-3">
                  <label className="text-xs text-slate-500 mb-1.5 block">Max Width</label>
                  <input
                    type="number"
                    value={selectedLayer.maxWidth || selectedLayer.width || 200}
                    onChange={(e) => handleUpdate({ maxWidth: Number(e.target.value) })}
                    disabled={selectedLayer.locked}
                    className="w-full h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm tabular-nums text-slate-200 focus:outline-none focus:border-blue-500 transition-colors disabled:opacity-50"
                  />
                </div>
              )}
            </section>

            {/* Typography */}
            <section>
              <h4 className="text-xs font-bold uppercase text-slate-500 tracking-wider mb-3">
                Typography
              </h4>
              <div className="space-y-3">
                <div>
                  <label className="text-xs text-slate-500 mb-1.5 block">Font Family</label>
                  <select
                    value={selectedLayer.fontFamily || 'Arial'}
                    onChange={(e) => handleUpdate({ fontFamily: e.target.value })}
                    disabled={selectedLayer.locked}
                    className="w-full h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-blue-500 transition-colors disabled:opacity-50"
                  >
                    {FONT_FAMILIES.map((font) => (
                      <option key={font} value={font}>{font}</option>
                    ))}
                  </select>
                </div>
                
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs text-slate-500 mb-1.5 block">Font Size</label>
                    <input
                      type="number"
                      value={selectedLayer.fontSize || 16}
                      onChange={(e) => handleUpdate({ fontSize: Number(e.target.value) })}
                      disabled={selectedLayer.locked}
                      min={8}
                      max={200}
                      className="w-full h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm tabular-nums text-slate-200 focus:outline-none focus:border-blue-500 transition-colors disabled:opacity-50"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-slate-500 mb-1.5 block">Line Height</label>
                    <input
                      type="number"
                      value={selectedLayer.lineHeight || 1.2}
                      onChange={(e) => handleUpdate({ lineHeight: Number(e.target.value) })}
                      disabled={selectedLayer.locked}
                      min={0.5}
                      max={3}
                      step={0.1}
                      className="w-full h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm tabular-nums text-slate-200 focus:outline-none focus:border-blue-500 transition-colors disabled:opacity-50"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="text-xs text-slate-500 mb-1.5 block">Font Weight</label>
                  <select
                    value={selectedLayer.fontWeight || 'normal'}
                    onChange={(e) => handleUpdate({ fontWeight: e.target.value })}
                    disabled={selectedLayer.locked}
                    className="w-full h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-blue-500 transition-colors disabled:opacity-50"
                  >
                    {FONT_WEIGHTS.map(({ value, label }) => (
                      <option key={value} value={value}>{label}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="text-xs text-slate-500 mb-1.5 block">Text Style</label>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleUpdate({ fontWeight: selectedLayer.fontWeight === 'bold' ? 'normal' : 'bold' })}
                      disabled={selectedLayer.locked}
                      className={`flex-1 h-9 rounded-lg text-sm font-bold transition-colors ${
                        selectedLayer.fontWeight === 'bold' || selectedLayer.fontWeight === '700' || selectedLayer.fontWeight === '600' || selectedLayer.fontWeight === '800'
                          ? 'bg-blue-500/20 border border-blue-500/50 text-blue-400'
                          : 'bg-slate-900 border border-slate-800 text-slate-400 hover:bg-slate-800'
                      } disabled:opacity-50`}
                    >
                      B
                    </button>
                    <button
                      onClick={() => handleUpdate({ fontStyle: selectedLayer.fontStyle === 'italic' ? 'normal' : 'italic' })}
                      disabled={selectedLayer.locked}
                      className={`flex-1 h-9 rounded-lg text-sm italic transition-colors ${
                        selectedLayer.fontStyle === 'italic'
                          ? 'bg-blue-500/20 border border-blue-500/50 text-blue-400'
                          : 'bg-slate-900 border border-slate-800 text-slate-400 hover:bg-slate-800'
                      } disabled:opacity-50`}
                    >
                      I
                    </button>
                    <button
                      onClick={() => handleUpdate({ textDecoration: selectedLayer.textDecoration === 'underline' ? 'none' : 'underline' })}
                      disabled={selectedLayer.locked}
                      className={`flex-1 h-9 rounded-lg text-sm underline transition-colors ${
                        selectedLayer.textDecoration === 'underline'
                          ? 'bg-blue-500/20 border border-blue-500/50 text-blue-400'
                          : 'bg-slate-900 border border-slate-800 text-slate-400 hover:bg-slate-800'
                      } disabled:opacity-50`}
                    >
                      U
                    </button>
                  </div>
                </div>
                
                <div>
                  <label className="text-xs text-slate-500 mb-1.5 block">Color</label>
                  <div className="flex gap-2">
                    <input
                      type="color"
                      value={selectedLayer.color || '#000000'}
                      onChange={(e) => handleUpdate({ color: e.target.value })}
                      disabled={selectedLayer.locked}
                      className="w-12 h-9 bg-slate-900 border border-slate-800 rounded-lg cursor-pointer disabled:opacity-50"
                    />
                    <input
                      type="text"
                      value={selectedLayer.color || '#000000'}
                      onChange={(e) => handleUpdate({ color: e.target.value })}
                      disabled={selectedLayer.locked}
                      className="flex-1 h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm font-mono text-slate-200 focus:outline-none focus:border-blue-500 transition-colors disabled:opacity-50"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="text-xs text-slate-500 mb-1.5 block">Letter Spacing</label>
                  <input
                    type="number"
                    value={selectedLayer.letterSpacing || 0}
                    onChange={(e) => handleUpdate({ letterSpacing: Number(e.target.value) })}
                    disabled={selectedLayer.locked}
                    step={0.5}
                    className="w-full h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm tabular-nums text-slate-200 focus:outline-none focus:border-blue-500 transition-colors disabled:opacity-50"
                  />
                </div>
              </div>
            </section>

            {/* Text Transform */}
            <section>
              <h4 className="text-xs font-bold uppercase text-slate-500 tracking-wider mb-3">
                Text Transform
              </h4>
              <div className="flex gap-2">
                <button
                  onClick={() => handleUpdate({ uppercase: !selectedLayer.uppercase, lowercase: false })}
                  disabled={selectedLayer.locked}
                  className={`flex-1 h-9 rounded-lg text-sm font-medium transition-colors ${
                    selectedLayer.uppercase
                      ? 'bg-blue-500/20 border border-blue-500/50 text-blue-400'
                      : 'bg-slate-900 border border-slate-800 text-slate-400 hover:bg-slate-800'
                  } disabled:opacity-50`}
                >
                  UPPERCASE
                </button>
                <button
                  onClick={() => handleUpdate({ lowercase: !selectedLayer.lowercase, uppercase: false })}
                  disabled={selectedLayer.locked}
                  className={`flex-1 h-9 rounded-lg text-sm font-medium transition-colors ${
                    selectedLayer.lowercase
                      ? 'bg-blue-500/20 border border-blue-500/50 text-blue-400'
                      : 'bg-slate-900 border border-slate-800 text-slate-400 hover:bg-slate-800'
                  } disabled:opacity-50`}
                >
                  lowercase
                </button>
              </div>
            </section>
          </>
        )}

        {/* Image-specific controls */}
        {isImageLayer && (
          <>
            <section>
              <h4 className="text-xs font-bold uppercase text-slate-500 tracking-wider mb-3">
                Image Source
              </h4>
              <select
                value={selectedLayer.field || ''}
                onChange={(e) => handleUpdate({ field: e.target.value || null })}
                disabled={selectedLayer.locked}
                className="w-full h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-blue-500 transition-colors disabled:opacity-50"
              >
                <option value="">Static Image</option>
                <option value="photo">Dynamic Photo</option>
                <option value="school_logo">School Logo</option>
                <option value="principal_signature">Principal Signature</option>
              </select>
            </section>

            <section>
              <h4 className="text-xs font-bold uppercase text-slate-500 tracking-wider mb-3">
                Object Fit
              </h4>
              <select
                value={selectedLayer.objectFit || 'cover'}
                onChange={(e) => handleUpdate({ objectFit: e.target.value })}
                disabled={selectedLayer.locked}
                className="w-full h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-blue-500 transition-colors disabled:opacity-50"
              >
                <option value="cover">Cover (Fill, crop if needed)</option>
                <option value="contain">Contain (Fit, may have gaps)</option>
                <option value="fill">Fill (Stretch to fit)</option>
                <option value="none">None (Original size)</option>
              </select>
            </section>

            <section>
              <h4 className="text-xs font-bold uppercase text-slate-500 tracking-wider mb-3">
                Border Radius
              </h4>
              <input
                type="number"
                value={selectedLayer.borderRadius || 0}
                onChange={(e) => handleUpdate({ borderRadius: Number(e.target.value) })}
                disabled={selectedLayer.locked}
                min={0}
                className="w-full h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm tabular-nums text-slate-200 focus:outline-none focus:border-blue-500 transition-colors disabled:opacity-50"
              />
            </section>
          </>
        )}

        {/* Shape-specific controls */}
        {isShapeLayer && (
          <>
            <section>
              <h4 className="text-xs font-bold uppercase text-slate-500 tracking-wider mb-3">
                Shape Type
              </h4>
              <select
                value={selectedLayer.shape || 'rectangle'}
                onChange={(e) => handleUpdate({ shape: e.target.value })}
                disabled={selectedLayer.locked}
                className="w-full h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-blue-500 transition-colors disabled:opacity-50"
              >
                <option value="rectangle">Rectangle</option>
                <option value="circle">Circle / Ellipse</option>
                <option value="line">Line</option>
              </select>
            </section>

            <section>
              <h4 className="text-xs font-bold uppercase text-slate-500 tracking-wider mb-3">
                Fill & Stroke
              </h4>
              <div className="space-y-3">
                <div>
                  <label className="text-xs text-slate-500 mb-1.5 block">Fill Color</label>
                  <div className="flex gap-2">
                    <input
                      type="color"
                      value={selectedLayer.fill || '#cccccc'}
                      onChange={(e) => handleUpdate({ fill: e.target.value })}
                      disabled={selectedLayer.locked}
                      className="w-12 h-9 bg-slate-900 border border-slate-800 rounded-lg cursor-pointer disabled:opacity-50"
                    />
                    <input
                      type="text"
                      value={selectedLayer.fill || '#cccccc'}
                      onChange={(e) => handleUpdate({ fill: e.target.value })}
                      disabled={selectedLayer.locked}
                      className="flex-1 h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm font-mono text-slate-200 focus:outline-none focus:border-blue-500 transition-colors disabled:opacity-50"
                    />
                  </div>
                </div>
                <div>
                  <label className="text-xs text-slate-500 mb-1.5 block">Stroke Color</label>
                  <div className="flex gap-2">
                    <input
                      type="color"
                      value={selectedLayer.stroke || '#000000'}
                      onChange={(e) => handleUpdate({ stroke: e.target.value })}
                      disabled={selectedLayer.locked}
                      className="w-12 h-9 bg-slate-900 border border-slate-800 rounded-lg cursor-pointer disabled:opacity-50"
                    />
                    <input
                      type="text"
                      value={selectedLayer.stroke || '#000000'}
                      onChange={(e) => handleUpdate({ stroke: e.target.value })}
                      disabled={selectedLayer.locked}
                      className="flex-1 h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm font-mono text-slate-200 focus:outline-none focus:border-blue-500 transition-colors disabled:opacity-50"
                    />
                  </div>
                </div>
                <div>
                  <label className="text-xs text-slate-500 mb-1.5 block">Stroke Width</label>
                  <input
                    type="number"
                    value={selectedLayer.strokeWidth || 0}
                    onChange={(e) => handleUpdate({ strokeWidth: Number(e.target.value) })}
                    disabled={selectedLayer.locked}
                    min={0}
                    className="w-full h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm tabular-nums text-slate-200 focus:outline-none focus:border-blue-500 transition-colors disabled:opacity-50"
                  />
                </div>
              </div>
            </section>
          </>
        )}

        {/* QR Code-specific controls */}
        {isQRLayer && (
          <>
            <section>
              <h4 className="text-xs font-bold uppercase text-slate-500 tracking-wider mb-3">
                QR Code Data
              </h4>
              <select
                value={selectedLayer.field || 'id_number'}
                onChange={(e) => handleUpdate({ field: e.target.value })}
                disabled={selectedLayer.locked}
                className="w-full h-9 px-3 bg-slate-900 border border-slate-800 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-blue-500 transition-colors disabled:opacity-50"
              >
                {availableFields.map((field) => (
                  <option key={field.key} value={field.key}>{field.label}</option>
                ))}
              </select>
            </section>

            <section>
              <h4 className="text-xs font-bold uppercase text-slate-500 tracking-wider mb-3">
                QR Colors
              </h4>
              <div className="space-y-3">
                <div>
                  <label className="text-xs text-slate-500 mb-1.5 block">Foreground</label>
                  <input
                    type="color"
                    value={selectedLayer.foregroundColor || '#000000'}
                    onChange={(e) => handleUpdate({ foregroundColor: e.target.value })}
                    disabled={selectedLayer.locked}
                    className="w-full h-9 bg-slate-900 border border-slate-800 rounded-lg cursor-pointer disabled:opacity-50"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-500 mb-1.5 block">Background</label>
                  <input
                    type="color"
                    value={selectedLayer.backgroundColor || '#ffffff'}
                    onChange={(e) => handleUpdate({ backgroundColor: e.target.value })}
                    disabled={selectedLayer.locked}
                    className="w-full h-9 bg-slate-900 border border-slate-800 rounded-lg cursor-pointer disabled:opacity-50"
                  />
                </div>
              </div>
            </section>
          </>
        )}

        {/* Layer Actions */}
        <section className="pt-4 border-t border-slate-800 space-y-2">
          <button
            onClick={onLayerDuplicate}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-slate-900 border border-slate-800 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:border-slate-700 transition-all duration-200"
          >
            <Copy size={16} />
            Duplicate Layer
          </button>
          <button
            onClick={onLayerDelete}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-red-500/10 border border-red-500/30 rounded-lg text-sm font-medium text-red-400 hover:bg-red-500/20 hover:border-red-500/50 transition-all duration-200"
          >
            <Trash size={16} />
            Delete Layer
          </button>
        </section>
      </div>
    </aside>
  )
}
