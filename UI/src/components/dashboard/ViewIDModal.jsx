import { Modal } from '../shared'
import { X } from '@phosphor-icons/react'

export default function ViewIDModal({ isOpen, onClose, student }) {
  if (!student) return null

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl" showClose={false}>
      {/* Close Button */}
      <button
        onClick={onClose}
        className="fixed top-6 right-6 z-50 w-12 h-12 flex items-center justify-center rounded-full bg-navy-800 border border-navy-700 text-slate-200 hover:bg-navy-700 hover:scale-105 transition-all shadow-xl"
      >
        <X size={24} weight="bold" />
      </button>

      {/* Content */}
      <div className="flex flex-col lg:flex-row items-center justify-center gap-12 py-8">
        {/* Front ID */}
        <div className="text-center">
          <p className="text-xs font-bold uppercase text-slate-500 tracking-widest mb-3">Front</p>
          {student.front_image ? (
            <img
              src={student.front_image}
              alt="Front ID"
              className="max-h-[70vh] w-auto rounded-xl border-2 border-navy-700 shadow-2xl hover:scale-[1.02] transition-transform"
            />
          ) : (
            <div className="w-80 h-[500px] bg-navy-800 rounded-xl border-2 border-navy-700 flex items-center justify-center text-slate-600">
              No image
            </div>
          )}
        </div>

        {/* Back ID */}
        <div className="text-center">
          <p className="text-xs font-bold uppercase text-slate-500 tracking-widest mb-3">Back</p>
          {student.back_image ? (
            <img
              src={student.back_image}
              alt="Back ID"
              className="max-h-[70vh] w-auto rounded-xl border-2 border-navy-700 shadow-2xl hover:scale-[1.02] transition-transform"
            />
          ) : (
            <div className="w-80 h-[500px] bg-navy-800 rounded-xl border-2 border-navy-700 flex items-center justify-center text-slate-600">
              No image
            </div>
          )}
        </div>
      </div>

      {/* Student Info */}
      <div className="text-center pb-4">
        <p className="text-lg font-semibold text-slate-200">{student.full_name}</p>
        <p className="text-sm text-slate-500">ID: {student.id_number}</p>
      </div>
    </Modal>
  )
}
