import { forwardRef } from 'react'
import { clsx } from 'clsx'
import Spinner from './Spinner'

const variants = {
  primary: 'bg-blue-600 text-white hover:bg-blue-500 active:bg-blue-700 shadow-md focus:ring-blue-500',
  secondary: 'bg-navy-800 text-slate-300 border border-navy-700 hover:bg-navy-700 hover:text-white focus:ring-navy-600',
  ghost: 'bg-transparent text-slate-400 hover:bg-navy-800/50 hover:text-slate-200 focus:ring-navy-600',
  danger: 'bg-red-600/20 text-red-400 border border-red-500/30 hover:bg-red-600/30 focus:ring-red-500',
  success: 'bg-green-600 text-white hover:bg-green-500 active:bg-green-700 shadow-md focus:ring-green-500',
}

const sizes = {
  sm: 'h-8 px-3 text-xs gap-1.5',
  md: 'h-10 px-4 text-sm gap-2',
  lg: 'h-12 px-6 text-base gap-2',
}

const Button = forwardRef(function Button(
  {
    variant = 'primary',
    size = 'md',
    loading = false,
    disabled = false,
    icon: Icon,
    iconPosition = 'left',
    children,
    className,
    ...props
  },
  ref
) {
  const isDisabled = disabled || loading

  return (
    <button
      ref={ref}
      disabled={isDisabled}
      className={clsx(
        'inline-flex items-center justify-center font-semibold rounded-lg transition-all duration-150',
        'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-navy-950',
        'active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100',
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {loading ? (
        <>
          <Spinner size="sm" />
          <span>{children}</span>
        </>
      ) : (
        <>
          {Icon && iconPosition === 'left' && <Icon size={size === 'sm' ? 14 : size === 'lg' ? 20 : 16} weight="bold" />}
          <span>{children}</span>
          {Icon && iconPosition === 'right' && <Icon size={size === 'sm' ? 14 : size === 'lg' ? 20 : 16} weight="bold" />}
        </>
      )}
    </button>
  )
})

export default Button
