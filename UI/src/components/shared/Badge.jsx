import { clsx } from 'clsx'

const variants = {
  success: 'bg-green-500/10 border-green-500/20 text-green-400',
  error: 'bg-red-500/10 border-red-500/20 text-red-400',
  warning: 'bg-amber-500/10 border-amber-500/20 text-amber-400',
  info: 'bg-blue-500/10 border-blue-500/20 text-blue-400',
  neutral: 'bg-slate-500/10 border-slate-500/20 text-slate-400',
}

export default function Badge({ variant = 'neutral', icon: Icon, children, className }) {
  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md border text-xs font-medium',
        variants[variant],
        className
      )}
    >
      {Icon && <Icon size={14} weight="fill" />}
      {children}
    </span>
  )
}
