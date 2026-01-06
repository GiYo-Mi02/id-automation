import { useState, useEffect, useCallback } from 'react'
import { clsx } from 'clsx'
import { ClockCounterClockwise, ArrowsClockwise, Eye, Camera, PencilSimple, CaretLeft, CaretRight, Users, Check, MagnifyingGlass, Student, Chalkboard, UserCircle } from '@phosphor-icons/react'
import { Input, Spinner } from '../shared'
import { formatDistanceToNow } from '../utils/formatTime'
import { authenticatedFetch } from '../../services/api'

const ITEMS_PER_PAGE = 10

// Entity type configuration for badges
const ENTITY_CONFIG = {
  student: { label: 'Student', icon: Student, color: 'blue', bgClass: 'bg-blue-600/20', textClass: 'text-blue-400' },
  teacher: { label: 'Teacher', icon: Chalkboard, color: 'green', bgClass: 'bg-green-600/20', textClass: 'text-green-400' },
  staff: { label: 'Staff', icon: UserCircle, color: 'yellow', bgClass: 'bg-yellow-600/20', textClass: 'text-yellow-400' },
}

export default function CaptureRightPanel({
  inputMode,
  entityType = 'student',
  captures,
  onRefresh,
  onView,
  manualData,
  onManualDataChange,
  onStudentSelect,
  onTeacherSelect,
  onStaffSelect,
}) {
  const [activeTab, setActiveTab] = useState('history')
  const [currentPage, setCurrentPage] = useState(1)
  const [students, setStudents] = useState([])
  const [teachers, setTeachers] = useState([])
  const [staffMembers, setStaffMembers] = useState([])
  const [isLoadingStudents, setIsLoadingStudents] = useState(false)
  const [isLoadingTeachers, setIsLoadingTeachers] = useState(false)
  const [isLoadingStaff, setIsLoadingStaff] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  // Stable fetch function for students
  const fetchStudents = useCallback(async () => {
    setIsLoadingStudents(true)
    try {
      const data = await authenticatedFetch('/api/students?page=1&page_size=100')
      setStudents(data.students || [])
    } catch (err) {
      console.error('Failed to fetch students:', err)
      setStudents([])
    } finally {
      setIsLoadingStudents(false)
    }
  }, [])

  // Fetch teachers
  const fetchTeachers = useCallback(async () => {
    setIsLoadingTeachers(true)
    try {
      const data = await authenticatedFetch('/api/teachers?page=1&per_page=100')
      const teacherList = data.teachers || data.items || []
      setTeachers(Array.isArray(teacherList) ? teacherList : [])
    } catch (err) {
      console.error('Failed to fetch teachers:', err)
      setTeachers([])
    } finally {
      setIsLoadingTeachers(false)
    }
  }, [])

  // Fetch staff
  const fetchStaff = useCallback(async () => {
    setIsLoadingStaff(true)
    try {
      const data = await authenticatedFetch('/api/staff?page=1&per_page=100')
      const staffList = data.items || data.staff || []
      setStaffMembers(Array.isArray(staffList) ? staffList : [])
    } catch (err) {
      console.error('Failed to fetch staff:', err)
      setStaffMembers([])
    } finally {
      setIsLoadingStaff(false)
    }
  }, [])

  // Fetch data based on active tab
  useEffect(() => {
    if (inputMode === 'database') {
      if (activeTab === 'students') fetchStudents()
      else if (activeTab === 'teachers') fetchTeachers()
      else if (activeTab === 'staff') fetchStaff()
    }
  }, [activeTab, inputMode, fetchStudents, fetchTeachers, fetchStaff])

  // Reset page and search when tab changes
  useEffect(() => {
    setCurrentPage(1)
    setSearchQuery('')
  }, [activeTab])

  // Determine what content to show
  const showManualForm = inputMode === 'manual'
  const effectiveTab = showManualForm ? 'form' : activeTab

  // Filter data based on search query
  const filterData = (data, type) => {
    if (!searchQuery) return data
    const query = searchQuery.toLowerCase()
    return data.filter(item => {
      const id = (item.student_id || item.id_number || item.employee_id || '').toLowerCase()
      const name = (item.full_name || '').toLowerCase()
      const dept = (item.department || item.section || '').toLowerCase()
      return id.includes(query) || name.includes(query) || dept.includes(query)
    })
  }

  // Get data for current tab with filtering
  const getTabData = () => {
    if (effectiveTab === 'history') return captures
    if (effectiveTab === 'students') return filterData(students, 'student')
    if (effectiveTab === 'teachers') return filterData(teachers, 'teacher')
    if (effectiveTab === 'staff') return filterData(staffMembers, 'staff')
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

  const handleRefresh = () => {
    if (effectiveTab === 'history') onRefresh?.()
    else if (effectiveTab === 'students') fetchStudents()
    else if (effectiveTab === 'teachers') fetchTeachers()
    else if (effectiveTab === 'staff') fetchStaff()
  }

  const getHeaderInfo = () => {
    const config = ENTITY_CONFIG[entityType] || ENTITY_CONFIG.student
    if (effectiveTab === 'history') return { icon: ClockCounterClockwise, label: 'Recent Captures' }
    if (effectiveTab === 'students') return { icon: Student, label: 'Student Database' }
    if (effectiveTab === 'teachers') return { icon: Chalkboard, label: 'Teacher Database' }
    if (effectiveTab === 'staff') return { icon: UserCircle, label: 'Staff Database' }
    if (effectiveTab === 'form') return { icon: PencilSimple, label: `Manual Entry (${config.label})` }
    return { icon: Users, label: 'Database' }
  }

  const headerInfo = getHeaderInfo()
  const HeaderIcon = headerInfo.icon

  return (
    <div className="h-full flex flex-col bg-navy-900 border-l border-navy-700">
      {/* Header */}
      <div className="h-14 px-5 flex items-center justify-between border-b border-navy-700 bg-gradient-to-r from-navy-850 to-navy-900 shrink-0">
        <div className="flex items-center gap-2 text-base font-bold text-slate-200">
          <HeaderIcon size={20} weight="bold" />
          {headerInfo.label}
        </div>
        {(effectiveTab !== 'form') && (
          <button
            onClick={handleRefresh}
            className="w-9 h-9 flex items-center justify-center rounded-lg border border-navy-700 text-slate-400 hover:bg-navy-800 hover:text-slate-200 transition-all active:rotate-180 active:transition-transform active:duration-500"
            title="Refresh"
          >
            <ArrowsClockwise size={18} weight="bold" />
          </button>
        )}
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto">
        {/* Search Bar - Show for database tabs */}
        {['students', 'teachers', 'staff'].includes(effectiveTab) && (
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
                placeholder="Search by ID, Name, or Department..."
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
          <EntityListContent
            items={paginatedData}
            entityType="student"
            onSelect={onStudentSelect}
            isEmpty={safeTabData.length === 0}
            isLoading={isLoadingStudents}
            searchQuery={searchQuery}
          />
        )}
        {effectiveTab === 'teachers' && (
          <EntityListContent
            items={paginatedData}
            entityType="teacher"
            onSelect={onTeacherSelect}
            isEmpty={safeTabData.length === 0}
            isLoading={isLoadingTeachers}
            searchQuery={searchQuery}
          />
        )}
        {effectiveTab === 'staff' && (
          <EntityListContent
            items={paginatedData}
            entityType="staff"
            onSelect={onStaffSelect}
            isEmpty={safeTabData.length === 0}
            isLoading={isLoadingStaff}
            searchQuery={searchQuery}
          />
        )}
        {effectiveTab === 'form' && (
          <ManualFormContent
            entityType={entityType}
            manualData={manualData}
            onManualChange={handleManualChange}
          />
        )}
      </div>

      {/* Pagination - Show for History and entity lists */}
      {!showManualForm && safeTabData.length > 0 && (
        <div className="px-4 py-3 border-t border-navy-700 bg-navy-850 shrink-0">
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-400">
              Showing {startIndex + 1}-{Math.min(endIndex, safeTabData.length)} of {safeTabData.length}
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
        <div className="h-14 px-2 flex items-center gap-1 border-t border-navy-700 bg-navy-850 shrink-0">
          <button
            onClick={() => setActiveTab('history')}
            className={clsx(
              'flex-1 h-10 rounded-lg font-semibold text-xs transition-all flex items-center justify-center gap-1',
              activeTab === 'history'
                ? 'bg-blue-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200 hover:bg-navy-800'
            )}
          >
            <ClockCounterClockwise size={16} weight="bold" />
            <span className="hidden sm:inline">History</span>
          </button>
          <button
            onClick={() => setActiveTab('students')}
            className={clsx(
              'flex-1 h-10 rounded-lg font-semibold text-xs transition-all flex items-center justify-center gap-1',
              activeTab === 'students'
                ? 'bg-blue-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200 hover:bg-navy-800'
            )}
          >
            <Student size={16} weight="bold" />
            <span className="hidden sm:inline">Students</span>
          </button>
          <button
            onClick={() => setActiveTab('teachers')}
            className={clsx(
              'flex-1 h-10 rounded-lg font-semibold text-xs transition-all flex items-center justify-center gap-1',
              activeTab === 'teachers'
                ? 'bg-green-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200 hover:bg-navy-800'
            )}
          >
            <Chalkboard size={16} weight="bold" />
            <span className="hidden sm:inline">Teachers</span>
          </button>
          <button
            onClick={() => setActiveTab('staff')}
            className={clsx(
              'flex-1 h-10 rounded-lg font-semibold text-xs transition-all flex items-center justify-center gap-1',
              activeTab === 'staff'
                ? 'bg-yellow-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200 hover:bg-navy-800'
            )}
          >
            <UserCircle size={16} weight="bold" />
            <span className="hidden sm:inline">Staff</span>
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
          key={`${capture.student_id || capture.id_number || capture.entity_id}-${capture.timestamp || capture.created_at}-${index}`}
          capture={capture}
          onView={onView}
        />
      ))}
    </ul>
  )
}

