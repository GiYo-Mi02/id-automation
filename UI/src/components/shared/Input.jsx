import { forwardRef } from 'react'
import { clsx } from 'clsx'

const Input = forwardRef(function Input(
  {
    label,
    error,
    hint,
    icon: Icon,
    required,
    className,
    containerClassName,
    ...props
  },
  ref
) {
  return (
    <div className={containerClassName}>
      {label && (
        <label className="label">
          {label}
          {required && <span className="text-red-400 ml-1">*</span>}
        </label>
      )}
      <div className="relative">
        {Icon && (
          <Icon
            size={18}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none"
          />
        )}
        <input
          ref={ref}
          className={clsx(
            'input',
            Icon && 'pl-10',
            error && 'input-error',
            className
          )}
          {...props}
        />
      </div>
      {error && <p className="mt-1.5 text-xs text-red-400">{error}</p>}
      {hint && !error && <p className="mt-1.5 text-xs text-slate-600">{hint}</p>}
    </div>
  )
})

export default Input
