import { clsx } from 'clsx'

export default function Slider({
  value,
  onChange,
  min = 0,
  max = 100,
  step = 1,
  label,
  showValue = true,
  disabled = false,
}) {
  const percentage = ((value - min) / (max - min)) * 100

  return (
    <div className={clsx(disabled && 'opacity-50')}>
      {(label || showValue) && (
        <div className="flex items-center justify-between mb-3">
          {label && <span className="text-sm font-semibold text-slate-300">{label}</span>}
          {showValue && (
            <span className="text-sm tabular-nums text-slate-500 bg-navy-800 px-2 py-1 rounded">
              {value}
            </span>
          )}
        </div>
      )}
      <div className="relative">
        <div className="h-1.5 bg-navy-700 rounded-full">
          <div
            className="h-full bg-gradient-to-r from-blue-600 to-blue-500 rounded-full"
            style={{ width: `${percentage}%` }}
          />
        </div>
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          disabled={disabled}
          className={clsx(
            'absolute inset-0 w-full h-full opacity-0 cursor-pointer',
            disabled && 'cursor-not-allowed'
          )}
        />
        <div
          className="absolute top-1/2 -translate-y-1/2 w-5 h-5 bg-blue-500 border-[3px] border-navy-900 rounded-full shadow-lg pointer-events-none transition-transform hover:scale-110"
          style={{ left: `calc(${percentage}% - 10px)` }}
        />
      </div>
      <div className="flex justify-between mt-2 text-xs text-slate-600">
        <span>{min}</span>
        <span>{max}</span>
      </div>
    </div>
  )
}
