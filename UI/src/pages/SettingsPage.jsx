import { useState, useEffect } from 'react'
import { useSettings } from '../contexts/SettingsContext'
import { useWebSocket } from '../contexts/WebSocketContext'
import { useToast } from '../contexts/ToastContext'
import {
  Sliders,
  FloppyDisk,
  BookOpen,
  CaretRight,
  Info,
  Trash,
  ChartBar,
  Database,
  Clock,
  HardDrives,
  Spinner as SpinnerIcon,
  CheckCircle,
} from '@phosphor-icons/react'
import { Button, Toggle, Slider, Card, Badge, Spinner } from '../components/shared'
import ImportDataSection from '../components/settings/ImportDataSection'

export default function SettingsPage() {
  const { settings, updateSettings, loading } = useSettings()
  const { status } = useWebSocket()
  const toast = useToast()

  const [localSettings, setLocalSettings] = useState(settings)
  const [isSaving, setIsSaving] = useState(false)
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

  const handleClearHistory = async () => {
    if (!confirm('Are you sure you want to clear all generation history? This cannot be undone.')) {
      return
    }

    try {
      const res = await fetch('/api/history', { method: 'DELETE' })
      if (res.ok) {
        toast.success('History Cleared', 'All generation history has been removed')
        fetchSystemStats()
      }
    } catch (err) {
      toast.error('Clear Failed', 'Could not clear history')
    }
  }

  const handleExportAnalytics = async () => {
    try {
      const res = await fetch('/api/analytics/export')
      if (res.ok) {
        const blob = await res.blob()
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'analytics.csv'
        a.click()
        URL.revokeObjectURL(url)
        toast.success('Export Complete', 'Analytics exported successfully')
      }
    } catch (err) {
      toast.error('Export Failed', 'Could not export analytics')
    }
  }

  const storagePercent = Math.round((systemStats.storageUsed / systemStats.storageTotal) * 100)

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto bg-navy-950">
      <div className="max-w-3xl mx-auto px-6 py-10">
        {/* Page Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Sliders size={28} className="text-blue-500" />
            <h1 className="text-2xl font-bold text-slate-100">Settings</h1>
          </div>
          <p className="text-sm text-slate-500">Configure system preferences</p>
        </div>

        {/* Image Enhancement Section */}
        <CollapsibleSection title="IMAGE ENHANCEMENT" defaultOpen>
          <div className="space-y-6">
            {/* Smooth Strength */}
            <Slider
              label="Smooth Strength"
              value={localSettings.smoothStrength || 7}
              onChange={(v) => handleSettingChange('smoothStrength', v)}
              min={1}
              max={10}
              step={1}
            />

            {/* Toggles */}
            <div className="space-y-4 pt-2">
              <div className="flex items-center justify-between py-3 border-b border-navy-800">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-slate-300">Enable Hair Cleanup</span>
                  <button className="text-slate-500 hover:text-blue-400" title="Removes stray hairs and smooths hair edges">
                    <Info size={16} />
                  </button>
                </div>
                <Toggle
                  checked={localSettings.enableHairCleanup}
                  onChange={(v) => handleSettingChange('enableHairCleanup', v)}
                />
              </div>

              <div className="flex items-center justify-between py-3 border-b border-navy-800">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-slate-300">Enable Face Restoration</span>
                  <button className="text-slate-500 hover:text-blue-400" title="Uses AI to enhance facial features (requires GFPGAN)">
                    <Info size={16} />
                  </button>
                </div>
                <Toggle
                  checked={localSettings.enableFaceRestoration}
                  onChange={(v) => handleSettingChange('enableFaceRestoration', v)}
                />
              </div>

              <div className="flex items-center justify-between py-3">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-slate-300">Enable Background Removal</span>
                  <button className="text-slate-500 hover:text-blue-400" title="Automatically removes and replaces photo background">
                    <Info size={16} />
                  </button>
                </div>
                <Toggle
                  checked={localSettings.enableBackgroundRemoval}
                  onChange={(v) => handleSettingChange('enableBackgroundRemoval', v)}
                />
              </div>
            </div>
          </div>
        </CollapsibleSection>

        {/* System Section */}
        <CollapsibleSection title="SYSTEM" defaultOpen>
          <div className="space-y-6">
            {/* Database Connection */}
            <div className="p-4 bg-navy-850 border border-navy-700 rounded-lg">
              <h4 className="text-sm font-semibold text-slate-300 mb-3">Database Connection</h4>
              <div className="flex items-center gap-3">
                <span className={`w-3 h-3 rounded-full ${status === 'connected' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
                <span className="text-sm text-slate-400">
                  {status === 'connected' ? 'Connected' : status === 'connecting' ? 'Connecting...' : 'Disconnected'}
                  {status === 'connected' && <span className="font-mono text-slate-500"> - localhost:3306</span>}
                </span>
              </div>
              <div className="flex items-center gap-2 mt-2 text-xs text-slate-600">
                <Clock size={12} />
                <span>Last sync: {systemStats.lastSync ? new Date(systemStats.lastSync).toLocaleTimeString() : 'Never'}</span>
              </div>
            </div>

            {/* Storage Usage */}
            <div>
              <h4 className="text-sm font-semibold text-slate-300 mb-2">Storage Usage</h4>
              <div className="h-2 bg-navy-700 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    storagePercent > 80 ? 'bg-gradient-to-r from-red-600 to-red-500' :
                    storagePercent > 60 ? 'bg-gradient-to-r from-amber-600 to-amber-500' :
                    'bg-gradient-to-r from-blue-600 to-blue-500'
                  }`}
                  style={{ width: `${storagePercent}%` }}
                />
              </div>
              <p className="mt-2 text-sm text-slate-400 tabular-nums">
                {systemStats.storageUsed} GB / {systemStats.storageTotal} GB ({storagePercent}%)
              </p>
            </div>

            {/* Processing Queue */}
            <div className="flex gap-4 p-3 bg-navy-850 rounded-lg">
              <div className="flex-1 text-center">
                <div className="flex items-center justify-center gap-2 mb-1">
                  {systemStats.pendingJobs > 0 ? (
                    <SpinnerIcon size={20} className="text-blue-400 animate-spin" />
                  ) : (
                    <CheckCircle size={20} className="text-slate-600" />
                  )}
                </div>
                <p className="text-2xl font-bold text-slate-200 tabular-nums">{systemStats.pendingJobs}</p>
                <p className="text-xs uppercase text-slate-600 tracking-wide">Pending</p>
              </div>
              <div className="w-px bg-navy-700" />
              <div className="flex-1 text-center">
                <div className="flex items-center justify-center gap-2 mb-1">
                  <CheckCircle size={20} className="text-green-400" />
                </div>
                <p className="text-2xl font-bold text-green-400 tabular-nums">{systemStats.completedJobs}</p>
                <p className="text-xs uppercase text-slate-600 tracking-wide">Completed</p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 pt-2">
              <Button
                variant="danger"
                icon={Trash}
                onClick={handleClearHistory}
              >
                Clear History
              </Button>
              <Button
                variant="secondary"
                icon={ChartBar}
                onClick={handleExportAnalytics}
              >
                Export Analytics
              </Button>
            </div>
          </div>
        </CollapsibleSection>

        {/* Import Data Section */}
        <ImportDataSection onImportComplete={fetchSystemStats} />

        {/* About Section */}
        <CollapsibleSection title="ABOUT">
          <div className="space-y-3 text-sm">
            <p className="text-slate-400">Version <span className="text-slate-200 font-medium">2.0.1</span></p>
            <p className="text-slate-600">Last updated: January 5, 2026</p>
            <div className="flex gap-4 pt-2">
              <a href="#" className="text-blue-400 hover:text-blue-300 transition-colors">GitHub</a>
              <a href="#" className="text-blue-400 hover:text-blue-300 transition-colors">Documentation</a>
              <a href="#" className="text-blue-400 hover:text-blue-300 transition-colors">Support</a>
            </div>
          </div>
        </CollapsibleSection>

        {/* Footer Actions */}
        <div className="sticky bottom-0 flex items-center justify-between py-5 mt-10 border-t border-navy-700 bg-navy-950">
          <Button
            variant="primary"
            icon={FloppyDisk}
            loading={isSaving}
            onClick={handleSave}
            size="lg"
          >
            SAVE CHANGES
          </Button>
          <Button
            variant="ghost"
            icon={BookOpen}
          >
            View Documentation
          </Button>
        </div>
      </div>
    </div>
  )
}

function CollapsibleSection({ title, children, defaultOpen = false }) {
  const [isOpen, setIsOpen] = useState(defaultOpen)

  return (
    <Card className="mb-5 overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full h-14 px-5 flex items-center justify-between hover:bg-navy-850 transition-colors"
      >
        <span className="text-base font-bold uppercase text-slate-300 tracking-wide">{title}</span>
        <CaretRight
          size={20}
          className={`text-slate-500 transition-transform duration-200 ${isOpen ? 'rotate-90' : ''}`}
        />
      </button>
      {isOpen && (
        <div className="px-5 pb-5 border-t border-navy-800 pt-5 animate-slide-down">
          {children}
        </div>
      )}
    </Card>
  )
}
