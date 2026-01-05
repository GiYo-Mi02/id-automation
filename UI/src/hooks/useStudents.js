import { useState, useEffect, useCallback } from 'react'
import { authenticatedFetch } from '../services/api'

export function useStudents(initialLimit = 50) {
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchStudents = useCallback(async (limit = initialLimit) => {
    setLoading(true)
    setError(null)
    
    try {
      const data = await authenticatedFetch(`/api/students?page=1&page_size=${limit}`)
      // Backend returns {students: [], total: N, page: 1, page_size: limit}
      setStudents(data.students || [])
    } catch (err) {
      setError(err.message)
      setStudents([])
    } finally {
      setLoading(false)
    }
  }, [initialLimit])

  const searchStudents = useCallback(async (query) => {
    if (!query) return []
    
    try {
      return await authenticatedFetch(`/api/students/search?q=${encodeURIComponent(query)}`)
    } catch (err) {
      console.error('Search error:', err)
      return []
    }
  }, [])

  const updateStudent = useCallback(async (idNumber, data) => {
    try {
      await authenticatedFetch(`/api/students/${idNumber}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      })
      await fetchStudents()
      return true
    } catch (err) {
      console.error('Update error:', err)
      return false
    }
  }, [fetchStudents])

  useEffect(() => {
    fetchStudents()
  }, [fetchStudents])

  return {
    students,
    loading,
    error,
    refresh: fetchStudents,
    search: searchStudents,
    update: updateStudent,
  }
}
