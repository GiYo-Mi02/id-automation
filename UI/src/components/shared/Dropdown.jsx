import { useState, useRef, useEffect } from 'react'
import { clsx } from 'clsx'
import { CaretDown, Check } from '@phosphor-icons/react'

export default function Dropdown({
  label,
  value,
  onChange,
  options,
  placeholder = 'Select...',
  disabled = false,
  error,
  className,
}) {
  const [isOpen, setIsOpen] = useState(false)
  const containerRef = useRef(null)

  const selectedOption = options.find(opt => opt.value === value)

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div ref={containerRef} className={clsx('relative', className)}>
      {label && <label className="label">{label}</label>}
      
      <button
        type="button"
        disabled={disabled}
        onClick={() => setIsOpen(!isOpen)}
        className={clsx(
          'w-full h-11 px-4 bg-navy-800 border rounded-lg text-left text-sm transition-all duration-150',
          'flex items-center justify-between gap-2',
          'focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          error ? 'border-red-500' : 'border-navy-700 hover:border-navy-600',
          isOpen && 'border-blue-500 ring-2 ring-blue-500/10'
        )}
      >
        <span className={selectedOption ? 'text-slate-200' : 'text-slate-500'}>
          {selectedOption?.label || placeholder}
        </span>
        <CaretDown
          size={16}
          className={clsx(
            'text-slate-500 transition-transform duration-200',
            isOpen && 'rotate-180'
          )}
        />
      </button>

      {isOpen && (
        <div className="absolute z-20 w-full mt-2 py-1 bg-navy-800 border border-navy-700 rounded-lg shadow-xl animate-fade-in max-h-60 overflow-y-auto">
          {options.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => {
                onChange(option.value)
                setIsOpen(false)
              }}
              className={clsx(
                'w-full px-4 py-2.5 text-left text-sm flex items-center justify-between',
                'hover:bg-navy-700 transition-colors',
                option.value === value
                  ? 'text-blue-400 border-l-2 border-blue-500 bg-navy-700/50'
                  : 'text-slate-300 border-l-2 border-transparent'
              )}
            >
              <span className="truncate">{option.label}</span>
              {option.value === value && <Check size={16} weight="bold" />}
            </button>
          ))}
        </div>
      )}

      {error && <p className="mt-1.5 text-xs text-red-400">{error}</p>}
    </div>
  )
}
