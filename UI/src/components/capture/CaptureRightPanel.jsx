import { useState, useEffect, useCallback } from 'react'
import { clsx } from 'clsx'
import { ClockCounterClockwise, ArrowsClockwise, Eye, Camera, PencilSimple, CaretLeft, CaretRight, Users, Check, MagnifyingGlass } from '@phosphor-icons/react'
import { Input, Spinner } from '../shared'
import { formatDistanceToNow } from '../utils/formatTime'
import { authenticatedFetch } from '../../services/api'

const ITEMS_PER_PAGE = 10

export default function CaptureRightPanel({
  inputMode,
  captures,
  onRefresh,
  onView,
  manualData,
  onManualDataChange,
  onStudentSelect,
}) {
  const [activeTab, setActiveTab] = useState('history')
  const [currentPage, setCurrentPage] = useState(1)
  const [students, setStudents] = useState([])
  const [isLoadingStudents, setIsLoadingStudents] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  // Stable fetch function to prevent infinite loops
  const fetchStudents = useCallback(async () => {
    setIsLoadingStudents(true)
    try {
      const data = await authenticatedFetch('/api/students?page=1&page_size=100')
      // Backend returns {students: [], total: N, page: 1, page_size: 100}
      setStudents(data.students || [])
    } catch (err) {
      console.error('Failed to fetch students:', err)
      setStudents([])
    } finally {
      setIsLoadingStudents(false)
    }
  }, [])

  // Fetch all students when Students tab is active
  useEffect(() => {
    if (activeTab === 'students' && inputMode === 'database') {
      fetchStudents()
    }
  }, [activeTab, inputMode, fetchStudents])

  // Reset page and search when tab changes
  useEffect(() => {
    setCurrentPage(1)
    setSearchQuery('')
  }, [activeTab])

  // Determine what content to show
  const showManualForm = inputMode === 'manual'
  const effectiveTab = showManualForm ? 'form' : activeTab

  // Filter students based on search query
  const filteredStudents = effectiveTab === 'students' && searchQuery
    ? students.filter(student => {
        const id = (student.student_id || student.id_number || '').toLowerCase()
        const name = (student.full_name || '').toLowerCase()
        const query = searchQuery.toLowerCase()
        return id.includes(query) || name.includes(query)
      })
    : students

  // Get data for current tab with pagination
  const getTabData = () => {
    if (effectiveTab === 'history') return captures
    if (effectiveTab === 'students') return filteredStudents
    return []
  }

  const tabData = getTabData() || []
  const safeTabData = Array.isArray(tabData) ? tabData : []
  const totalPages = Math.ceil(safeTabData.length / ITEMS_PER_PAGE)
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE
  const endIndex = startIndex + ITEMS_PER_PAGE
  const paginatedData = safeTabData.slice(startIndex, endIndex)

  const handleManualChange = (field, value) => {
    onManualDataChange(prev => ({ ...prev, [field]: value }))
  }

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage)
    }
  }

  return (
    <div className="h-full flex flex-col bg-navy-900 border-l border-navy-700">
      {/* Header */}
      <div className="h-14 px-5 flex items-center justify-between border-b border-navy-700 bg-gradient-to-r from-navy-850 to-navy-900 shrink-0">
        <div className="flex items-center gap-2 text-base font-bold text-slate-200">
          {effectiveTab === 'history' && (
            <>
              <ClockCounterClockwise size={20} weight="bold" />
              Recent Captures
            </>
          )}
          {effectiveTab === 'students' && (
            <>
              <Users size={20} weight="bold" />
              Student Database
            </>
          )}
          {effectiveTab === 'form' && (
            <>
              <PencilSimple size={20} weight="bold" />
              Manual Entry
            </>
          )}
        </div>
        {(effectiveTab === 'history' || effectiveTab === 'students') && (
          <button
            onClick={effectiveTab === 'history' ? onRefresh : fetchStudents}
            className="w-9 h-9 flex items-center justify-center rounded-lg border border-navy-700 text-slate-400 hover:bg-navy-800 hover:text-slate-200 transition-all active:rotate-180 active:transition-transform active:duration-500"
            title="Refresh"
          >
            <ArrowsClockwise size={18} weight="bold" />
          </button>
        )}
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto">
        {/* Search Bar - Only show for Students tab */}
        {effectiveTab === 'students' && (
          <div className="sticky top-0 z-10 p-3 bg-navy-900 border-b border-navy-700">
            <div className="relative">
              <MagnifyingGlass
                size={18}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none"
              />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by ID or Name..."
                className="w-full h-10 pl-10 pr-4 bg-navy-800 border border-navy-700 rounded-lg text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
                  title="Clear search"
                >
                  ✕
                </button>
              )}
            </div>
          </div>
        )}

        {effectiveTab === 'history' && (
          <HistoryContent
            captures={paginatedData}
            onView={onView}
            isEmpty={captures.length === 0}
          />
        )}
        {effectiveTab === 'students' && (
          <StudentsContent
            students={paginatedData}
            onStudentSelect={onStudentSelect}
            isEmpty={tabData.length === 0}
            isLoading={isLoadingStudents}
            searchQuery={searchQuery}
          />
        )}
        {effectiveTab === 'form' && (
          <ManualFormContent
            manualData={manualData}
            onManualChange={handleManualChange}
          />
        )}
      </div>

      {/* Pagination - Show for History and Students */}
      {!showManualForm && tabData.length > 0 && (
        <div className="px-4 py-3 border-t border-navy-700 bg-navy-850 shrink-0">
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-400">
              Showing {startIndex + 1}-{Math.min(endIndex, tabData.length)} of {tabData.length}
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className={clsx(
                  'w-8 h-8 flex items-center justify-center rounded-md border transition-colors',
                  currentPage === 1
                    ? 'border-navy-700 text-slate-700 cursor-not-allowed'
                    : 'border-navy-600 text-slate-400 hover:bg-navy-800 hover:text-slate-200'
                )}
              >
                <CaretLeft size={16} weight="bold" />
              </button>
              <span className="text-slate-300 font-mono">
                {currentPage} / {totalPages}
              </span>
              <button
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                className={clsx(
                  'w-8 h-8 flex items-center justify-center rounded-md border transition-colors',
                  currentPage === totalPages
                    ? 'border-navy-700 text-slate-700 cursor-not-allowed'
                    : 'border-navy-600 text-slate-400 hover:bg-navy-800 hover:text-slate-200'
                )}
              >
                <CaretRight size={16} weight="bold" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Tab Navigation - Only show when in database mode */}
      {!showManualForm && (
        <div className="h-14 px-4 flex items-center gap-2 border-t border-navy-700 bg-navy-850 shrink-0">
          <button
            onClick={() => setActiveTab('history')}
            className={clsx(
              'flex-1 h-10 rounded-lg font-semibold text-sm transition-all flex items-center justify-center gap-2',
              activeTab === 'history'
                ? 'bg-blue-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200 hover:bg-navy-800'
            )}
          >
            <ClockCounterClockwise size={18} weight="bold" />
            History
          </button>
          <button
            onClick={() => setActiveTab('students')}
            className={clsx(
              'flex-1 h-10 rounded-lg font-semibold text-sm transition-all flex items-center justify-center gap-2',
              activeTab === 'students'
                ? 'bg-blue-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200 hover:bg-navy-800'
            )}
          >
            <Users size={18} weight="bold" />
            Students
          </button>
        </div>
      )}
    </div>
  )
}

