import { useState, useEffect, useCallback } from 'react'

export function useStudents(initialLimit = 50) {
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchStudents = useCallback(async (limit = initialLimit) => {
    setLoading(true)
    setError(null)
    
    try {
      const res = await fetch(`/api/students?limit=${limit}`)
      if (!res.ok) throw new Error('Failed to fetch students')
      const data = await res.json()
      setStudents(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [initialLimit])

  const searchStudents = useCallback(async (query) => {
    if (!query) return []
    
    try {
      const res = await fetch(`/api/students/search?q=${encodeURIComponent(query)}`)
      if (!res.ok) throw new Error('Search failed')
      return await res.json()
    } catch (err) {
      console.error('Search error:', err)
      return []
    }
  }, [])

  const updateStudent = useCallback(async (idNumber, data) => {
    try {
      const res = await fetch(`/api/students/${idNumber}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
      if (!res.ok) throw new Error('Update failed')
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
