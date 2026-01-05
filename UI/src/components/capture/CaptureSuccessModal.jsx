import { Modal } from '../shared'
import { CheckCircle, X, Eye } from '@phosphor-icons/react'

export default function CaptureSuccessModal({ isOpen, onClose, captureData }) {
  if (!captureData) return null

  const handleClose = () => {
    console.log('CaptureSuccessModal: Closing modal')
    onClose()
  }

  return (
    <Modal isOpen={isOpen} onClose={handleClose} size="xl" showClose={false} closeOnOverlay={true} closeOnEscape={true}>
      {/* Success Header */}
      <div className="text-center mb-6">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-500/20 border-2 border-green-500 mb-4">
          <CheckCircle size={32} className="text-green-400" weight="fill" />
        </div>
        <h2 className="text-2xl font-bold text-slate-100 mb-2">ID Card Generated!</h2>
        <p className="text-sm text-slate-400">
          Successfully created ID for <span className="text-slate-200 font-semibold">{captureData.full_name || captureData.student_id}</span>
        </p>
      </div>

      {/* ID Cards Preview */}
      <div className="flex flex-col lg:flex-row items-center justify-center gap-8 py-4">
        {/* Front ID */}
        <div className="text-center">
          <p className="text-xs font-bold uppercase text-slate-500 tracking-widest mb-3">Front</p>
          <div className="relative group">
            <img
              src={captureData.front_image || captureData.front_url}
              alt="Front ID"
              className="max-h-[50vh] w-auto rounded-xl border-2 border-navy-700 shadow-2xl hover:scale-[1.02] transition-transform"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity rounded-xl flex items-end justify-center pb-4">
              <span className="text-white text-xs font-medium flex items-center gap-1">
                <Eye size={14} /> Click to view full size
              </span>
            </div>
          </div>
        </div>

        {/* Back ID */}
        <div className="text-center">
          <p className="text-xs font-bold uppercase text-slate-500 tracking-widest mb-3">Back</p>
          <div className="relative group">
            <img
              src={captureData.back_image || captureData.back_url}
              alt="Back ID"
              className="max-h-[50vh] w-auto rounded-xl border-2 border-navy-700 shadow-2xl hover:scale-[1.02] transition-transform"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity rounded-xl flex items-end justify-center pb-4">
              <span className="text-white text-xs font-medium flex items-center gap-1">
                <Eye size={14} /> Click to view full size
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Student Info */}
      <div className="mt-6 p-4 bg-navy-850 rounded-lg border border-navy-700">
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <span className="text-slate-500">ID Number:</span>
            <span className="ml-2 text-slate-200 font-mono">{captureData.id_number || captureData.student_id}</span>
          </div>
          <div>
            <span className="text-slate-500">Name:</span>
            <span className="ml-2 text-slate-200">{captureData.full_name || 'N/A'}</span>
          </div>
          {captureData.section && (
            <div>
              <span className="text-slate-500">Section:</span>
              <span className="ml-2 text-slate-200">{captureData.section}</span>
            </div>
          )}
          {captureData.lrn && (
            <div>
              <span className="text-slate-500">LRN:</span>
              <span className="ml-2 text-slate-200 font-mono">{captureData.lrn}</span>
            </div>
          )}
        </div>
      </div>

      {/* Close Button */}
      <div className="mt-6 flex justify-center">
        <button
          type="button"
          onClick={(e) => {
            e.preventDefault()
            e.stopPropagation()
            handleClose()
          }}
          className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors flex items-center gap-2"
        >
          <CheckCircle size={20} weight="bold" />
          Continue
        </button>
      </div>

      {/* Top-right close button */}
      <button
        type="button"
        onClick={(e) => {
          e.preventDefault()
          e.stopPropagation()
          handleClose()
        }}
        className="absolute top-4 right-4 w-10 h-10 flex items-center justify-center rounded-full bg-navy-800 border border-navy-700 text-slate-300 hover:text-white hover:bg-navy-700 transition-all"
      >
        <X size={20} weight="bold" />
      </button>
    </Modal>
  )
}