function HistoryContent({ captures, onView, isEmpty }) {
  if (isEmpty) {
    return (
      <div className="flex flex-col items-center justify-center h-full py-12 px-6">
        <Camera size={80} className="text-slate-700 animate-pulse-slow" weight="thin" />
        <p className="mt-6 text-lg font-semibold text-slate-400">No captures yet</p>
        <p className="text-sm text-slate-600 mt-2 text-center">
          Capture your first ID to see it appear here
        </p>
      </div>
    )
  }

  return (
    <ul className="p-3 space-y-2">
      {(Array.isArray(captures) ? captures : []).map((capture, index) => (
        <CaptureItem
          key={`${capture.student_id || capture.id_number}-${capture.timestamp || capture.created_at}-${index}`}
          capture={capture}
          onView={onView}
        />
      ))}
    </ul>
  )
}

function CaptureItem({ capture, onView }) {
  return (
    <li
      onClick={() => onView(capture)}
      className="group flex items-center gap-3 p-3 rounded-xl cursor-pointer bg-navy-800/50 border border-navy-700/50 hover:bg-navy-800 hover:border-blue-600/50 transition-all hover:shadow-lg"
    >
      {/* Thumbnail */}
      <div className="w-14 h-14 rounded-lg border-2 border-navy-700 bg-navy-900 overflow-hidden shrink-0 group-hover:border-blue-500 transition-colors">
        {capture.front_image ? (
          <img
            src={capture.front_image}
            alt=""
            className="w-full h-full object-cover"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-slate-700">
            <Camera size={24} />
          </div>
        )}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-bold text-slate-100 group-hover:text-blue-400 transition-colors truncate font-mono">
          {capture.student_id || capture.id_number}
        </p>
        <p className="text-sm text-slate-300 truncate font-medium">{capture.full_name}</p>
        <p className="text-xs text-slate-500 mt-1 flex items-center gap-1">
          <ClockCounterClockwise size={12} />
          {formatDistanceToNow(capture.timestamp || capture.created_at)}
        </p>
      </div>

      {/* View Icon */}
      <div className="text-slate-600 group-hover:text-blue-400 transition-all group-hover:scale-125">
        <Eye size={20} weight="bold" />
      </div>
    </li>
  )
}

