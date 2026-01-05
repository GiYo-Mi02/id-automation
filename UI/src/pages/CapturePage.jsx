import { useState, useEffect, useCallback, useRef } from 'react'
import { useWebSocket } from '../contexts/WebSocketContext'
import { useToast } from '../contexts/ToastContext'
import CaptureTopBar from '../components/capture/CaptureTopBar'
import CameraViewport from '../components/capture/CameraViewport'
import ControlBar from '../components/capture/ControlBar'
import CaptureRightPanel from '../components/capture/CaptureRightPanel'
import CaptureResultModal from '../components/capture/CaptureResultModal'
import CaptureSuccessModal from '../components/capture/CaptureSuccessModal'

export default function CapturePage() {
  const { status, lastMessage, clearLastMessage } = useWebSocket()
  const toast = useToast()
  const processedMessageRef = useRef(null)
  
  const [showGuide, setShowGuide] = useState(true)
  const [cameras, setCameras] = useState([])
  const [selectedCamera, setSelectedCamera] = useState('')
  const [inputMode, setInputMode] = useState('database') // 'database' | 'manual'
  const [selectedStudent, setSelectedStudent] = useState(null)
  const [manualData, setManualData] = useState({
    id_number: '',
    full_name: '',
    lrn_number: '',
    grade_level: '',
    section: '',
    guardian_name: '',
    address: '',
    contact_number: '',
  })
  const [isCapturing, setIsCapturing] = useState(false)
  const [recentCaptures, setRecentCaptures] = useState([])
  const [modalData, setModalData] = useState(null)
  const [successData, setSuccessData] = useState(null) // For success modal

  // Reset modal states on mount and cleanup on unmount
  useEffect(() => {
    // Clear any persisting modal data when entering the page
    setModalData(null)
    setSuccessData(null)
    
    // Cleanup function - reset modal states when leaving the page
    return () => {
      setModalData(null)
      setSuccessData(null)
    }
  }, [])

  // Enumerate cameras on mount
  useEffect(() => {
    async function enumerateCameras() {
      try {
        await navigator.mediaDevices.getUserMedia({ video: true })
        const devices = await navigator.mediaDevices.enumerateDevices()
        const videoDevices = devices.filter(d => d.kind === 'videoinput')
        setCameras(videoDevices.map(d => ({
          value: d.deviceId,
          label: d.label || `Camera ${videoDevices.indexOf(d) + 1}`
        })))
        if (videoDevices.length > 0 && !selectedCamera) {
          setSelectedCamera(videoDevices[0].deviceId)
        }
      } catch (err) {
        console.error('Failed to enumerate cameras:', err)
        toast.error('Camera Error', 'Could not access camera devices')
      }
    }
    enumerateCameras()
  }, [])

  // Listen for WebSocket updates
  useEffect(() => {
    if (lastMessage?.type === 'id_generated' && lastMessage?.data) {
      const newCapture = lastMessage.data
      const messageKey = `${newCapture.student_id || newCapture.id_number}-${newCapture.timestamp || newCapture.created_at}`
      
      // Prevent processing the same message multiple times
      if (processedMessageRef.current === messageKey) {
        return
      }
      
      console.log('ID Generated WebSocket received:', newCapture)
      processedMessageRef.current = messageKey
      
      // Check if this capture already exists to prevent duplicates
      setRecentCaptures(prev => {
        const exists = prev.some(c => 
          (c.student_id || c.id_number) === (newCapture.student_id || newCapture.id_number) &&
          (c.timestamp || c.created_at) === (newCapture.timestamp || newCapture.created_at)
        )
        
        if (exists) return prev
        return [newCapture, ...prev].slice(0, 20)
      })
      
      // Stop capturing state
      setIsCapturing(false)
      
      // Show success modal with generated ID
      setSuccessData(newCapture)
      
      // Show toast notification (only once)
      toast.success('ID Generated!', `Successfully created ID for ${newCapture.full_name || newCapture.student_id}`)
      
      // Clear the message immediately after processing to prevent re-triggering
      clearLastMessage()
    }
  }, [lastMessage, clearLastMessage, toast])

  // Stable fetch function to prevent infinite loops
  const fetchRecentCaptures = useCallback(async () => {
    try {
      const res = await fetch('/api/history?limit=20')
      if (res.ok) {
        const data = await res.json()
        setRecentCaptures(data)
      }
    } catch (err) {
      console.error('Failed to fetch history:', err)
    }
  }, [])

  // Fetch recent history on mount
  useEffect(() => {
    fetchRecentCaptures()
  }, [fetchRecentCaptures])

  const handleCapture = useCallback(async (imageData) => {
    if (isCapturing) return

    const studentData = inputMode === 'database' ? selectedStudent : manualData
    
    if (!studentData || !studentData.id_number || !studentData.full_name) {
      toast.warning('Missing Data', 'Please select or enter student information first')
      return
    }

    setIsCapturing(true)

    try {
      // Convert base64 image to blob
      const response = await fetch(imageData)
      const blob = await response.blob()
      
      // Create FormData for multipart upload
      const formData = new FormData()
      formData.append('file', blob, 'capture.jpg')
      formData.append('student_id', studentData.id_number || studentData.student_id)
      
      // Add manual data if in manual mode
      if (inputMode === 'manual') {
        formData.append('manual_name', studentData.full_name || '')
        formData.append('manual_grade', studentData.grade_level || '')
        formData.append('manual_section', studentData.section || '')
        formData.append('manual_guardian', studentData.guardian_name || '')
        formData.append('manual_address', studentData.address || '')
        formData.append('manual_contact', studentData.contact_number || studentData.guardian_contact || '')
      }

      const res = await fetch('/api/capture', {
        method: 'POST',
        body: formData,
      })

      if (!res.ok) {
        throw new Error('Capture failed')
      }

      toast.success('Photo Captured', 'Processing ID card...')
      // Result will come via WebSocket
    } catch (err) {
      console.error('Capture error:', err)
      toast.error('Capture Failed', 'Could not process the capture')
      setIsCapturing(false)
    }
  }, [inputMode, selectedStudent, manualData, isCapturing, toast])

  const handleViewCapture = (capture) => {
    setModalData(capture)
  }

  return (
    <div className="h-full flex flex-col bg-navy-950">
      <CaptureTopBar
        status={status}
        showGuide={showGuide}
        onToggleGuide={() => setShowGuide(!showGuide)}
      />

      <div className="flex-1 flex overflow-hidden">
        {/* Left Column - Camera & Controls */}
        <div className="flex-1 overflow-y-auto">
          <div className="h-full flex flex-col p-6 gap-4">
            {/* Camera Viewport */}
            <div className="flex-1 min-h-0">
              <CameraViewport
                deviceId={selectedCamera}
                showGuide={showGuide}
                onCapture={handleCapture}
                isCapturing={isCapturing}
              />
            </div>

            {/* Control Bar */}
            <div className="shrink-0">
              <ControlBar
                cameras={cameras}
                selectedCamera={selectedCamera}
                onCameraChange={setSelectedCamera}
                inputMode={inputMode}
                onInputModeChange={setInputMode}
                selectedStudent={selectedStudent}
                onStudentSelect={setSelectedStudent}
                manualData={manualData}
                onManualDataChange={setManualData}
                onCapture={handleCapture}
                isCapturing={isCapturing}
              />
            </div>
          </div>
        </div>

        {/* Right Column - Sidebar Panel */}
        <div className="w-[400px] shrink-0">
          <CaptureRightPanel
            inputMode={inputMode}
            captures={recentCaptures}
            onRefresh={fetchRecentCaptures}
            onView={handleViewCapture}
            manualData={manualData}
            onManualDataChange={setManualData}
            onStudentSelect={setSelectedStudent}
          />
        </div>
      </div>

      <CaptureResultModal
        isOpen={!!modalData}
        onClose={() => setModalData(null)}
        data={modalData}
      />

      <CaptureSuccessModal
        isOpen={!!successData}
        onClose={() => setSuccessData(null)}
        captureData={successData}
      />
    </div>
  )
}
