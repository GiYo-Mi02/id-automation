import { Outlet } from 'react-router-dom'
import Sidebar from '../components/layout/Sidebar'

export default function RootLayout() {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  )
}
