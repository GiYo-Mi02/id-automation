import { clsx } from 'clsx'

export default function Toggle({ checked, onChange, disabled = false, label, description }) {
  return (
    <label className={clsx(
      'flex items-center justify-between gap-4 cursor-pointer',
      disabled && 'opacity-50 cursor-not-allowed'
    )}>
      <div className="flex-1">
        {label && <span className="text-sm font-medium text-slate-300">{label}</span>}
        {description && <p className="text-xs text-slate-600 mt-1">{description}</p>}
      </div>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        disabled={disabled}
        onClick={() => !disabled && onChange(!checked)}
        className={clsx(
          'relative inline-flex h-6 w-12 shrink-0 items-center rounded-full transition-all duration-200',
          'focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:ring-offset-2 focus:ring-offset-navy-950',
          checked ? 'bg-blue-600' : 'bg-navy-700 border border-navy-600'
        )}
      >
        <span
          className={clsx(
            'inline-block h-[18px] w-[18px] rounded-full bg-white shadow-sm transition-all duration-200 ease-spring',
            checked ? 'translate-x-[27px]' : 'translate-x-[3px]'
          )}
        />
      </button>
    </label>
  )
}
