import { NavLink } from 'react-router-dom'
import { clsx } from 'clsx'
import {
  Camera,
  ChartBar,
  PencilRuler,
  GearSix,
  CirclesFour,
} from '@phosphor-icons/react'

const navItems = [
  { path: '/capture', icon: Camera, label: 'Capture' },
  { path: '/dashboard', icon: ChartBar, label: 'Dashboard' },
  { path: '/editor', icon: PencilRuler, label: 'Editor' },
  { path: '/settings', icon: GearSix, label: 'Settings' },
]

export default function Sidebar() {
  return (
    <aside className="w-[72px] lg:w-[240px] h-screen bg-navy-900 border-r border-navy-700 flex flex-col shrink-0">
      {/* Logo */}
      <div className="h-16 flex items-center justify-center lg:justify-start gap-3 px-4 border-b border-navy-700">
        <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center">
          <CirclesFour size={24} weight="fill" className="text-white" />
        </div>
        <div className="hidden lg:block">
          <h1 className="text-sm font-bold text-slate-100">ID Automation</h1>
          <p className="text-xs text-slate-500">v2.0</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3">
        <ul className="space-y-1">
          {navItems.map(({ path, icon: Icon, label }) => (
            <li key={path}>
              <NavLink
                to={path}
                className={({ isActive }) =>
                  clsx(
                    'flex items-center gap-3 px-3 py-3 rounded-lg transition-all duration-150',
                    'hover:bg-navy-800 group',
                    isActive
                      ? 'bg-blue-600/10 text-blue-400 border-l-2 border-blue-500'
                      : 'text-slate-400 border-l-2 border-transparent'
                  )
                }
              >
                <Icon size={22} weight="bold" className="shrink-0" />
                <span className="hidden lg:block text-sm font-medium">{label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-3 border-t border-navy-700">
        <div className="hidden lg:block px-3 py-2">
          <p className="text-xs text-slate-600">Powered by</p>
          <p className="text-xs text-slate-500 font-medium">School ID System</p>
        </div>
      </div>
    </aside>
  )
}
