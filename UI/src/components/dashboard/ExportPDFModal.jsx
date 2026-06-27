import { useState, useEffect } from 'react'
import { FilePdf, CaretDown, DownloadSimple, X, Archive } from '@phosphor-icons/react'
import { Modal, Button } from '../shared'

export default function ExportPDFModal({ isOpen, onClose, schools = [], onExport, defaultSchool = '' }) {
  const [selectedSchool, setSelectedSchool] = useState('All Schools')
  const [selectedSide, setSelectedSide] = useState('front')
  const [selectedFormat, setSelectedFormat] = useState('zip') // 'zip' | 'pdf'
  const [isExporting, setIsExporting] = useState(false)

  // Reset selection on open
  useEffect(() => {
    if (isOpen) {
      setSelectedSchool(defaultSchool || 'All Schools')
      setSelectedSide('front')
      setSelectedFormat('zip')
      setIsExporting(false)
    }
  }, [isOpen, defaultSchool])

  const handleExport = async () => {
    setIsExporting(true)
    try {
      await onExport(selectedSchool, selectedSide, selectedFormat)
      onClose()
    } catch (err) {
      console.error(err)
    } finally {
      setIsExporting(false)
    }
  }

  const footer = (
    <div className="flex justify-end gap-3">
      <Button variant="secondary" onClick={onClose} disabled={isExporting}>
        Cancel
      </Button>
      <Button
        variant="success"
        icon={DownloadSimple}
        loading={isExporting}
        onClick={handleExport}
        disabled={!selectedSchool || isExporting}
      >
        Export {selectedFormat.toUpperCase()}
      </Button>
    </div>
  )

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Export Compiled IDs"
      icon={selectedFormat === 'zip' ? Archive : FilePdf}
      size="sm"
      footer={footer}
    >
      <div className="space-y-4 py-2 text-slate-200">
        <p className="text-xs text-slate-400 leading-relaxed">
          Select school, ID card side, and export format. ZIP folders preserve raw PNG files for borderless printing in Windows.
        </p>

        <div className="flex flex-col gap-2">
          <label className="text-xs font-semibold text-slate-300">Select School</label>
          <div className="relative">
            <select
              value={selectedSchool}
              onChange={(e) => setSelectedSchool(e.target.value)}
              className="w-full h-10 pl-3 pr-10 bg-slate-950 border border-slate-800 rounded-md text-xs text-slate-200 focus:outline-none focus:border-blue-500 transition-colors appearance-none cursor-pointer"
            >
              <option value="All Schools">All Schools</option>
              {schools.map(school => (
                <option key={school} value={school}>
                  {school}
                </option>
              ))}
            </select>
            <CaretDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
          </div>
        </div>

        <div className="flex flex-col gap-2">
          <label className="text-xs font-semibold text-slate-300">Export Format</label>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setSelectedFormat('zip')}
              className={`flex-1 h-10 rounded-md text-xs font-semibold transition-all cursor-pointer border ${
                selectedFormat === 'zip'
                  ? 'bg-blue-600 border-blue-600 text-white shadow-sm shadow-blue-900/50'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              ZIP Folder (Borderless)
            </button>
            <button
              type="button"
              onClick={() => setSelectedFormat('pdf')}
              className={`flex-1 h-10 rounded-md text-xs font-semibold transition-all cursor-pointer border ${
                selectedFormat === 'pdf'
                  ? 'bg-blue-600 border-blue-600 text-white shadow-sm shadow-blue-900/50'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              Single PDF File
            </button>
          </div>
        </div>

        <div className="flex flex-col gap-2">
          <label className="text-xs font-semibold text-slate-300">ID Card Side</label>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setSelectedSide('front')}
              className={`flex-1 h-10 rounded-md text-xs font-semibold transition-all cursor-pointer border ${
                selectedSide === 'front'
                  ? 'bg-blue-600 border-blue-600 text-white shadow-sm shadow-blue-900/50'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              Front ID
            </button>
            <button
              type="button"
              onClick={() => setSelectedSide('back')}
              className={`flex-1 h-10 rounded-md text-xs font-semibold transition-all cursor-pointer border ${
                selectedSide === 'back'
                  ? 'bg-blue-600 border-blue-600 text-white shadow-sm shadow-blue-900/50'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              Back ID
            </button>
          </div>
        </div>
      </div>
    </Modal>
  )
}
