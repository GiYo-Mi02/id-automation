import { useState, useEffect, useCallback } from 'react'
import { authenticatedFetch } from '../services/api'

export function useHistory(initialLimit = 50) {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchHistory = useCallback(async (limit = initialLimit) => {
    setLoading(true)
    setError(null)
    
    try {
      const data = await authenticatedFetch(`/api/history?limit=${limit}`)
      // Backend returns {history: [], total: N, limit: N}
      setHistory(data.history || [])
    } catch (err) {
      setError(err.message)
      setHistory([])
    } finally {
      setLoading(false)
    }
  }, [initialLimit])

  const addToHistory = useCallback((item) => {
    setHistory(prev => [item, ...prev].slice(0, initialLimit))
  }, [initialLimit])

  const clearHistory = useCallback(async () => {
    try {
      await authenticatedFetch('/api/history', { method: 'DELETE' })
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