function CaptureItem({ capture, onView }) {
  // Determine entity type from capture data
  const entityType = capture.entity_type || 'student'
  const config = ENTITY_CONFIG[entityType] || ENTITY_CONFIG.student

  return (
    <li
      onClick={() => onView(capture)}
      className="group flex items-center gap-3 p-3 rounded-xl cursor-pointer bg-navy-800/50 border border-navy-700/50 hover:bg-navy-800 hover:border-blue-600/50 transition-all hover:shadow-lg"
    >
      {/* Thumbnail */}
      <div className="w-14 h-14 rounded-lg border-2 border-navy-700 bg-navy-900 overflow-hidden shrink-0 group-hover:border-blue-500 transition-colors relative">
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
        {/* Entity Type Badge */}
        <div className={clsx(
          'absolute bottom-0 left-0 right-0 text-center text-[8px] font-bold uppercase py-0.5',
          config.bgClass, config.textClass
        )}>
          {entityType.charAt(0)}
        </div>
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className={clsx(
            'px-1.5 py-0.5 text-[9px] font-bold uppercase rounded',
            config.bgClass, config.textClass
          )}>
            {config.label}
          </span>
        </div>
        <p className="text-sm font-bold text-slate-100 group-hover:text-blue-400 transition-colors truncate font-mono mt-1">
          {capture.student_id || capture.id_number || capture.entity_id}
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

function EntityListContent({ items, entityType, onSelect, isEmpty, isLoading, searchQuery }) {
  const config = ENTITY_CONFIG[entityType] || ENTITY_CONFIG.student
  const Icon = config.icon

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-full py-12 px-6">
        <Spinner size="lg" />
        <p className="mt-6 text-sm text-slate-400">Loading {config.label.toLowerCase()}s...</p>
      </div>
    )
  }

  if (isEmpty) {
    return (
      <div className="flex flex-col items-center justify-center h-full py-12 px-6">
        <Icon size={80} className="text-slate-700" weight="thin" />
        <p className="mt-6 text-lg font-semibold text-slate-400">
          {searchQuery ? `No ${config.label.toLowerCase()}s found` : `No ${config.label.toLowerCase()}s in database`}
        </p>
        <p className="text-sm text-slate-600 mt-2 text-center">
          {searchQuery ? `No results for "${searchQuery}"` : `Import ${config.label.toLowerCase()}s to get started`}
        </p>
      </div>
    )
  }

  return (
    <ul className="p-3 space-y-2">
      {(Array.isArray(items) ? items : []).map((item) => (
        <EntityItem
          key={item.student_id || item.id_number || item.employee_id}
          item={item}
          entityType={entityType}
          onSelect={onSelect}
        />
      ))}
    </ul>
  )
}

