import { useState, useEffect, useCallback } from 'react'

export function useTemplates() {
  const [templates, setTemplates] = useState({ front: [], back: [] })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchTemplates = useCallback(async () => {
    setLoading(true)
    setError(null)
    
    try {
      const res = await fetch('/api/templates')
      if (!res.ok) throw new Error('Failed to fetch templates')
      const data = await res.json()
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
      const res = await fetch('/api/templates/upload', {
        method: 'POST',
        body: formData,
      })
      if (!res.ok) throw new Error('Upload failed')
      await fetchTemplates()
      return true
    } catch (err) {
      console.error('Upload error:', err)
      return false
    }
  }, [fetchTemplates])

  const deleteTemplate = useCallback(async (templatePath) => {
    try {
      const res = await fetch('/api/templates', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: templatePath }),
      })
      if (!res.ok) throw new Error('Delete failed')
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
