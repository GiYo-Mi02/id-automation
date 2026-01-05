import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { authenticatedFetch } from '../services/api'

const SettingsContext = createContext(null)

const defaultSettings = {
  smoothStrength: 7,
  enableHairCleanup: true,
  enableFaceRestoration: false,
  enableBackgroundRemoval: true,
}

export function SettingsProvider({ children }) {
  const [settings, setSettings] = useState(defaultSettings)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchSettings()
  }, [])

  const fetchSettings = async () => {
    try {
      const data = await authenticatedFetch('/api/settings')
      setSettings(prev => ({ ...prev, ...data }))
    } catch (err) {
      console.error('Failed to fetch settings:', err)
    } finally {
      setLoading(false)
    }
  }

  const updateSettings = useCallback(async (newSettings) => {
    const updated = { ...settings, ...newSettings }
    setSettings(updated)
    
    try {
      await authenticatedFetch('/api/settings', {
        method: 'POST',
        body: JSON.stringify(updated),
      })
      return true
    } catch (err) {
      console.error('Failed to save settings:', err)
      return false
    }
  }, [settings])

  const resetSettings = useCallback(() => {
    setSettings(defaultSettings)
  }, [])

  return (
    <SettingsContext.Provider value={{ settings, updateSettings, resetSettings, loading }}>
      {children}
    </SettingsContext.Provider>
  )
}

export function useSettings() {
  const context = useContext(SettingsContext)
  if (!context) {
    throw new Error('useSettings must be used within a SettingsProvider')
  }
  return context
}