function EntityItem({ item, entityType, onSelect }) {
  const config = ENTITY_CONFIG[entityType] || ENTITY_CONFIG.student
  const Icon = config.icon
  const itemId = item.student_id || item.id_number || item.employee_id

  return (
    <li className="group flex items-center gap-3 p-3 rounded-xl bg-navy-800/50 border border-navy-700/50 hover:bg-navy-800 hover:border-blue-600/50 transition-all">
      {/* Entity Icon */}
      <div className={clsx(
        'w-10 h-10 rounded-lg bg-navy-900 border-2 flex items-center justify-center transition-colors shrink-0',
        entityType === 'student' ? 'border-blue-700 text-blue-400 group-hover:border-blue-500' :
        entityType === 'teacher' ? 'border-green-700 text-green-400 group-hover:border-green-500' :
        'border-yellow-700 text-yellow-400 group-hover:border-yellow-500'
      )}>
        <Icon size={20} weight="bold" />
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-bold text-slate-100 font-mono">
          {itemId}
        </p>
        <p className="text-sm text-slate-300 truncate">{item.full_name}</p>
        {(item.section || item.department) && (
          <p className="text-xs text-slate-500 mt-0.5">{item.section || item.department}</p>
        )}
      </div>

      {/* Select Button */}
      <button
        onClick={() => onSelect(item)}
        className={clsx(
          'px-3 py-1.5 text-white text-xs font-bold rounded-lg transition-all flex items-center gap-1.5 hover:shadow-lg hover:scale-105',
          entityType === 'student' ? 'bg-blue-600 hover:bg-blue-700' :
          entityType === 'teacher' ? 'bg-green-600 hover:bg-green-700' :
          'bg-yellow-600 hover:bg-yellow-700'
        )}
      >
        <Check size={14} weight="bold" />
        Select
      </button>
    </li>
  )
}

