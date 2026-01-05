import { useState, useEffect, useCallback } from 'react'

export function useHistory(initialLimit = 50) {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchHistory = useCallback(async (limit = initialLimit) => {
    setLoading(true)
    setError(null)
    
    try {
      const res = await fetch(`/api/history?limit=${limit}`)
      if (!res.ok) throw new Error('Failed to fetch history')
      const data = await res.json()
      setHistory(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [initialLimit])

  const addToHistory = useCallback((item) => {
    setHistory(prev => [item, ...prev].slice(0, initialLimit))
  }, [initialLimit])

  const clearHistory = useCallback(async () => {
    try {
      const res = await fetch('/api/history', { method: 'DELETE' })
      if (!res.ok) throw new Error('Clear failed')
      setHistory([])
      return true
    } catch (err) {
      console.error('Clear error:', err)
      return false
    }
  }, [])

  useEffect(() => {
    fetchHistory()
  }, [fetchHistory])

  return {
    history,
    loading,
    error,
    refresh: fetchHistory,
    add: addToHistory,
    clear: clearHistory,
  }
}
