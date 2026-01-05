import { clsx } from 'clsx'

export default function Card({ className, children, ...props }) {
  return (
    <div
      className={clsx(
        'bg-slate-900/50 border border-slate-800 rounded-xl backdrop-blur-sm',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

Card.Header = function CardHeader({ className, children }) {
  return (
    <div className={clsx('px-5 py-4 border-b border-slate-800', className)}>
      {children}
    </div>
  )
}

Card.Body = function CardBody({ className, children }) {
  return (
    <div className={clsx('p-5', className)}>
      {children}
    </div>
  )
}

Card.Footer = function CardFooter({ className, children }) {
  return (
    <div className={clsx('px-5 py-4 border-t border-slate-800 bg-slate-900/30 rounded-b-xl', className)}>
      {children}
    </div>
  )
}
