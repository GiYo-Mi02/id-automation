import { Users, Clock, Heartbeat, HardDrives } from '@phosphor-icons/react'
import { Card } from '../shared'

export default function StatsGrid({ totalIds, pendingCount = 0, systemStatus = 'Online', storageUsage = 45 }) {
  const stats = [
    {
      label: 'Total IDs Printed',
      value: totalIds,
      icon: Users,
      color: 'text-blue-400',
      trend: '+12% from last week'
    },
    {
      label: 'Pending Queue',
      value: pendingCount,
      icon: Clock,
      color: 'text-amber-400',
      trend: 'Processing...'
    },
    {
      label: 'System Health',
      value: systemStatus,
      icon: Heartbeat,
      color: 'text-emerald-400',
      trend: 'All systems operational'
    },
    {
      label: 'Storage Usage',
      value: `${storageUsage}%`,
      icon: HardDrives,
      color: 'text-purple-400',
      trend: '120GB / 500GB'
    }
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {stats.map((stat, index) => (
        <Card key={index} className="p-4 flex items-start justify-between hover:border-slate-700 transition-colors">
          <div>
            <p className="text-sm font-medium text-slate-400">{stat.label}</p>
            <h3 className="text-2xl font-bold text-white mt-1">{stat.value}</h3>
            <p className="text-xs text-slate-500 mt-2">{stat.trend}</p>
          </div>
          <div className={`p-2 rounded-lg bg-slate-800/50 ${stat.color}`}>
            <stat.icon size={24} weight="duotone" />
          </div>
        </Card>
      ))}
    </div>
  )
}