function StudentsContent({ students, onStudentSelect, isEmpty, isLoading, searchQuery }) {
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-full py-12 px-6">
        <Spinner size="lg" />
        <p className="mt-6 text-sm text-slate-400">Loading students...</p>
      </div>
    )
  }

  if (isEmpty) {
    return (
      <div className="flex flex-col items-center justify-center h-full py-12 px-6">
        <Users size={80} className="text-slate-700" weight="thin" />
        <p className="mt-6 text-lg font-semibold text-slate-400">
          {searchQuery ? 'No students found' : 'No students in database'}
        </p>
        <p className="text-sm text-slate-600 mt-2 text-center">
          {searchQuery ? `No results for "${searchQuery}"` : 'Import students to get started'}
        </p>
      </div>
    )
  }

  return (
    <ul className="p-3 space-y-2">
      {(Array.isArray(students) ? students : []).map((student) => (
        <StudentItem
          key={student.student_id || student.id_number}
          student={student}
          onSelect={onStudentSelect}
        />
      ))}
    </ul>
  )
}

function StudentItem({ student, onSelect }) {
  const studentId = student.student_id || student.id_number

  return (
    <li className="group flex items-center gap-3 p-3 rounded-xl bg-navy-800/50 border border-navy-700/50 hover:bg-navy-800 hover:border-blue-600/50 transition-all">
      {/* Student Icon */}
      <div className="w-10 h-10 rounded-lg bg-navy-900 border-2 border-navy-700 flex items-center justify-center text-slate-400 group-hover:border-blue-500 group-hover:text-blue-400 transition-colors shrink-0">
        <Users size={20} weight="bold" />
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-bold text-slate-100 font-mono">
          {studentId}
        </p>
        <p className="text-sm text-slate-300 truncate">{student.full_name}</p>
        {student.section && (
          <p className="text-xs text-slate-500 mt-0.5">{student.section}</p>
        )}
      </div>

      {/* Select Button */}
      <button
        onClick={() => onSelect(student)}
        className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-lg transition-all flex items-center gap-1.5 hover:shadow-lg hover:scale-105"
      >
        <Check size={14} weight="bold" />
        Select
      </button>
    </li>
  )
}

function ManualFormContent({ manualData, onManualChange }) {
  return (
    <div className="p-5 space-y-4">
      <div className="space-y-1 mb-6">
        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wide">Student Information</h3>
        <p className="text-xs text-slate-500">Enter student details manually</p>
      </div>

      <Input
        label="ID Number"
        value={manualData.id_number}
        onChange={(e) => onManualChange('id_number', e.target.value)}
        placeholder="e.g., 2025-208"
        required
      />

      <Input
        label="Full Name"
        value={manualData.full_name}
        onChange={(e) => onManualChange('full_name', e.target.value)}
        placeholder="e.g., Juan Dela Cruz"
        required
      />

      <Input
        label="LRN Number"
        value={manualData.lrn_number}
        onChange={(e) => onManualChange('lrn_number', e.target.value)}
        placeholder="e.g., 123456789012"
      />

      <div className="grid grid-cols-2 gap-4">
        <Input
          label="Grade Level"
          value={manualData.grade_level}
          onChange={(e) => onManualChange('grade_level', e.target.value)}
          placeholder="e.g., Grade 7"
        />
        <Input
          label="Section"
          value={manualData.section}
          onChange={(e) => onManualChange('section', e.target.value)}
          placeholder="e.g., Einstein"
        />
      </div>

      <div className="pt-4 border-t border-navy-700">
        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wide mb-4">Guardian Information</h3>

        <div className="space-y-4">
          <Input
            label="Guardian Name"
            value={manualData.guardian_name}
            onChange={(e) => onManualChange('guardian_name', e.target.value)}
            placeholder="Parent/Guardian name"
          />

          <Input
            label="Contact Number"
            value={manualData.contact_number}
            onChange={(e) => onManualChange('contact_number', e.target.value)}
            placeholder="e.g., 09123456789"
          />

          <Input
            label="Address"
            value={manualData.address}
            onChange={(e) => onManualChange('address', e.target.value)}
            placeholder="Complete address"
          />
        </div>
      </div>
    </div>
  )
}
