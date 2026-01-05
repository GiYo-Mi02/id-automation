import { clsx } from 'clsx'
import { CameraPlus, Database, PencilSimple } from '@phosphor-icons/react'
import { Dropdown, Button } from '../shared'

export default function ControlBar({
  cameras,
  selectedCamera,
  onCameraChange,
  inputMode,
  onInputModeChange,
  selectedStudent,
  manualData,
  isCapturing,
}) {
  const handleCaptureClick = () => {
    // Trigger capture from parent which has the canvas
    const event = new CustomEvent('capture-request')
    window.dispatchEvent(event)
  }

  // Get display text for current selection
  const getSelectionDisplay = () => {
    if (inputMode === 'database' && selectedStudent) {
      const studentId = selectedStudent.student_id || selectedStudent.id_number
      const studentName = selectedStudent.full_name || ''
      return `${studentId} - ${studentName}`
    }
    if (inputMode === 'manual' && manualData.id_number) {
      return manualData.id_number
    }
    return inputMode === 'database' ? 'Select student from sidebar →' : 'Enter details in sidebar →'
  }

  return (
    <div className="card">
      <div className="p-4">
        {/* Control Row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
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
            <label className="label">Student Data</label>
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
          <div className="md:col-span-1">
            <label className="label">Current Selection</label>
            <div className="h-11 px-4 flex items-center bg-navy-800 border border-navy-700 rounded-lg">
              <span className={clsx(
                'text-sm truncate',
                (inputMode === 'database' && selectedStudent) || (inputMode === 'manual' && manualData.id_number)
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
