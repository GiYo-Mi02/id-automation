import { useState } from 'react'
import {
  MagnifyingGlass,
  Eye,
  ArrowsClockwise,
  CheckCircle,
  XCircle,
  CaretLeft,
  CaretRight
} from '@phosphor-icons/react'
import { Card, Badge } from '../shared'
import { formatDistanceToNow } from '../utils/formatTime'

export default function StudentTable({ students, isLoading, onRefresh, onEdit, onView, onRegenerate }) {
  const [searchQuery, setSearchQuery] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 10

  const filteredStudents = students.filter(student => {
    if (!searchQuery) return true
    const query = searchQuery.toLowerCase()
    const studentId = student.student_id || student.id_number
    return (
      studentId?.toLowerCase().includes(query) ||
      student.full_name?.toLowerCase().includes(query)
    )
  })

  // Pagination calculations
  const totalPages = Math.ceil(filteredStudents.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const paginatedStudents = filteredStudents.slice(startIndex, endIndex)

  // Reset to page 1 when search changes
  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value)
    setCurrentPage(1)
  }

  return (
    <Card className="h-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="px-5 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/30">
        <h2 className="text-sm font-bold text-slate-300">RECENT ACTIVITY</h2>
        
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
              paginatedStudents.map((student) => (
                <tr key={student.id || student.student_id} className="group hover:bg-slate-800/30 transition-colors">
                  <td className="px-5 py-2">
                    {student.front_image ? (
                        <Badge variant="success" icon={CheckCircle} className="py-0.5 px-2 text-[10px]">Success</Badge>
                    ) : (
                        <Badge variant="error" icon={XCircle} className="py-0.5 px-2 text-[10px]">Failed</Badge>
                    )}
                  </td>
                  <td className="px-5 py-2 text-xs text-slate-400 font-mono">
                    {formatDistanceToNow(student.created_at || student.timestamp)}
                  </td>
                  <td className="px-5 py-2 text-xs text-slate-300 font-mono">
                    {student.student_id || student.id_number}
                  </td>
                  <td className="px-5 py-2 text-sm font-medium text-slate-200">
                    {student.full_name}
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
      {filteredStudents.length > 0 && (
        <div className="px-5 py-3 border-t border-slate-800 flex items-center justify-between bg-slate-900/30">
          <div className="text-xs text-slate-500">
            Showing {startIndex + 1}-{Math.min(endIndex, filteredStudents.length)} of {filteredStudents.length} records
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
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
                    onClick={() => setCurrentPage(pageNum)}
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
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
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
