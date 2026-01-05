import { useState, useRef } from 'react'
import { clsx } from 'clsx'
import {
  UploadSimple,
  FileArrowUp,
  CheckCircle,
  XCircle,
  Table,
  FileXls,
  FileCsv,
  Spinner as SpinnerIcon,
} from '@phosphor-icons/react'
import { Button, Card, Spinner } from '../shared'
import { useToast } from '../../contexts/ToastContext'
import { authenticatedFetch } from '../../services/api'

export default function ImportDataSection({ onImportComplete }) {
  const [isOpen, setIsOpen] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [isPreviewLoading, setIsPreviewLoading] = useState(false)
  const [isImporting, setIsImporting] = useState(false)
  const [importResult, setImportResult] = useState(null)
  const fileInputRef = useRef(null)
  const toast = useToast()

  const handleFileSelect = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    if (!file.name.endsWith('.csv') && !file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
      toast.error('Invalid File', 'Please select a CSV or Excel file')
      return
    }

    setSelectedFile(file)
    setImportResult(null)
    await loadPreview(file)
  }

  const loadPreview = async (file) => {
    setIsPreviewLoading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)

      const data = await authenticatedFetch('/api/students/import/preview', {
        method: 'POST',
        body: formData,
      })

      setPreview(data)
        
      if (!data.valid) {
        toast.warning('Missing Columns', `Missing: ${data.missing_columns.join(', ')}`)
      }
    } catch (err) {
      console.error('Preview error:', err)
      toast.error('Preview Failed', 'Could not load file preview')
      setSelectedFile(null)
    } finally {
      setIsPreviewLoading(false)
    }
  }

  const handleImport = async () => {
    if (!selectedFile || !preview?.valid) return

    setIsImporting(true)
    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      const data = await authenticatedFetch('/api/students/import', {
        method: 'POST',
        body: formData,
      })

      setImportResult(data)
        
      if (data.errors && data.errors.length > 0) {
        toast.warning('Import Complete with Errors', `${data.imported} imported, ${data.errors.length} errors`)
      } else {
        toast.success('Import Complete', `Successfully imported ${data.imported} students`)
      }
        
      if (onImportComplete) onImportComplete()
    } catch (err) {
      console.error('Import error:', err)
      toast.error('Import Failed', 'An error occurred during import')
    } finally {
      setIsImporting(false)
    }
  }

  const handleReset = () => {
    setSelectedFile(null)
    setPreview(null)
    setImportResult(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <Card className="mb-5 overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full h-14 px-5 flex items-center justify-between hover:bg-navy-850 transition-colors"
      >
        <span className="text-base font-bold uppercase text-slate-300 tracking-wide">IMPORT DATA</span>
        <div className="flex items-center gap-2">
          <FileArrowUp size={20} className="text-blue-500" />
        </div>
      </button>
      
      {isOpen && (
        <div className="px-5 pb-5 border-t border-navy-800 pt-5 animate-slide-down">
          <div className="space-y-5">
            <p className="text-sm text-slate-400">
              Import student or teacher data from CSV or Excel files. 
              Required columns: ID_Number, Full_Name, LRN, Section, Guardian_Name, Address, Guardian_Contact
            </p>

            {/* File Upload Area */}
            {!selectedFile && (
              <div
                onClick={() => fileInputRef.current?.click()}
                className={clsx(
                  'border-2 border-dashed rounded-lg p-8 cursor-pointer transition-all',
                  'hover:border-blue-500 hover:bg-blue-500/5',
                  'border-navy-600'
                )}
              >
                <div className="text-center">
                  <UploadSimple size={48} className="mx-auto text-slate-600 mb-3" />
                  <p className="text-sm font-medium text-slate-300 mb-1">
                    Click to upload or drag and drop
                  </p>
                  <p className="text-xs text-slate-600">
                    CSV or Excel files (XLS, XLSX) only
                  </p>
                </div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  onChange={handleFileSelect}
                  className="hidden"
                />
              </div>
            )}

            {/* File Info */}
            {selectedFile && (
              <div className="p-4 bg-navy-850 border border-navy-700 rounded-lg">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    {selectedFile.name.endsWith('.csv') ? (
                      <FileCsv size={32} className="text-green-400" />
                    ) : (
                      <FileXls size={32} className="text-green-400" />
                    )}
                    <div>
                      <p className="text-sm font-medium text-slate-200">{selectedFile.name}</p>
                      <p className="text-xs text-slate-600">
                        {(selectedFile.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={handleReset}
                    className="text-slate-500 hover:text-red-400 transition-colors"
                  >
                    <XCircle size={24} />
                  </button>
                </div>

                {/* Preview Loading */}
                {isPreviewLoading && (
                  <div className="text-center py-4">
                    <Spinner size="md" />
                    <p className="text-sm text-slate-500 mt-2">Loading preview...</p>
                  </div>
                )}

                {/* Preview Data */}
                {preview && !isPreviewLoading && (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-400">Total Rows:</span>
                      <span className="font-mono text-slate-200">{preview.total_rows}</span>
                    </div>
                    
                    {!preview.valid && (
                      <div className="p-3 bg-red-900/20 border border-red-700 rounded-lg">
                        <div className="flex items-start gap-2">
                          <XCircle size={20} className="text-red-400 shrink-0 mt-0.5" />
                          <div>
                            <p className="text-sm font-medium text-red-300 mb-1">Missing Required Columns</p>
                            <p className="text-xs text-red-400">{preview.missing_columns.join(', ')}</p>
                          </div>
                        </div>
                      </div>
                    )}

                    {preview.valid && (
                      <div className="p-3 bg-green-900/20 border border-green-700 rounded-lg">
                        <div className="flex items-center gap-2">
                          <CheckCircle size={20} className="text-green-400" />
                          <span className="text-sm text-green-300">File is valid and ready to import</span>
                        </div>
                      </div>
                    )}

                    {/* Preview Table */}
                    {preview.preview_data && preview.preview_data.length > 0 && (
                      <div className="mt-4">
                        <p className="text-xs font-semibold text-slate-500 uppercase mb-2">Preview (First 10 rows)</p>
                        <div className="overflow-x-auto border border-navy-700 rounded-lg">
                          <table className="w-full text-xs">
                            <thead className="bg-navy-800">
                              <tr>
                                {preview.headers.slice(0, 5).map((header, idx) => (
                                  <th key={idx} className="px-3 py-2 text-left text-slate-400 font-medium">
                                    {header}
                                  </th>
                                ))}
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-navy-800">
                              {preview.preview_data.slice(0, 5).map((row, idx) => (
                                <tr key={idx} className="hover:bg-navy-850">
                                  {preview.headers.slice(0, 5).map((header, colIdx) => (
                                    <td key={colIdx} className="px-3 py-2 text-slate-300">
                                      {String(row[header] || '')}
                                    </td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Import Result */}
                {importResult && (
                  <div className="mt-4 p-4 bg-navy-900 border border-navy-700 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <CheckCircle size={20} className="text-green-400" />
                      <p className="text-sm font-semibold text-green-300">Import Complete</p>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div>
                        <span className="text-slate-500">Imported:</span>
                        <span className="ml-2 text-green-400 font-mono">{importResult.imported}</span>
                      </div>
                      <div>
                        <span className="text-slate-500">Total:</span>
                        <span className="ml-2 text-slate-300 font-mono">{importResult.total}</span>
                      </div>
                    </div>
                    {importResult.errors && importResult.errors.length > 0 && (
                      <div className="mt-2 p-2 bg-red-900/20 rounded text-xs text-red-400">
                        {importResult.errors.length} errors occurred (first 10 shown)
                      </div>
                    )}
                  </div>
                )}

                {/* Action Buttons */}
                {preview && !importResult && (
                  <div className="flex gap-3 mt-4">
                    <Button
                      variant="primary"
                      icon={FileArrowUp}
                      onClick={handleImport}
                      disabled={!preview.valid || isImporting}
                      loading={isImporting}
                      className="flex-1"
                    >
                      {isImporting ? 'Importing...' : 'Import Data'}
                    </Button>
                    <Button
                      variant="ghost"
                      onClick={handleReset}
                      disabled={isImporting}
                    >
                      Cancel
                    </Button>
                  </div>
                )}

                {importResult && (
                  <div className="mt-4">
                    <Button
                      variant="secondary"
                      onClick={handleReset}
                      className="w-full"
                    >
                      Import Another File
                    </Button>
                  </div>
                )}
              </div>
            )}

            {/* Download Template */}
            <div className="pt-3 border-t border-navy-800">
              <p className="text-xs text-slate-600 mb-2">Need a template?</p>
              <a
                href="/students.csv"
                download="students_template.csv"
                className="inline-flex items-center gap-2 text-sm text-blue-400 hover:text-blue-300 transition-colors"
              >
                <FileCsv size={16} />
                Download CSV Template
              </a>
            </div>
          </div>
        </div>
      )}
    </Card>
  )
}
