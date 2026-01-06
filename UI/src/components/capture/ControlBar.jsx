import { clsx } from 'clsx'
import { CameraPlus, Database, PencilSimple, Student, Chalkboard, Users } from '@phosphor-icons/react'
import { Dropdown, Button } from '../shared'

// Entity type configuration
const ENTITY_TYPES = [
  { value: 'student', label: 'Student', icon: Student, color: 'blue' },
  { value: 'teacher', label: 'Teacher', icon: Chalkboard, color: 'green' },
  { value: 'staff', label: 'Staff', icon: Users, color: 'yellow' },
]

export default function ControlBar({
  cameras,
  selectedCamera,
  onCameraChange,
  inputMode,
  onInputModeChange,
  entityType = 'student',
  onEntityTypeChange,
  selectedStudent,
  selectedTeacher,
  selectedStaff,
  manualData,
  isCapturing,
}) {
  const handleCaptureClick = () => {
    // Trigger capture from parent which has the canvas
    const event = new CustomEvent('capture-request')
    window.dispatchEvent(event)
  }

  // Get the currently selected entity based on type
  const getSelectedEntity = () => {
    if (entityType === 'student') return selectedStudent
    if (entityType === 'teacher') return selectedTeacher
    if (entityType === 'staff') return selectedStaff
    return null
  }

  // Get display text for current selection
  const getSelectionDisplay = () => {
    const entity = getSelectedEntity()
    
    if (inputMode === 'database' && entity) {
      const id = entity.student_id || entity.id_number || entity.employee_id || ''
      const name = entity.full_name || ''
      return `${id} - ${name}`
    }
    if (inputMode === 'manual' && (manualData.id_number || manualData.employee_id)) {
      return manualData.id_number || manualData.employee_id
    }
    
    const entityLabel = ENTITY_TYPES.find(e => e.value === entityType)?.label || 'Entity'
    return inputMode === 'database' 
      ? `Select ${entityLabel.toLowerCase()} from sidebar →` 
      : 'Enter details in sidebar →'
  }

  // Get badge color for entity type
  const getEntityColor = () => {
    const entity = ENTITY_TYPES.find(e => e.value === entityType)
    return entity?.color || 'blue'
  }

  return (
    <div className="card">
      <div className="p-4">
        {/* Control Row */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {/* Entity Type Selector */}
          <div>
            <label className="label">Entity Type</label>
            <div className="h-11 p-1 bg-navy-800 border border-navy-700 rounded-lg flex gap-1">
              {ENTITY_TYPES.map(({ value, label, icon: Icon, color }) => (
                <button
                  key={value}
                  onClick={() => onEntityTypeChange?.(value)}
                  className={clsx(
                    'flex-1 h-full rounded-md text-xs font-bold uppercase tracking-wide transition-all duration-200',
                    'flex items-center justify-center gap-1',
                    entityType === value
                      ? color === 'blue' ? 'bg-blue-600 text-white shadow-md' :
                        color === 'green' ? 'bg-green-600 text-white shadow-md' :
                        'bg-yellow-600 text-white shadow-md'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-navy-700'
                  )}
                  title={label}
                >
                  <Icon size={14} weight="bold" />
                  <span className="hidden lg:inline">{label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Camera Select */}
          <Dropdown
            label="Camera Source"
            value={selectedCamera}
            onChange={onCameraChange}
            options={cameras}
            placeholder="Select camera..."
          />

          {/* Input Mode Toggle */}
          <div>
            <label className="label">Data Source</label>
            <div className="h-11 p-1 bg-navy-800 border border-navy-700 rounded-full flex">
              <button
                onClick={() => onInputModeChange('database')}
                className={clsx(
                  'flex-1 h-full rounded-full text-xs font-bold uppercase tracking-wide transition-all duration-200 ease-spring',
                  'flex items-center justify-center gap-1.5',
                  inputMode === 'database'
                    ? 'bg-blue-600 text-white shadow-md scale-[1.02]'
                    : 'text-slate-400 hover:text-slate-200'
                )}
              >
                <Database size={14} weight="bold" />
                Database
              </button>
              <button
                onClick={() => onInputModeChange('manual')}
                className={clsx(
                  'flex-1 h-full rounded-full text-xs font-bold uppercase tracking-wide transition-all duration-200 ease-spring',
                  'flex items-center justify-center gap-1.5',
                  inputMode === 'manual'
                    ? 'bg-blue-600 text-white shadow-md scale-[1.02]'
                    : 'text-slate-400 hover:text-slate-200'
                )}
              >
                <PencilSimple size={14} weight="bold" />
                Manual
              </button>
            </div>
          </div>

          {/* Current Selection Display */}
          <div>
            <label className="label">Current Selection</label>
            <div className="h-11 px-4 flex items-center gap-2 bg-navy-800 border border-navy-700 rounded-lg">
              {/* Entity Type Badge */}
              <span className={clsx(
                'px-1.5 py-0.5 text-[10px] font-bold uppercase rounded',
                entityType === 'student' ? 'bg-blue-600/20 text-blue-400' :
                entityType === 'teacher' ? 'bg-green-600/20 text-green-400' :
                'bg-yellow-600/20 text-yellow-400'
              )}>
                {entityType.charAt(0)}
              </span>
              <span className={clsx(
                'text-sm truncate',
                getSelectedEntity() || (manualData.id_number || manualData.employee_id)
                  ? 'text-slate-200 font-medium'
                  : 'text-slate-500'
              )}>
                {getSelectionDisplay()}
              </span>
            </div>
          </div>

          {/* Capture Button */}
          <div className="flex items-end">
            <Button
              variant="primary"
              size="lg"
              icon={CameraPlus}
              loading={isCapturing}
              onClick={handleCaptureClick}
              className="w-full h-14 shadow-lg shadow-blue-600/30 hover:shadow-glow-blue"
            >
              {isCapturing ? 'PROCESSING...' : 'CAPTURE'}
            </Button>
          </div>
        </div>
      </div>

      {/* Keyboard Hint */}
      <div className="px-4 pb-3">
        <p className="text-xs text-slate-600 text-center">Press <kbd className="px-1.5 py-0.5 bg-navy-800 rounded text-slate-400">Space</kbd> to capture</p>
      </div>
    </div>
  )
}
