import { useRef, useEffect, useCallback } from 'react'
import { clsx } from 'clsx'

export default function CameraViewport({ deviceId, showGuide, onCapture, isCapturing }) {
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const streamRef = useRef(null)

  useEffect(() => {
    async function startCamera() {
      if (!deviceId) return

      // Stop existing stream
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(t => t.stop())
      }

      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: {
            deviceId: { exact: deviceId },
            width: { ideal: 1920 },
            height: { ideal: 1080 },
          }
        })
        
        streamRef.current = stream
        if (videoRef.current) {
          videoRef.current.srcObject = stream
        }
      } catch (err) {
        console.error('Failed to start camera:', err)
      }
    }

    startCamera()

    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(t => t.stop())
      }
    }
  }, [deviceId])

  const captureFrame = useCallback(() => {
    if (!videoRef.current || !canvasRef.current || isCapturing) return

    const video = videoRef.current
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')

    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    // Mirror the image
    ctx.translate(canvas.width, 0)
    ctx.scale(-1, 1)
    ctx.drawImage(video, 0, 0)

    const imageData = canvas.toDataURL('image/jpeg', 0.9)
    onCapture(imageData)
  }, [onCapture, isCapturing])

  // Keyboard shortcut
  useEffect(() => {
    const handleKeyPress = (e) => {
      if (e.code === 'Space' && !e.repeat && document.activeElement.tagName !== 'INPUT') {
        e.preventDefault()
        captureFrame()
      }
    }

    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [captureFrame])

  return (
    <div className="relative rounded-xl overflow-hidden border-2 border-navy-700 shadow-xl bg-black aspect-video group">
      {/* Video Feed */}
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="w-full h-full object-cover scale-x-[-1] opacity-95 group-hover:opacity-100 transition-opacity"
      />

      {/* Hidden Canvas for Capture */}
      <canvas ref={canvasRef} className="hidden" />

      {/* Alignment Guide Overlay */}
      {showGuide && (
        <svg
          className="absolute inset-0 w-full h-full pointer-events-none transition-opacity duration-300"
          style={{ opacity: 0.4 }}
          viewBox="0 0 1920 1080"
          preserveAspectRatio="xMidYMid slice"
        >
          {/* Outer Frame */}
          <rect
            x="96"
            y="54"
            width="1728"
            height="972"
            rx="20"
            fill="none"
            stroke="white"
            strokeWidth="2"
            strokeDasharray="10 10"
            opacity="0.5"
          />

          {/* Face Circle */}
          <circle
            cx="960"
            cy="324"
            r="173"
            fill="rgba(255,255,255,0.05)"
            stroke="white"
            strokeWidth="3"
            opacity="0.8"
          />

          {/* Shoulder Line */}
          <path
            d="M 288 594 Q 960 650 1632 594"
            fill="none"
            stroke="white"
            strokeWidth="3"
            opacity="0.7"
          />

          {/* Top Center Alignment Mark */}
          <line
            x1="960"
            y1="54"
            x2="960"
            y2="140"
            stroke="white"
            strokeWidth="2"
            opacity="0.6"
          />
        </svg>
      )}

      {/* Capturing Overlay */}
      {isCapturing && (
        <div className="absolute inset-0 bg-blue-500/20 flex items-center justify-center animate-pulse">
          <div className="text-white text-lg font-bold">Processing...</div>
        </div>
      )}
    </div>
  )
}
