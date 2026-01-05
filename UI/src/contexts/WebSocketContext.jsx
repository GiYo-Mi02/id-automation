import { createContext, useContext, useEffect, useState, useCallback, useRef } from 'react'

const WebSocketContext = createContext(null)

export function WebSocketProvider({ children }) {
  const [status, setStatus] = useState('disconnected') // 'connecting' | 'connected' | 'disconnected'
  const [lastMessage, setLastMessage] = useState(null)
  const wsRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)
  const reconnectAttempts = useRef(0)
  const messageClearTimeoutRef = useRef(null)

  // Function to clear the last message (prevents duplicate processing)
  const clearLastMessage = useCallback(() => {
    setLastMessage(null)
    if (messageClearTimeoutRef.current) {
      clearTimeout(messageClearTimeoutRef.current)
      messageClearTimeoutRef.current = null
    }
  }, [])

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    setStatus('connecting')
    
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws`
    
    try {
      wsRef.current = new WebSocket(wsUrl)

      wsRef.current.onopen = () => {
        setStatus('connected')
        reconnectAttempts.current = 0
      }

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          setLastMessage(data)
          
          // Auto-clear message after 5 seconds to prevent it from persisting across navigations
          if (messageClearTimeoutRef.current) {
            clearTimeout(messageClearTimeoutRef.current)
          }
          messageClearTimeoutRef.current = setTimeout(() => {
            setLastMessage(null)
            messageClearTimeoutRef.current = null
          }, 5000)
        } catch {
          console.warn('Failed to parse WebSocket message:', event.data)
        }
      }

      wsRef.current.onclose = () => {
        setStatus('disconnected')
        scheduleReconnect()
      }

      wsRef.current.onerror = () => {
        setStatus('disconnected')
      }
    } catch (err) {
      console.error('WebSocket connection error:', err)
      setStatus('disconnected')
      scheduleReconnect()
    }
  }, [])

  const scheduleReconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) return

    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000)
    reconnectAttempts.current += 1

    reconnectTimeoutRef.current = setTimeout(() => {
      reconnectTimeoutRef.current = null
      connect()
    }, delay)
  }, [connect])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    if (messageClearTimeoutRef.current) {
      clearTimeout(messageClearTimeoutRef.current)
      messageClearTimeoutRef.current = null
    }
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    setStatus('disconnected')
    setLastMessage(null) // Clear message on disconnect
  }, [])

  const send = useCallback((data) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data))
    }
  }, [])

  useEffect(() => {
    connect()
    return () => disconnect()
  }, [connect, disconnect])

  return (
    <WebSocketContext.Provider value={{ status, lastMessage, send, connect, disconnect, clearLastMessage }}>
      {children}
    </WebSocketContext.Provider>
  )
}

export function useWebSocket() {
  const context = useContext(WebSocketContext)
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider')
  }
  return context
}
