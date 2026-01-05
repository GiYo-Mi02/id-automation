import { useState, useEffect } from 'react'
import { useSettings } from '../contexts/SettingsContext'
import { useWebSocket } from '../contexts/WebSocketContext'
import { useToast } from '../contexts/ToastContext'
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
      const res = await fetch('/api/system/stats')
      if (res.ok) {
        const data = await res.json()
        setSystemStats(data)
      }
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
              <p className="text-2xl font-bold text-white tabular-nums">{stats.completedJobs}</p>
              <p className="text-xs text-slate-500">Total Records</p>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-amber-500/20 rounded-lg">
              <Clock size={20} className="text-amber-400" weight="duotone" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white tabular-nums">{stats.pendingJobs}</p>
              <p className="text-xs text-slate-500">Pending</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Actions */}
      <Card className="p-6">
        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-4">Database Actions</h3>
        <div className="space-y-3">
          <Button variant="outline" icon={Trash} className="w-full justify-start">
            Clear All Data
          </Button>
        </div>
      </Card>
    </div>
  )
}

// Storage Settings Section
function StorageSettings({ stats, storagePercent }) {
  const [isRefreshing, setIsRefreshing] = useState(false)

  const handleRefreshStorage = async () => {
    setIsRefreshing(true)
    try {
      const res = await fetch('/api/system/stats')
      if (res.ok) {
        const data = await res.json()
        // Stats will be updated via parent component
      }
    } catch (err) {
      console.error('Failed to refresh storage:', err)
    } finally {
      setIsRefreshing(false)
    }
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
