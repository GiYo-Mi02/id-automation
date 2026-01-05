import { useState } from 'react'
import { clsx } from 'clsx'
import {
  MagnifyingGlass,
  Eye,
  PencilSimple,
  ArrowsClockwise,
  DotsThree,
  Database,
} from '@phosphor-icons/react'
import { Card, Spinner, Dropdown } from '../shared'
import { formatTime, formatDistanceToNow } from '../utils/formatTime'

const filterOptions = [
  { value: 'today', label: 'Today' },
  { value: 'week', label: 'This Week' },
  { value: 'month', label: 'This Month' },
  { value: 'all', label: 'All Time' },
]

export default function StudentTable({ students, isLoading, onRefresh, onEdit, onView, onRegenerate }) {
  const [searchQuery, setSearchQuery] = useState('')
  const [filter, setFilter] = useState('today')

  const filteredStudents = students.filter(student => {
    if (!searchQuery) return true
    const query = searchQuery.toLowerCase()
    const studentId = student.student_id || student.id_number
    return (
      studentId?.toLowerCase().includes(query) ||
      student.full_name?.toLowerCase().includes(query)
    )
  })

  return (
    <Card className="overflow-hidden">
      {/* Header */}
      <div className="h-14 px-6 flex items-center justify-between border-b border-navy-700 bg-gradient-to-r from-navy-850 to-navy-900">
        <h2 className="text-base font-bold text-slate-300">RECENT GENERATIONS (Last 50)</h2>
        
        <div className="flex items-center gap-3">
          {/* Filter */}
          <Dropdown
            value={filter}
            onChange={setFilter}
            options={filterOptions}
            className="w-36"
          />

          {/* Search */}
          <div className="relative">
            <MagnifyingGlass
              size={14}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
            />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search..."
              className="h-9 w-48 pl-9 pr-3 bg-navy-800 border border-navy-700 rounded-md text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="max-h-[500px] overflow-y-auto">
        <table className="w-full">
          <thead className="sticky top-0 z-10 bg-navy-900 border-b-2 border-navy-700">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-bold uppercase text-slate-500 tracking-wider w-[15%]">
                Time
              </th>
              <th className="px-6 py-3 text-left text-xs font-bold uppercase text-slate-500 tracking-wider w-[20%]">
                ID Number
              </th>
              <th className="px-6 py-3 text-left text-xs font-bold uppercase text-slate-500 tracking-wider w-[35%]">
                Student Name
              </th>
              <th className="px-6 py-3 text-right text-xs font-bold uppercase text-slate-500 tracking-wider w-[30%]">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-navy-800">
            {isLoading ? (
              <tr>
                <td colSpan={4} className="py-16 text-center">
                  <Spinner size="lg" className="mx-auto" />
                  <p className="mt-4 text-sm text-slate-500">Loading students...</p>
                </td>
              </tr>
            ) : filteredStudents.length === 0 ? (
              <tr>
                <td colSpan={4}>
                  <EmptyState />
                </td>
              </tr>
            ) : (
              filteredStudents.map((student, index) => (
                <StudentRow
                  key={(student.student_id || student.id_number) + (student.timestamp || student.created_at || index)}
                  student={student}
                  onEdit={onEdit}
                  onView={onView}
                  onRegenerate={onRegenerate}
                />
              ))
            )}
          </tbody>
        </table>
      </div>
    </Card>
  )
}

function StudentRow({ student, onEdit, onView, onRegenerate }) {
  const studentId = student.student_id || student.id_number
  const timestamp = student.timestamp || student.created_at
  
  return (
    <tr className="group hover:bg-navy-800/50 transition-colors">
      <td className="px-6 py-4 text-sm text-slate-600 font-mono">
        {formatTime(timestamp)}
      </td>
      <td className="px-6 py-4 text-sm font-bold text-slate-200 group-hover:text-blue-400 transition-colors">
        {studentId}
      </td>
      <td className="px-6 py-4 text-sm text-slate-400 truncate max-w-[300px]">
        {student.full_name}
      </td>
      <td className="px-6 py-4">
        <div className="flex items-center justify-end gap-2">
          {/* View */}
          <button
            onClick={() => onView(student)}
            className="w-8 h-8 flex items-center justify-center rounded-md bg-blue-900/30 border border-blue-800 text-blue-400 hover:bg-blue-900/50 hover:scale-105 transition-all"
            title="View IDs"
          >
            <Eye size={16} />
          </button>

          {/* Edit */}
          <button
            onClick={() => onEdit(student)}
            className="w-8 h-8 flex items-center justify-center rounded-md bg-navy-800 border border-navy-700 text-slate-400 hover:bg-navy-700 hover:text-slate-200 transition-colors"
            title="Edit Student"
          >
            <PencilSimple size={16} />
          </button>

          {/* Regenerate */}
          <button
            onClick={() => onRegenerate(student)}
            className="w-8 h-8 flex items-center justify-center rounded-md bg-navy-800 border border-navy-700 text-slate-400 hover:bg-navy-700 hover:text-slate-200 transition-colors"
            title="Regenerate ID"
          >
            <ArrowsClockwise size={16} />
          </button>
        </div>
      </td>
    </tr>
  )
}

function EmptyState() {
  return (
    <div className="py-16 text-center">
      <Database size={48} className="mx-auto text-slate-700" weight="thin" />
      <p className="mt-4 text-sm text-slate-500">No generations yet</p>
      <p className="text-xs text-slate-600">Captures will appear here</p>
    </div>
  )
}