function ManualFormContent({ entityType, manualData, onManualChange }) {
  const config = ENTITY_CONFIG[entityType] || ENTITY_CONFIG.student

  // Student form
  if (entityType === 'student') {
    return (
      <div className="p-5 space-y-4">
        <div className="space-y-1 mb-6">
          <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wide flex items-center gap-2">
            <Student size={16} className="text-blue-400" />
            Student Information
          </h3>
          <p className="text-xs text-slate-500">Enter student details manually</p>
        </div>

        <Input
          label="ID Number"
          value={manualData.id_number || ''}
          onChange={(e) => onManualChange('id_number', e.target.value)}
          placeholder="e.g., 2025-208"
          required
        />

        <Input
          label="Full Name"
          value={manualData.full_name || ''}
          onChange={(e) => onManualChange('full_name', e.target.value)}
          placeholder="e.g., Juan Dela Cruz"
          required
        />

        <Input
          label="LRN Number"
          value={manualData.lrn_number || ''}
          onChange={(e) => onManualChange('lrn_number', e.target.value)}
          placeholder="e.g., 123456789012"
        />

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Grade Level"
            value={manualData.grade_level || ''}
            onChange={(e) => onManualChange('grade_level', e.target.value)}
            placeholder="e.g., Grade 7"
          />
          <Input
            label="Section"
            value={manualData.section || ''}
            onChange={(e) => onManualChange('section', e.target.value)}
            placeholder="e.g., Einstein"
          />
        </div>

        <div className="pt-4 border-t border-navy-700">
          <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wide mb-4">Guardian Information</h3>

          <div className="space-y-4">
            <Input
              label="Guardian Name"
              value={manualData.guardian_name || ''}
              onChange={(e) => onManualChange('guardian_name', e.target.value)}
              placeholder="Parent/Guardian name"
            />

            <Input
              label="Contact Number"
              value={manualData.contact_number || ''}
              onChange={(e) => onManualChange('contact_number', e.target.value)}
              placeholder="e.g., 09123456789"
            />

            <Input
              label="Address"
              value={manualData.address || ''}
              onChange={(e) => onManualChange('address', e.target.value)}
              placeholder="Complete address"
            />
          </div>
        </div>
      </div>
    )
  }

  // Teacher form
  if (entityType === 'teacher') {
    return (
      <div className="p-5 space-y-4">
        <div className="space-y-1 mb-6">
          <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wide flex items-center gap-2">
            <Chalkboard size={16} className="text-green-400" />
            Teacher Information
          </h3>
          <p className="text-xs text-slate-500">Enter teacher details manually</p>
        </div>

        <Input
          label="Employee ID"
          value={manualData.employee_id || ''}
          onChange={(e) => onManualChange('employee_id', e.target.value)}
          placeholder="e.g., EMP-2024-001"
          required
        />

        <Input
          label="Full Name"
          value={manualData.full_name || ''}
          onChange={(e) => onManualChange('full_name', e.target.value)}
          placeholder="e.g., Dr. Maria Santos"
          required
        />

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Department"
            value={manualData.department || ''}
            onChange={(e) => onManualChange('department', e.target.value)}
            placeholder="e.g., Science Dept"
          />
          <Input
            label="Position"
            value={manualData.position || ''}
            onChange={(e) => onManualChange('position', e.target.value)}
            placeholder="e.g., Senior Teacher"
          />
        </div>

        <Input
          label="Specialization"
          value={manualData.specialization || ''}
          onChange={(e) => onManualChange('specialization', e.target.value)}
          placeholder="e.g., Physics"
        />

        <Input
          label="Contact Number"
          value={manualData.contact_number || ''}
          onChange={(e) => onManualChange('contact_number', e.target.value)}
          placeholder="e.g., 09123456789"
        />

        <div className="pt-4 border-t border-navy-700">
          <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wide mb-4">Emergency Contact</h3>

          <div className="space-y-4">
            <Input
              label="Emergency Contact Name"
              value={manualData.emergency_contact_name || ''}
              onChange={(e) => onManualChange('emergency_contact_name', e.target.value)}
              placeholder="Contact person name"
            />

            <Input
              label="Emergency Contact Number"
              value={manualData.emergency_contact_number || ''}
              onChange={(e) => onManualChange('emergency_contact_number', e.target.value)}
              placeholder="e.g., 09123456789"
            />

            <Input
              label="Address"
              value={manualData.address || ''}
              onChange={(e) => onManualChange('address', e.target.value)}
              placeholder="Complete address"
            />
          </div>
        </div>
      </div>
    )
  }

  // Staff form
  return (
    <div className="p-5 space-y-4">
      <div className="space-y-1 mb-6">
        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wide flex items-center gap-2">
          <UserCircle size={16} className="text-yellow-400" />
          Staff Information
        </h3>
        <p className="text-xs text-slate-500">Enter staff details manually</p>
      </div>

      <Input
        label="Employee ID"
        value={manualData.employee_id || ''}
        onChange={(e) => onManualChange('employee_id', e.target.value)}
        placeholder="e.g., STAFF-2024-001"
        required
      />

      <Input
        label="Full Name"
        value={manualData.full_name || ''}
        onChange={(e) => onManualChange('full_name', e.target.value)}
        placeholder="e.g., Roberto Carlos"
        required
      />

      <div className="grid grid-cols-2 gap-4">
        <Input
          label="Department"
          value={manualData.department || ''}
          onChange={(e) => onManualChange('department', e.target.value)}
          placeholder="e.g., Admin Office"
        />
        <Input
          label="Position"
          value={manualData.position || ''}
          onChange={(e) => onManualChange('position', e.target.value)}
          placeholder="e.g., Clerk III"
        />
      </div>

      <Input
        label="Contact Number"
        value={manualData.contact_number || ''}
        onChange={(e) => onManualChange('contact_number', e.target.value)}
        placeholder="e.g., 09123456789"
      />

      <div className="pt-4 border-t border-navy-700">
        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wide mb-4">Emergency Contact</h3>

        <div className="space-y-4">
          <Input
            label="Emergency Contact Name"
            value={manualData.emergency_contact_name || ''}
            onChange={(e) => onManualChange('emergency_contact_name', e.target.value)}
            placeholder="Contact person name"
          />

          <Input
            label="Emergency Contact Number"
            value={manualData.emergency_contact_number || ''}
            onChange={(e) => onManualChange('emergency_contact_number', e.target.value)}
            placeholder="e.g., 09123456789"
          />

          <Input
            label="Address"
            value={manualData.address || ''}
            onChange={(e) => onManualChange('address', e.target.value)}
            placeholder="Complete address"
          />
        </div>
      </div>
    </div>
  )
}
