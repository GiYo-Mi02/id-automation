import { useState, useEffect } from 'react'
import { useSettings } from '../contexts/SettingsContext'
import { useWebSocket } from '../contexts/WebSocketContext'
import { useToast } from '../contexts/ToastContext'
import { api } from '../services/api'
import {
  Sliders,
  FloppyDisk,
  Gear,
  Camera,
  Database,
  HardDrives,
  CheckCircle,
  Clock,
  Trash,
  ChartBar,
  Spinner as SpinnerIcon,
  ArrowsClockwise,
  Chalkboard,
  UserCircle,
} from '@phosphor-icons/react'
import { Button, Toggle, Slider, Card, Spinner } from '../components/shared'
import ImportDataSection from '../components/settings/ImportDataSection'
import { clsx } from 'clsx'

const TABS = [
  { id: 'general', label: 'General', icon: Gear },
  { id: 'camera', label: 'Camera', icon: Camera },
  { id: 'database', label: 'Database', icon: Database },
  { id: 'storage', label: 'Storage', icon: HardDrives },
]

export default function SettingsPage() {
  const { settings, updateSettings, loading } = useSettings()
  const { status } = useWebSocket()
  const toast = useToast()

  const [activeTab, setActiveTab] = useState('general')
  const [localSettings, setLocalSettings] = useState(settings)
  const [isSaving, setIsSaving] = useState(false)
  const [cameras, setCameras] = useState([])
  const [selectedCamera, setSelectedCamera] = useState(null)
  const [loadingCameras, setLoadingCameras] = useState(false)
  const [systemStats, setSystemStats] = useState({
    storageUsed: 2.4,
    storageTotal: 3.5,
    pendingJobs: 0,
    completedJobs: 247,
    lastSync: new Date(),
  })

  useEffect(() => {
    setLocalSettings(settings)
  }, [settings])

  useEffect(() => {
    fetchSystemStats()
    fetchCameras()
  }, [])

  const fetchSystemStats = async () => {
    try {
      const data = await api.get('/api/system/stats')
      setSystemStats(data)
    } catch (err) {
      console.error('Failed to fetch system stats:', err)
    }
  }

  const fetchCameras = async () => {
    setLoadingCameras(true)
    try {
      const devices = await navigator.mediaDevices.enumerateDevices()
      const videoDevices = devices.filter(device => device.kind === 'videoinput')
      setCameras(videoDevices)
      if (videoDevices.length > 0 && !selectedCamera) {
        setSelectedCamera(videoDevices[0].deviceId)
      }
    } catch (err) {
      console.error('Failed to fetch cameras:', err)
      toast.error('Camera Error', 'Could not access camera devices')
    } finally {
      setLoadingCameras(false)
    }
  }

  const handleSettingChange = (key, value) => {
    setLocalSettings(prev => ({ ...prev, [key]: value }))
  }

  const handleSave = async () => {
    setIsSaving(true)
    const success = await updateSettings(localSettings)
    setIsSaving(false)
    
    if (success) {
      toast.success('Settings Saved', 'Your preferences have been updated')
    } else {
      toast.error('Save Failed', 'Could not save settings')
    }
  }

  const storagePercent = Math.round((systemStats.storageUsed / systemStats.storageTotal) * 100)

  return (
    <div className="flex h-full bg-slate-950">
      {/* Sidebar */}
      <div className="w-64 border-r border-slate-800 flex flex-col">
        <div className="p-6 border-b border-slate-800">
          <div className="flex items-center gap-2 text-slate-400 mb-1">
            <Sliders size={16} weight="duotone" />
            <span className="text-xs font-bold uppercase tracking-wider">Configuration</span>
          </div>
          <h1 className="text-2xl font-bold text-white">Settings</h1>
        </div>

        <nav className="flex-1 p-4">
          <div className="space-y-1">
            {TABS.map(tab => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={clsx(
                    "w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-all",
                    activeTab === tab.id
                      ? "bg-blue-500/10 text-blue-400 border border-blue-500/50"
                      : "text-slate-400 hover:text-white hover:bg-slate-900"
                  )}
                >
                  <Icon size={20} weight="duotone" />
                  <span className="text-sm font-medium">{tab.label}</span>
                </button>
              )
            })}
          </div>
        </nav>

        <div className="p-4 border-t border-slate-800">
          <Button
            onClick={handleSave}
            loading={isSaving}
            icon={FloppyDisk}
            className="w-full"
          >
            Save Changes
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto p-8">
          {activeTab === 'general' && (
            <GeneralSettings 
              settings={localSettings}
              onChange={handleSettingChange}
            />
          )}
          {activeTab === 'camera' && (
            <CameraSettings 
              settings={localSettings}
              onChange={handleSettingChange}
              cameras={cameras}
              selectedCamera={selectedCamera}
              onCameraChange={setSelectedCamera}
              loadingCameras={loadingCameras}
              onRefresh={fetchCameras}
            />
          )}
          {activeTab === 'database' && (
            <DatabaseSettings stats={systemStats} />
          )}
          {activeTab === 'storage' && (
            <StorageSettings stats={systemStats} storagePercent={storagePercent} />
          )}
        </div>
      </div>
    </div>
  )
}

