import { createContext, useContext, useState, useCallback } from 'react'
import Toast from '../components/shared/Toast'

const ToastContext = createContext(null)

let toastId = 0

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const addToast = useCallback(({ type = 'info', title, message, duration = 4000 }) => {
    const id = ++toastId
    setToasts(prev => [...prev, { id, type, title, message, duration }])
    return id
  }, [])

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  const success = useCallback((title, message) => addToast({ type: 'success', title, message }), [addToast])
  const error = useCallback((title, message) => addToast({ type: 'error', title, message }), [addToast])
  const warning = useCallback((title, message) => addToast({ type: 'warning', title, message }), [addToast])
  const info = useCallback((title, message) => addToast({ type: 'info', title, message }), [addToast])

  return (
    <ToastContext.Provider value={{ addToast, removeToast, success, error, warning, info }}>
      {children}
      <div className="fixed top-20 right-6 z-50 flex flex-col gap-3 w-[360px] max-w-[calc(100vw-48px)]">
        {toasts.map(toast => (
          <Toast key={toast.id} {...toast} onClose={() => removeToast(toast.id)} />
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider')
  }
  return context
}
