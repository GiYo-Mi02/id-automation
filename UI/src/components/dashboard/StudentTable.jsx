import { useState, useEffect } from 'react'
import {
  MagnifyingGlass,
  Eye,
  ArrowsClockwise,
  CheckCircle,
  XCircle,
  CaretLeft,
  CaretRight,
  CaretDown
} from '@phosphor-icons/react'
import { Card, Badge } from '../shared'
import { formatDistanceToNow } from '../utils/formatTime'

export default function StudentTable({ 
  students, 
  isLoading, 
  totalStudents,
  currentPage,
  onPageChange,
  sortBy,
  sortOrder,
  onSortChange,
  filterSection,
  onFilterChange,
  onRefresh, 
  onEdit, 
  onView, 
  onRegenerate 
}) {
  const [searchQuery, setSearchQuery] = useState('')
  const itemsPerPage = 50

  // Defensive: Ensure students is always an array
  const safeStudents = Array.isArray(students) ? students : []
  
  // Get unique sections for filter
  const allSections = [...new Set(safeStudents.map(s => s.section).filter(Boolean))]
  
  const filteredStudents = safeStudents.filter(student => {
    if (!searchQuery) return true
    const query = searchQuery.toLowerCase()
    const studentId = student.student_id || student.id_number
    return (
      studentId?.toLowerCase().includes(query) ||
      student.full_name?.toLowerCase().includes(query)
    )
  })

  // Calculate total pages based on total students from backend
  const totalPages = Math.ceil((totalStudents || 0) / itemsPerPage)

  // Reset to page 1 when search changes
  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value)
    if (onPageChange) {
      onPageChange(1)
    }
  }
  
  const handleSortChange = (e) => {
    const value = e.target.value
    const [newSortBy, newSortOrder] = value.split('_')
    if (onSortChange) {
      onSortChange(newSortBy, newSortOrder)
    }
  }
  
  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages && onPageChange) {
      onPageChange(newPage)
    }
  }

  return (
    <Card className="h-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="px-5 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/30">
        <h2 className="text-sm font-bold text-slate-300">RECENT ACTIVITY</h2>
        
        <div className="flex items-center gap-3">
          {/* Sort Dropdown */}
          <div className="relative">
            <select
              value={`${sortBy}_${sortOrder}`}
              onChange={handleSortChange}
              className="h-8 pl-3 pr-8 bg-slate-950 border border-slate-800 rounded-md text-xs text-slate-200 focus:outline-none focus:border-blue-500 transition-colors appearance-none cursor-pointer"
            >
              <option value="created_at_DESC">Latest First</option>
              <option value="created_at_ASC">Oldest First</option>
              <option value="id_number_ASC">ID Number</option>
              <option value="section_ASC">Section</option>
              <option value="full_name_ASC">Name A-Z</option>
            </select>
            <CaretDown size={12} className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
          </div>
          
          {/* Section Filter */}
          {allSections.length > 0 && (
            <div className="relative">
              <select
                value={filterSection || ''}
                onChange={(e) => onFilterChange && onFilterChange(e.target.value)}
                className="h-8 pl-3 pr-8 bg-slate-950 border border-slate-800 rounded-md text-xs text-slate-200 focus:outline-none focus:border-blue-500 transition-colors appearance-none cursor-pointer"
              >
                <option value="">All Sections</option>
                {allSections.map(section => (
                  <option key={section} value={section}>{section}</option>
                ))}
              </select>
              <CaretDown size={12} className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
            </div>
          )}
          
          {/* Search */}
          <div className="relative">
              <MagnifyingGlass
                size={14}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
              />
              <input
                type="text"
                value={searchQuery}
                onChange={handleSearchChange}
                placeholder="Search history..."
                className="h-8 w-64 pl-9 pr-3 bg-slate-950 border border-slate-800 rounded-md text-xs text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-blue-500 transition-colors"
              />
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-y-auto">
        <table className="w-full text-left border-collapse">
          <thead className="sticky top-0 z-10 bg-slate-900 border-b border-slate-800">
            <tr>
              <th className="px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider w-[15%]">Status</th>
              <th className="px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider w-[20%]">Time</th>
              <th className="px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider w-[20%]">ID Number</th>
              <th className="px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider w-[25%]">Student Name</th>
              <th className="px-5 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider w-[20%]">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {isLoading ? (
              <tr>
                <td colSpan={5} className="py-12 text-center text-slate-500 text-sm">
                  Loading records...
                </td>
              </tr>
            ) : filteredStudents.length === 0 ? (
              <tr>
                <td colSpan={5} className="py-12 text-center text-slate-500 text-sm">
                  No recent activity found.
                </td>
              </tr>
            ) : (
              filteredStudents.map((student, index) => (
                <tr key={student.id_number || student.student_id || student.id || `student-${index}`} className="group hover:bg-slate-800/30 transition-colors">
                  <td className="px-5 py-2">
                    {student.front_image || student.file_path ? (
                        <Badge variant="success" icon={CheckCircle} className="py-0.5 px-2 text-[10px]">Generated</Badge>
                    ) : (
                        <Badge variant="info" className="py-0.5 px-2 text-[10px]">Ready</Badge>
                    )}
                  </td>
                  <td className="px-5 py-2 text-xs text-slate-400 font-mono">
                    {student.created_at || student.timestamp ? formatDistanceToNow(student.created_at || student.timestamp) : 'N/A'}
                  </td>
                  <td className="px-5 py-2 text-xs text-slate-300 font-mono">
                    {student.id_number || student.student_id}
                  </td>
                  <td className="px-5 py-2 text-sm font-medium text-slate-200">
                    {student.full_name}
                    {student.section && <span className="ml-2 text-xs text-slate-500">({student.section})</span>}
                  </td>
                  <td className="px-5 py-2 text-right">
                    <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button 
                            onClick={() => onView(student)}
                            className="p-1.5 rounded hover:bg-slate-700 text-slate-400 hover:text-blue-400 transition-colors"
                            title="View Details"
                        >
                            <Eye size={16} />
                        </button>
                        <button 
                            onClick={() => onRegenerate(student)}
                            className="p-1.5 rounded hover:bg-slate-700 text-slate-400 hover:text-amber-400 transition-colors"
                            title="Reprint"
                        >
                            <ArrowsClockwise size={16} />
                        </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      {totalStudents > 0 && (
        <div className="px-5 py-3 border-t border-slate-800 flex items-center justify-between bg-slate-900/30">
          <div className="text-xs text-slate-500">
            Showing {((currentPage - 1) * itemsPerPage) + 1}-{Math.min(currentPage * itemsPerPage, totalStudents)} of {totalStudents} records
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
              title="Previous Page"
            >
              <CaretLeft size={16} weight="bold" />
            </button>
            <div className="flex items-center gap-1">
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                let pageNum
                if (totalPages <= 5) {
                  pageNum = i + 1
                } else if (currentPage <= 3) {
                  pageNum = i + 1
                } else if (currentPage >= totalPages - 2) {
                  pageNum = totalPages - 4 + i
                } else {
                  pageNum = currentPage - 2 + i
                }
                return (
                  <button
                    key={pageNum}
                    onClick={() => handlePageChange(pageNum)}
                    className={`w-8 h-8 rounded text-xs font-medium transition-colors ${
                      currentPage === pageNum
                        ? 'bg-blue-500 text-white'
                        : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                    }`}
                  >
                    {pageNum}
                  </button>
                )
              })}
            </div>
            <button
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
              title="Next Page"
            >
              <CaretRight size={16} weight="bold" />
            </button>
          </div>
        </div>
      )}
    </Card>
  )
}
