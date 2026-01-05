import { clsx } from 'clsx'

const sizes = {
  sm: 'w-4 h-4 border-2',
  md: 'w-6 h-6 border-2',
  lg: 'w-12 h-12 border-3',
}

export default function Spinner({ size = 'md', className }) {
  return (
    <div
      className={clsx(
        'rounded-full border-blue-500 border-t-transparent animate-spin',
        sizes[size],
        className
      )}
    />
  )
}
