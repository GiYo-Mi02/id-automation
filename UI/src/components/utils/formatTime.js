export function formatDistanceToNow(dateString) {
  if (!dateString) return 'Unknown'
  
  try {
    // Principal Engineer Fix: Properly handle ISO 8601 timestamps (UTC)
    // JavaScript Date constructor automatically converts UTC to local time
    const date = new Date(dateString)
    
    // Validate the date
    if (isNaN(date.getTime())) {
      return 'Invalid date'
    }
    
    const now = new Date()
    const diffMs = now - date
    const diffSec = Math.floor(diffMs / 1000)
    const diffMin = Math.floor(diffSec / 60)
    const diffHour = Math.floor(diffMin / 60)
    const diffDay = Math.floor(diffHour / 24)

    if (diffSec < 10) return 'Just now'
    if (diffSec < 60) return `${diffSec} seconds ago`
    if (diffMin < 60) return `${diffMin} minute${diffMin > 1 ? 's' : ''} ago`
    if (diffHour < 24) return `${diffHour} hour${diffHour > 1 ? 's' : ''} ago`
    if (diffDay < 7) return `${diffDay} day${diffDay > 1 ? 's' : ''} ago`
    
    return date.toLocaleDateString()
  } catch (error) {
    console.error('Date parsing error:', error)
    return 'Unknown'
  }
}

export function formatTime(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}
