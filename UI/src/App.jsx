import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { WebSocketProvider } from './contexts/WebSocketContext'
import { ToastProvider } from './contexts/ToastContext'
import { SettingsProvider } from './contexts/SettingsContext'
import RootLayout from './layouts/RootLayout'
import CapturePage from './pages/CapturePage'
import DashboardPage from './pages/DashboardPage'
import EditorPage from './pages/EditorPage'
import SettingsPage from './pages/SettingsPage'

function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <SettingsProvider>
          <WebSocketProvider>
            <Routes>
              <Route path="/" element={<RootLayout />}>
                <Route index element={<Navigate to="/capture" replace />} />
                <Route path="capture" element={<CapturePage />} />
                <Route path="dashboard" element={<DashboardPage />} />
                <Route path="editor" element={<EditorPage />} />
                <Route path="settings" element={<SettingsPage />} />
              </Route>
            </Routes>
          </WebSocketProvider>
        </SettingsProvider>
      </ToastProvider>
    </BrowserRouter>
  )
}

export default App
