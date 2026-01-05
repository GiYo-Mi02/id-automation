import { useState, useEffect, useCallback } from 'react'
import { useWebSocket } from '../contexts/WebSocketContext'
import { useToast } from '../contexts/ToastContext'
import { authenticatedFetch, api } from '../services/api'
import DashboardTopBar from '../components/dashboard/DashboardTopBar'
import StatsGrid from '../components/dashboard/StatsGrid'
import LivePreviewColumn from '../components/dashboard/LivePreviewColumn'
import StudentTable from '../components/dashboard/StudentTable'
import EditStudentModal from '../components/dashboard/EditStudentModal'
import ViewIDModal from '../components/dashboard/ViewIDModal'

export default function DashboardPage() {
  const { status, lastMessage, clearLastMessage } = useWebSocket()
  const toast = useToast()
  
  const [templates, setTemplates] = useState({ front: [], back: [] })
  const [activeTemplate, setActiveTemplate] = useState({ front: null, back: null })
  const [latestOutput, setLatestOutput] = useState(null)
  const [students, setStudents] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalStudents, setTotalStudents] = useState(0)
  const [sortBy, setSortBy] = useState('created_at')
  const [sortOrder, setSortOrder] = useState('DESC')
  const [filterSection, setFilterSection] = useState('')
  
  const [editingStudent, setEditingStudent] = useState(null)
  const [viewingStudent, setViewingStudent] = useState(null)

  // Define fetch functions with useCallback (must be before useEffect that uses them)
  const fetchTemplates = useCallback(async () => {
    try {
      const data = await api.get('/api/templates')
      setTemplates(data)
      // Set active templates if available
      if (data.front?.length > 0) {
        setActiveTemplate(prev => ({ ...prev, front: data.front[0] }))
      }
      if (data.back?.length > 0) {
        setActiveTemplate(prev => ({ ...prev, back: data.back[0] }))
      }
    } catch (err) {
      console.error('Failed to fetch templates:', err)
    }
  }, [])

  const fetchStudents = useCallback(async () => {
    setIsLoading(true)
    try {
      const params = new URLSearchParams({
        page: currentPage.toString(),
        page_size: '50',
        sort_by: sortBy,
        sort_order: sortOrder
      })
      
      if (filterSection) {
        params.append('section', filterSection)
      }
      
      const data = await api.get(`/api/students?${params.toString()}`)
      // Backend returns {students: [], total: N, page: 1, page_size: 50}
      setStudents(data.students || [])
      setTotalStudents(data.total || 0)
    } catch (err) {
      console.error('Failed to fetch students:', err)
      setStudents([])
      setTotalStudents(0)
    } finally {
      setIsLoading(false)
    }
  }, [currentPage, sortBy, sortOrder, filterSection])

  const fetchLatestOutput = useCallback(async () => {
    try {
      const data = await api.get('/api/history?limit=1')
      // Backend returns {history: [], total: N, limit: N}
      if (data.history && data.history.length > 0) {
        setLatestOutput(data.history[0])
      }
    } catch (err) {
      console.error('Failed to fetch latest output:', err)
    }
  }, [])

  // Fetch initial data
  useEffect(() => {
    fetchTemplates()
    fetchStudents()
    fetchLatestOutput()
  }, [fetchTemplates, fetchStudents, fetchLatestOutput])

  // Listen for WebSocket updates
  useEffect(() => {
    if (lastMessage?.type === 'id_generated') {
      setLatestOutput(lastMessage.data)
      fetchStudents() // Refresh student list
      toast.success('New ID Generated', `ID created for ${lastMessage.data.full_name}`)
      
      // Clear the message immediately after processing to prevent re-triggering
      clearLastMessage()
    }
  }, [lastMessage, fetchStudents, clearLastMessage, toast])

  const handleTemplateSelect = (type, template) => {
    setActiveTemplate(prev => ({ ...prev, [type]: template }))
  }

  const handleEditStudent = (student) => {
    setEditingStudent(student)
  }

  const handleViewStudent = (student) => {
    setViewingStudent(student)
  }

  const handleSaveStudent = async (updatedStudent) => {
    try {
      const studentId = updatedStudent.student_id || updatedStudent.id_number
      await api.put(`/api/students/${studentId}`, updatedStudent)
      toast.success('Student Updated', 'Student information saved successfully')
      setEditingStudent(null)
      fetchStudents()
    } catch (err) {
      toast.error('Update Failed', err.message || 'Could not save student information')
    }
  }

  const handleRegenerate = async (student) => {
    try {
      const studentId = student.student_id || student.id_number
      await api.post(`/api/regenerate/${studentId}`)
      toast.info('Regenerating', `ID regeneration started for ${student.full_name}`)
    } catch (err) {
      toast.error('Regeneration Failed', err.message || 'Could not regenerate ID')
    }
  }

  return (
    <div className="h-full flex flex-col bg-slate-950 text-slate-200 font-sans">
      <DashboardTopBar status={status} />

      <div className="flex-1 p-6 overflow-hidden flex flex-col">
        {/* Top Row: Stats */}
        <StatsGrid totalIds={students.length} />

        {/* Main Split */}
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-0">
          {/* Left: Recent Activity (70% -> col-span-8) */}
          <div className="lg:col-span-8 h-full min-h-0">
            <StudentTable
              students={students}
              isLoading={isLoading}
              totalStudents={totalStudents}
              currentPage={currentPage}
              onPageChange={setCurrentPage}
              sortBy={sortBy}
              sortOrder={sortOrder}
              onSortChange={(newSortBy, newSortOrder) => {
                setSortBy(newSortBy)
                setSortOrder(newSortOrder)
                setCurrentPage(1)
              }}
              filterSection={filterSection}
              onFilterChange={(section) => {
                setFilterSection(section)
                setCurrentPage(1)
              }}
              onRefresh={fetchStudents}
              onEdit={handleEditStudent}
              onView={handleViewStudent}
              onRegenerate={handleRegenerate}
            />
          </div>

          {/* Right: Live Preview (30% -> col-span-4) */}
          <div className="lg:col-span-4 h-full min-h-0">
            <LivePreviewColumn
              latestOutput={latestOutput}
              templates={templates}
              activeTemplate={activeTemplate}
              onTemplateSelect={handleTemplateSelect}
              onRegenerate={() => latestOutput && handleRegenerate(latestOutput)}
              onView={() => latestOutput && handleViewStudent(latestOutput)}
            />
          </div>
        </div>
      </div>

      {/* Modals */}
      <EditStudentModal
        isOpen={!!editingStudent}
        onClose={() => setEditingStudent(null)}
        student={editingStudent}
        onSave={handleSaveStudent}
      />

      <ViewIDModal
        isOpen={!!viewingStudent}
        onClose={() => setViewingStudent(null)}
        student={viewingStudent}
      />
    </div>
  )
}