// General Settings Section
function GeneralSettings({ settings, onChange }) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white mb-1">General Settings</h2>
        <p className="text-sm text-slate-500">Configure system-wide preferences</p>
      </div>

      <Card className="p-6">
        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-4">Import Data</h3>
        <ImportDataSection onImportComplete={(count) => {
          console.log(`Imported ${count} students`)
        }} />
      </Card>

      <Card className="p-6">
        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-4">Processing</h3>
        <div className="space-y-4">
          <SettingToggle
            label="Auto-Enhance Photos"
            description="Automatically improve photo quality using AI"
            checked={settings.autoEnhance !== false}
            onChange={(v) => onChange('autoEnhance', v)}
          />
          <SettingToggle
            label="Background Removal"
            description="Remove backgrounds from ID photos"
            checked={settings.removeBackground || false}
            onChange={(v) => onChange('removeBackground', v)}
          />
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-4">Quality</h3>
        <SettingSlider
          label="Image Quality"
          description="Higher quality = larger file sizes"
          value={settings.imageQuality || 85}
          onChange={(v) => onChange('imageQuality', v)}
          min={50}
          max={100}
          suffix="%"
        />
      </Card>
    </div>
  )
}

// Camera Settings Section
function CameraSettings({ settings, onChange, cameras, selectedCamera, onCameraChange, loadingCameras, onRefresh }) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white mb-1">Camera Settings</h2>
        <p className="text-sm text-slate-500">Configure capture and camera options</p>
      </div>

      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider">Available Cameras</h3>
          <button
            onClick={onRefresh}
            className="px-3 py-1.5 text-xs bg-slate-900 border border-slate-800 rounded-lg text-slate-400 hover:text-white hover:border-slate-700 transition-colors"
          >
            Refresh
          </button>
        </div>
        
        {loadingCameras ? (
          <div className="py-8 text-center text-slate-500">
            <Spinner className="mx-auto mb-2" />
            <p className="text-sm">Detecting cameras...</p>
          </div>
        ) : cameras.length === 0 ? (
          <div className="py-8 text-center">
            <Camera size={48} className="mx-auto text-slate-700 mb-3" weight="thin" />
            <p className="text-sm text-slate-500 mb-2">No cameras detected</p>
            <p className="text-xs text-slate-600">Please connect a camera and refresh</p>
          </div>
        ) : (
          <div className="space-y-2">
            {cameras.map((camera, index) => (
              <button
                key={camera.deviceId}
                onClick={() => onCameraChange(camera.deviceId)}
                className={`w-full p-4 rounded-lg border text-left transition-all ${
                  selectedCamera === camera.deviceId
                    ? 'bg-blue-500/10 border-blue-500/50'
                    : 'bg-slate-900 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${
                    selectedCamera === camera.deviceId ? 'bg-blue-500/20' : 'bg-slate-800'
                  }`}>
                    <Camera size={20} className={
                      selectedCamera === camera.deviceId ? 'text-blue-400' : 'text-slate-500'
                    } weight="duotone" />
                  </div>
                  <div className="flex-1">
                    <p className={`text-sm font-medium ${
                      selectedCamera === camera.deviceId ? 'text-blue-400' : 'text-slate-300'
                    }`}>
                      {camera.label || `Camera ${index + 1}`}
                    </p>
                    <p className="text-xs text-slate-500 font-mono mt-0.5">
                      {camera.deviceId.substring(0, 32)}...
                    </p>
                  </div>
                  {selectedCamera === camera.deviceId && (
                    <CheckCircle size={20} className="text-blue-400" weight="fill" />
                  )}
                </div>
              </button>
            ))}
          </div>
        )}
      </Card>

      <Card className="p-6">
        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-4">Camera Settings</h3>
        <div className="space-y-4">
          <SettingToggle
            label="Auto-Focus"
            description="Automatically adjust focus for sharper images"
            checked={settings.autoFocus !== false}
            onChange={(v) => onChange('autoFocus', v)}
          />
          <SettingToggle
            label="Flash"
            description="Use flash for better lighting"
            checked={settings.useFlash || false}
            onChange={(v) => onChange('useFlash', v)}
          />
        </div>
      </Card>
    </div>
  )
}

