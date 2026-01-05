import { clsx } from 'clsx'

export default function Card({ className, children, ...props }) {
  return (
    <div
      className={clsx(
        'bg-navy-900 border border-navy-700 rounded-xl shadow-lg',
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
    <div className={clsx('px-5 py-4 border-b border-navy-700', className)}>
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
    <div className={clsx('px-5 py-4 border-t border-navy-700 bg-navy-850 rounded-b-xl', className)}>
      {children}
    </div>
  )
}
