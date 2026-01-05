import { useState, useEffect, useCallback } from 'react'
import { authenticatedFetch } from '../services/api'

export function useTemplates() {
  const [templates, setTemplates] = useState({ front: [], back: [] })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchTemplates = useCallback(async () => {
    setLoading(true)
    setError(null)
    
    try {
      const data = await authenticatedFetch('/api/templates')
      setTemplates(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  const uploadTemplate = useCallback(async (files, type) => {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    formData.append('type', type)

    try {
      await authenticatedFetch('/api/templates/upload', {
        method: 'POST',
        body: formData,
      })
      await fetchTemplates()
      return true
    } catch (err) {
      console.error('Upload error:', err)
      return false
    }
  }, [fetchTemplates])

  const deleteTemplate = useCallback(async (templatePath) => {
    try {
      await authenticatedFetch('/api/templates', {
        method: 'DELETE',
        body: JSON.stringify({ path: templatePath }),
      })
      await fetchTemplates()
      return true
    } catch (err) {
      console.error('Delete error:', err)
      return false
    }
  }, [fetchTemplates])

  useEffect(() => {
    fetchTemplates()
  }, [fetchTemplates])

  return {
    templates,
    loading,
    error,
    refresh: fetchTemplates,
    upload: uploadTemplate,
    delete: deleteTemplate,
  }
}
