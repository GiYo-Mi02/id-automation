import { useState } from 'react'
import { DownloadSimple } from '@phosphor-icons/react'
import { Button } from '../shared'
import { useToast } from '../../contexts/ToastContext'

export default function ExportDataSection() {
  const [isExporting, setIsExporting] = useState(false)
  const toast = useToast()

  const handleExport = async () => {
    setIsExporting(true)
    try {
      const response = await fetch('/api/students/export', {
        method: 'GET',
        headers: {
          'X-API-Key': import.meta.env.VITE_API_KEY || '',
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const blob = await response.blob()
      const downloadUrl = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = downloadUrl
      a.download = `students_export_${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(downloadUrl)

      toast.success('Export Successful', 'Student database exported to CSV')
    } catch (err) {
      console.error('Export error:', err)
      toast.error('Export Failed', err.message || 'Could not export student database')
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h4 className="text-sm font-semibold text-slate-200">Student Database Export</h4>
          <p className="text-xs text-slate-500 mt-1">
            Download all student records (LRN, grade levels, sections, and emergency contact details) in a single CSV file.
          </p>
        </div>
        <Button
          onClick={handleExport}
          loading={isExporting}
          icon={DownloadSimple}
          variant="secondary"
          className="shrink-0 ml-4"
        >
          Export to CSV
        </Button>
      </div>
    </div>
  )
}