// Database Settings Section
function DatabaseSettings({ stats }) {
  const toast = useToast()
  const [showClearModal, setShowClearModal] = useState(false)
  const [clearStep, setClearStep] = useState(1)
  const [clearType, setClearType] = useState(null)
  const [confirmText, setConfirmText] = useState('')
  const [isClearing, setIsClearing] = useState(false)
  const [dbStatus, setDbStatus] = useState(null)

  // Fetch database status
  useEffect(() => {
    fetchDbStatus()
  }, [])

  const fetchDbStatus = async () => {
    try {
      const data = await api.get('/api/system/database/status')
      setDbStatus(data)
    } catch (err) {
      console.error('Failed to fetch database status:', err)
    }
  }

  const CLEAR_OPTIONS = [
    { 
      id: 'students', 
      label: 'Clear Students Only', 
      description: 'Remove all student records and their generated IDs',
      confirmText: 'DELETE STUDENTS',
      danger: 'high',
    },
    { 
      id: 'teachers', 
      label: 'Clear Teachers Only', 
      description: 'Remove all teacher records and their generated IDs',
      confirmText: 'DELETE TEACHERS',
      danger: 'high',
    },
    { 
      id: 'staff', 
      label: 'Clear Staff Only', 
      description: 'Remove all staff records and their generated IDs',
      confirmText: 'DELETE STAFF',
      danger: 'high',
    },
    { 
      id: 'history', 
      label: 'Clear History Only', 
      description: 'Remove all capture history, keep student/teacher data',
      confirmText: 'DELETE HISTORY',
      danger: 'medium',
    },
    { 
      id: 'all', 
      label: 'Full System Reset', 
      description: 'WARNING: Removes ALL data including students, teachers, staff, history, and generated IDs',
      confirmText: 'RESET SYSTEM',
      danger: 'critical',
    },
  ]

  const selectedOption = CLEAR_OPTIONS.find(o => o.id === clearType)
  const isConfirmValid = confirmText === selectedOption?.confirmText

  const handleStartClear = (type) => {
    setClearType(type)
    setClearStep(1)
    setConfirmText('')
    setShowClearModal(true)
  }

  const handleNextStep = () => {
    if (clearStep < 3) {
      setClearStep(clearStep + 1)
    }
  }

  const handleClear = async () => {
    if (!isConfirmValid) return
    
    setIsClearing(true)
    try {
      await api.post('/api/system/database/clear', {
        clear_type: clearType,
        confirm_text: confirmText,
      })
      
      toast.success('Data Cleared', `Successfully cleared ${clearType} data`)
      setShowClearModal(false)
      setClearStep(1)
      setConfirmText('')
      fetchDbStatus()
    } catch (err) {
      console.error('Clear failed:', err)
      toast.error('Clear Failed', err.message || 'Could not clear data')
    } finally {
      setIsClearing(false)
    }
  }

  const handleCloseModal = () => {
    setShowClearModal(false)
    setClearStep(1)
    setConfirmText('')
    setClearType(null)
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white mb-1">Database Settings</h2>
        <p className="text-sm text-slate-500">Manage data and backups</p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-2 gap-4">
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <ChartBar size={20} className="text-blue-400" weight="duotone" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white tabular-nums">{dbStatus?.total_students || stats.completedJobs || 0}</p>
              <p className="text-xs text-slate-500">Students</p>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-500/20 rounded-lg">
              <Chalkboard size={20} className="text-green-400" weight="duotone" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white tabular-nums">{dbStatus?.total_teachers || 0}</p>
              <p className="text-xs text-slate-500">Teachers</p>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-500/20 rounded-lg">
              <UserCircle size={20} className="text-yellow-400" weight="duotone" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white tabular-nums">{dbStatus?.total_staff || 0}</p>
              <p className="text-xs text-slate-500">Staff</p>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-amber-500/20 rounded-lg">
              <Clock size={20} className="text-amber-400" weight="duotone" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white tabular-nums">{dbStatus?.total_history || stats.pendingJobs || 0}</p>
              <p className="text-xs text-slate-500">History Records</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Database Actions */}
      <Card className="p-6">
        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-4">Database Actions</h3>
        <div className="space-y-3">
          {CLEAR_OPTIONS.map((option) => (
            <button
              key={option.id}
              onClick={() => handleStartClear(option.id)}
              className={clsx(
                'w-full flex items-center gap-4 p-4 rounded-lg border text-left transition-all',
                option.danger === 'critical' 
                  ? 'border-red-700 bg-red-950/30 hover:bg-red-950/50 hover:border-red-600' 
                  : option.danger === 'high'
                  ? 'border-orange-700/50 bg-orange-950/20 hover:bg-orange-950/40 hover:border-orange-600'
                  : 'border-slate-700 bg-slate-900 hover:bg-slate-800 hover:border-slate-600'
              )}
            >
              <div className={clsx(
                'p-2 rounded-lg',
                option.danger === 'critical' ? 'bg-red-500/20' :
                option.danger === 'high' ? 'bg-orange-500/20' :
                'bg-slate-800'
              )}>
                <Trash size={20} className={clsx(
                  option.danger === 'critical' ? 'text-red-400' :
                  option.danger === 'high' ? 'text-orange-400' :
                  'text-slate-400'
                )} weight="duotone" />
              </div>
              <div className="flex-1">
                <p className={clsx(
                  'text-sm font-medium',
                  option.danger === 'critical' ? 'text-red-400' :
                  option.danger === 'high' ? 'text-orange-300' :
                  'text-slate-300'
                )}>{option.label}</p>
                <p className="text-xs text-slate-500 mt-0.5">{option.description}</p>
              </div>
            </button>
          ))}
        </div>
      </Card>

      {/* Clear Confirmation Modal */}
      {showClearModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 rounded-xl border border-slate-700 w-full max-w-md shadow-2xl">
            {/* Modal Header */}
            <div className={clsx(
              'px-6 py-4 border-b rounded-t-xl',
              selectedOption?.danger === 'critical' ? 'border-red-700 bg-red-950/50' :
              selectedOption?.danger === 'high' ? 'border-orange-700 bg-orange-950/50' :
              'border-slate-700'
            )}>
              <h3 className="text-lg font-bold text-white">
                {clearStep === 1 ? '⚠️ Warning' : clearStep === 2 ? '🛑 Confirm Action' : '🔐 Final Confirmation'}
              </h3>
              <p className="text-sm text-slate-400 mt-1">
                Step {clearStep} of 3
              </p>
            </div>

            {/* Modal Content */}
            <div className="p-6">
              {clearStep === 1 && (
                <div className="space-y-4">
                  <p className="text-slate-300">
                    You are about to <span className="font-bold text-red-400">{selectedOption?.label.toLowerCase()}</span>.
                  </p>
                  <div className="p-4 bg-red-950/30 border border-red-700/50 rounded-lg">
                    <p className="text-sm text-red-300">
                      {selectedOption?.description}
                    </p>
                  </div>
                  <p className="text-sm text-slate-400">
                    This action <span className="font-bold text-white">cannot be undone</span>. 
                    Please ensure you have backed up any important data.
                  </p>
                </div>
              )}

              {clearStep === 2 && (
                <div className="space-y-4">
                  <p className="text-slate-300">
                    Are you absolutely sure you want to proceed? This will permanently delete:
                  </p>
                  <ul className="list-disc list-inside text-sm text-slate-400 space-y-1">
                    {clearType === 'all' && (
                      <>
                        <li>All student records</li>
                        <li>All teacher records</li>
                        <li>All staff records</li>
                        <li>All capture history</li>
                        <li>All generated ID images</li>
                      </>
                    )}
                    {clearType === 'students' && (
                      <>
                        <li>All student records</li>
                        <li>Student capture history</li>
                        <li>Student ID images</li>
                      </>
                    )}
                    {clearType === 'teachers' && (
                      <>
                        <li>All teacher records</li>
                        <li>Teacher capture history</li>
                        <li>Teacher ID images</li>
                      </>
                    )}
                    {clearType === 'staff' && (
                      <>
                        <li>All staff records</li>
                        <li>Staff capture history</li>
                        <li>Staff ID images</li>
                      </>
                    )}
                    {clearType === 'history' && (
                      <>
                        <li>All capture history records</li>
                        <li>All generated ID images</li>
                      </>
                    )}
                  </ul>
                </div>
              )}

              {clearStep === 3 && (
                <div className="space-y-4">
                  <p className="text-slate-300">
                    To confirm, type <span className="font-mono bg-slate-800 px-2 py-1 rounded text-red-400">{selectedOption?.confirmText}</span> below:
                  </p>
                  <input
                    type="text"
                    value={confirmText}
                    onChange={(e) => setConfirmText(e.target.value.toUpperCase())}
                    placeholder={selectedOption?.confirmText}
                    className={clsx(
                      'w-full px-4 py-3 bg-slate-800 border rounded-lg text-center font-mono text-lg transition-colors',
                      isConfirmValid 
                        ? 'border-green-500 text-green-400' 
                        : 'border-slate-600 text-slate-300 focus:border-red-500'
                    )}
                    autoFocus
                  />
                  {confirmText && !isConfirmValid && (
                    <p className="text-xs text-red-400 text-center">
                      Text does not match. Please type exactly: {selectedOption?.confirmText}
                    </p>
                  )}
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-4 border-t border-slate-700 flex gap-3">
              <button
                onClick={handleCloseModal}
                className="flex-1 px-4 py-2.5 text-sm font-medium text-slate-300 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
              >
                Cancel
              </button>
              
              {clearStep < 3 ? (
                <button
                  onClick={handleNextStep}
                  className="flex-1 px-4 py-2.5 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
                >
                  I Understand, Continue
                </button>
              ) : (
                <button
                  onClick={handleClear}
                  disabled={!isConfirmValid || isClearing}
                  className={clsx(
                    'flex-1 px-4 py-2.5 text-sm font-medium rounded-lg transition-colors flex items-center justify-center gap-2',
                    isConfirmValid 
                      ? 'bg-red-600 hover:bg-red-700 text-white' 
                      : 'bg-slate-700 text-slate-500 cursor-not-allowed'
                  )}
                >
                  {isClearing ? (
                    <>
                      <SpinnerIcon size={16} className="animate-spin" />
                      Clearing...
                    </>
                  ) : (
                    <>
                      <Trash size={16} weight="bold" />
                      Clear Data
                    </>
                  )}
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// Storage Settings Section
function StorageSettings({ stats, storagePercent }) {
  const toast = useToast()
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [storageAnalysis, setStorageAnalysis] = useState(null)
  const [isCleaning, setIsCleaning] = useState(false)
  const [showCleanupConfirm, setShowCleanupConfirm] = useState(false)

  const handleRefreshStorage = async () => {
    setIsRefreshing(true)
    try {
      const data = await api.get('/api/system/stats')
      // Stats will be updated via parent component
    } catch (err) {
      console.error('Failed to refresh storage:', err)
    } finally {
      setIsRefreshing(false)
    }
  }

  const handleAnalyzeStorage = async () => {
    setIsAnalyzing(true)
    try {
      const data = await api.get('/api/system/storage/analyze')
      setStorageAnalysis(data)
      
      if (data.orphaned_files?.length > 0) {
        toast.warning('Orphaned Files Found', `${data.orphaned_files.length} files not linked to any records`)
      } else {
        toast.success('Storage Clean', 'No orphaned files found')
      }
    } catch (err) {
      console.error('Failed to analyze storage:', err)
      toast.error('Analysis Failed', 'Could not analyze storage')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleCleanupOrphans = async () => {
    if (!storageAnalysis?.orphaned_files?.length) return
    
    setIsCleaning(true)
    try {
      const result = await api.post('/api/system/storage/cleanup', {
        files: storageAnalysis.orphaned_files.map(f => f.path),
      })
      
      toast.success('Cleanup Complete', `Removed ${result.deleted_count} orphaned files`)
      setStorageAnalysis(null)
      setShowCleanupConfirm(false)
      handleRefreshStorage()
    } catch (err) {
      console.error('Cleanup failed:', err)
      toast.error('Cleanup Failed', 'Could not remove orphaned files')
    } finally {
      setIsCleaning(false)
    }
  }

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white mb-1">Storage Settings</h2>
        <p className="text-sm text-slate-500">Monitor disk usage and manage files</p>
      </div>

      {/* Storage Usage */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider">Storage Usage</h3>
          <button
            onClick={handleRefreshStorage}
            disabled={isRefreshing}
            className="p-1.5 rounded text-slate-400 hover:text-white hover:bg-slate-800 transition-colors disabled:opacity-50"
            title="Refresh Storage"
          >
            <ArrowsClockwise size={16} className={isRefreshing ? 'animate-spin' : ''} />
          </button>
        </div>
        
        {/* Visual Progress Bar */}
        <div className="mb-4">
          <div className="flex items-end justify-between mb-2">
            <span className="text-3xl font-bold text-white tabular-nums">{storagePercent}%</span>
            <span className="text-sm text-slate-500 tabular-nums">
              {stats.storageUsed} GB / {stats.storageTotal} GB
            </span>
          </div>
          <div className="h-3 bg-slate-900 rounded-full overflow-hidden">
            <div
              className={clsx(
                "h-full rounded-full transition-all duration-500",
                storagePercent > 80 ? 'bg-gradient-to-r from-red-600 to-red-500' :
                storagePercent > 60 ? 'bg-gradient-to-r from-amber-600 to-amber-500' :
                'bg-gradient-to-r from-blue-600 to-blue-500'
              )}
              style={{ width: `${storagePercent}%` }}
            />
          </div>
        </div>

        {/* Status Badge */}
        {storagePercent > 80 && (
          <div className="p-3 bg-red-500/10 border border-red-500/50 rounded-lg">
            <p className="text-sm text-red-400">⚠️ Storage space is running low. Consider clearing old files.</p>
          </div>
        )}
      </Card>

      {/* Storage Analyzer */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider">Storage Analyzer</h3>
            <p className="text-xs text-slate-500 mt-1">Find and clean up orphaned files</p>
          </div>
          <button
            onClick={handleAnalyzeStorage}
            disabled={isAnalyzing}
            className={clsx(
              'px-4 py-2 text-sm font-medium rounded-lg transition-colors flex items-center gap-2',
              isAnalyzing
                ? 'bg-slate-700 text-slate-400 cursor-wait'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            )}
          >
            {isAnalyzing ? (
              <>
                <SpinnerIcon size={16} className="animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <HardDrives size={16} weight="duotone" />
                Analyze Storage
              </>
            )}
          </button>
        </div>

        {/* Analysis Results */}
        {storageAnalysis && (
          <div className="space-y-4">
            {/* Summary Stats */}
            <div className="grid grid-cols-3 gap-3">
              <div className="p-3 bg-slate-800 rounded-lg text-center">
                <p className="text-lg font-bold text-white">{storageAnalysis.total_files || 0}</p>
                <p className="text-xs text-slate-500">Total Files</p>
              </div>
              <div className="p-3 bg-slate-800 rounded-lg text-center">
                <p className="text-lg font-bold text-green-400">{storageAnalysis.linked_files || 0}</p>
                <p className="text-xs text-slate-500">Linked</p>
              </div>
              <div className="p-3 bg-slate-800 rounded-lg text-center">
                <p className={clsx(
                  'text-lg font-bold',
                  (storageAnalysis.orphaned_files?.length || 0) > 0 ? 'text-amber-400' : 'text-slate-400'
                )}>{storageAnalysis.orphaned_files?.length || 0}</p>
                <p className="text-xs text-slate-500">Orphaned</p>
              </div>
            </div>

            {/* Orphaned Files List */}
            {storageAnalysis.orphaned_files?.length > 0 && (
              <div className="border border-amber-700/50 rounded-lg overflow-hidden">
                <div className="bg-amber-950/30 px-4 py-3 border-b border-amber-700/50 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-amber-400">⚠️</span>
                    <span className="text-sm font-medium text-amber-300">
                      {storageAnalysis.orphaned_files.length} Orphaned Files
                    </span>
                    <span className="text-xs text-slate-500">
                      ({formatBytes(storageAnalysis.orphaned_total_size || 0)})
                    </span>
                  </div>
                  <button
                    onClick={() => setShowCleanupConfirm(true)}
                    className="px-3 py-1.5 text-xs font-medium bg-red-600 hover:bg-red-700 text-white rounded transition-colors flex items-center gap-1.5"
                  >
                    <Trash size={12} weight="bold" />
                    Clean Up
                  </button>
                </div>
                
                <div className="max-h-48 overflow-y-auto">
                  {storageAnalysis.orphaned_files.slice(0, 10).map((file, index) => (
                    <div key={index} className="px-4 py-2 border-b border-slate-800 last:border-0 flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-slate-300 font-mono truncate">{file.name || file.path}</p>
                        <p className="text-xs text-slate-500">{file.modified || 'Unknown date'}</p>
                      </div>
                      <span className="text-xs text-slate-400 tabular-nums">{formatBytes(file.size || 0)}</span>
                    </div>
                  ))}
                  {storageAnalysis.orphaned_files.length > 10 && (
                    <div className="px-4 py-2 text-center text-xs text-slate-500">
                      ...and {storageAnalysis.orphaned_files.length - 10} more files
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* No Orphans Message */}
            {storageAnalysis.orphaned_files?.length === 0 && (
              <div className="p-4 bg-green-950/30 border border-green-700/50 rounded-lg flex items-center gap-3">
                <CheckCircle size={24} className="text-green-400" weight="fill" />
                <div>
                  <p className="text-sm font-medium text-green-300">Storage is clean!</p>
                  <p className="text-xs text-slate-500">No orphaned files found</p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Empty State */}
        {!storageAnalysis && !isAnalyzing && (
          <div className="py-8 text-center">
            <HardDrives size={48} className="mx-auto text-slate-700 mb-3" weight="thin" />
            <p className="text-sm text-slate-500">Click "Analyze Storage" to scan for orphaned files</p>
          </div>
        )}
      </Card>

      {/* Storage Breakdown */}
      <Card className="p-6">
        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-4">Storage Breakdown</h3>
        <div className="space-y-3">
          <StorageItem label="Generated IDs" size={stats.storageUsed * 0.6} color="text-blue-400" />
          <StorageItem label="Templates" size={stats.storageUsed * 0.2} color="text-purple-400" />
          <StorageItem label="Database" size={stats.storageUsed * 0.15} color="text-green-400" />
          <StorageItem label="Other" size={stats.storageUsed * 0.05} color="text-slate-400" />
        </div>
      </Card>

      {/* Cleanup Confirmation Modal */}
      {showCleanupConfirm && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 rounded-xl border border-slate-700 w-full max-w-sm shadow-2xl">
            <div className="px-6 py-4 border-b border-red-700 bg-red-950/50 rounded-t-xl">
              <h3 className="text-lg font-bold text-white">⚠️ Confirm Cleanup</h3>
            </div>
            <div className="p-6">
              <p className="text-slate-300 mb-4">
                This will permanently delete <span className="font-bold text-red-400">{storageAnalysis?.orphaned_files?.length} orphaned files</span>.
              </p>
              <p className="text-sm text-slate-500">
                These files are not linked to any student, teacher, or staff records.
              </p>
            </div>
            <div className="px-6 py-4 border-t border-slate-700 flex gap-3">
              <button
                onClick={() => setShowCleanupConfirm(false)}
                className="flex-1 px-4 py-2.5 text-sm font-medium text-slate-300 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleCleanupOrphans}
                disabled={isCleaning}
                className="flex-1 px-4 py-2.5 text-sm font-medium bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                {isCleaning ? (
                  <>
                    <SpinnerIcon size={16} className="animate-spin" />
                    Cleaning...
                  </>
                ) : (
                  <>
                    <Trash size={16} weight="bold" />
                    Delete Files
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}


function StorageItem({ label, size, color }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-slate-800 last:border-0">
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${color.replace('text-', 'bg-')}`} />
        <span className="text-sm text-slate-300">{label}</span>
      </div>
      <span className={`text-sm font-medium ${color} tabular-nums`}>{size.toFixed(2)} GB</span>
    </div>
  )
}

// Shared Setting Components
function SettingToggle({ label, description, checked, onChange }) {
  return (
    <div className="flex items-center justify-between py-3">
      <div>
        <p className="text-sm font-medium text-slate-300">{label}</p>
        <p className="text-xs text-slate-500 mt-0.5">{description}</p>
      </div>
      <Toggle checked={checked} onChange={onChange} />
    </div>
  )
}

function SettingSlider({ label, description, value, onChange, min, max, suffix }) {
  return (
    <div className="py-3">
      <div className="flex items-center justify-between mb-3">
        <div>
          <p className="text-sm font-medium text-slate-300">{label}</p>
          <p className="text-xs text-slate-500 mt-0.5">{description}</p>
        </div>
        <span className="text-sm font-bold text-white tabular-nums">
          {value}{suffix}
        </span>
      </div>
      <Slider value={value} onChange={onChange} min={min} max={max} />
    </div>
  )
}
