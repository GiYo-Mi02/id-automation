import { useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'
import { clsx } from 'clsx'
import { X } from '@phosphor-icons/react'

const sizes = {
  sm: 'max-w-md',
  md: 'max-w-xl',
  lg: 'max-w-3xl',
  xl: 'max-w-5xl',
  full: 'max-w-[95vw]',
}

export default function Modal({
  isOpen,
  onClose,
  title,
  icon: Icon,
  size = 'md',
  showClose = true,
  closeOnOverlay = true,
  closeOnEscape = true,
  children,
  footer,
}) {
  const overlayRef = useRef(null)

  useEffect(() => {
    if (!closeOnEscape) return

    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose()
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [isOpen, onClose, closeOnEscape])

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [isOpen])

  const handleOverlayClick = (e) => {
    if (closeOnOverlay && e.target === overlayRef.current) {
      onClose()
    }
  }

  if (!isOpen) return null

  return createPortal(
    <div
      ref={overlayRef}
      onClick={handleOverlayClick}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-950/90 backdrop-blur-xl animate-fade-in"
    >
      <div
        className={clsx(
          'w-full bg-navy-900 border border-navy-700 rounded-2xl shadow-2xl animate-slide-up',
          'max-h-[90vh] flex flex-col',
          sizes[size]
        )}
      >
        {/* Header */}
        {(title || showClose) && (
          <div className="flex items-center justify-between px-6 py-5 border-b border-navy-700 bg-navy-850 rounded-t-2xl">
            <div className="flex items-center gap-3">
              {Icon && <Icon size={24} className="text-blue-500" weight="bold" />}
              {title && <h2 className="text-xl font-bold text-slate-100">{title}</h2>}
            </div>
            {showClose && (
              <button
                onClick={onClose}
                className="p-2 rounded-lg bg-navy-800 hover:bg-navy-700 text-slate-400 hover:text-slate-200 transition-colors"
              >
                <X size={18} weight="bold" />
              </button>
            )}
          </div>
        )}

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-6">
          {children}
        </div>

        {/* Footer */}
        {footer && (
          <div className="px-6 py-4 border-t border-navy-700 bg-navy-850 rounded-b-2xl">
            {footer}
          </div>
        )}
      </div>
    </div>,
    document.body
  )
}
