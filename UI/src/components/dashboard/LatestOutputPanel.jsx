import { Eye, ArrowsClockwise, Image } from '@phosphor-icons/react'
import { Button, Card } from '../shared'
import { formatDistanceToNow } from '../utils/formatTime'

export default function LatestOutputPanel({ output, onRefresh, onView, onRegenerate }) {
  return (
    <Card>
      {/* Header */}
      <div className="px-6 py-4 border-b border-navy-700 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Eye size={20} weight="fill" className="text-blue-500" />
          <h2 className="text-base font-bold uppercase text-slate-400 tracking-wider">Latest Output Stream</h2>
        </div>
        <button
          onClick={onRefresh}
          className="w-9 h-9 flex items-center justify-center rounded-lg bg-navy-800 border border-navy-700 text-slate-400 hover:bg-navy-700 hover:text-blue-400 transition-colors active:rotate-180 active:transition-transform active:duration-500"
        >
          <ArrowsClockwise size={18} />
        </button>
      </div>

      {/* Preview Area */}
      <div className="p-8 bg-black rounded-b-xl">
        {output ? (
          <>
            {/* Images */}
            <div className="flex items-center justify-center gap-8 mb-6">
              {/* Front */}
              <div className="text-center">
                <p className="text-xs font-bold uppercase text-slate-600 tracking-widest mb-3">Front</p>
                {output.front_image ? (
                  <img
                    src={output.front_image}
                    alt="Front ID"
                    className="max-h-[350px] w-auto rounded-lg border-2 border-navy-700 shadow-2xl hover:scale-[1.02] transition-transform"
                  />
                ) : (
                  <div className="w-56 h-80 bg-navy-800 rounded-lg border-2 border-navy-700 flex items-center justify-center text-slate-700">
                    <Image size={48} weight="thin" />
                  </div>
                )}
              </div>

              {/* Back */}
              <div className="text-center">
                <p className="text-xs font-bold uppercase text-slate-600 tracking-widest mb-3">Back</p>
                {output.back_image ? (
                  <img
                    src={output.back_image}
                    alt="Back ID"
                    className="max-h-[350px] w-auto rounded-lg border-2 border-navy-700 shadow-2xl hover:scale-[1.02] transition-transform"
                  />
                ) : (
                  <div className="w-56 h-80 bg-navy-800 rounded-lg border-2 border-navy-700 flex items-center justify-center text-slate-700">
                    <Image size={48} weight="thin" />
                  </div>
                )}
              </div>
            </div>

            {/* Metadata Bar */}
            <div className="p-4 bg-navy-800/50 rounded-lg flex items-center justify-between">
              <div>
                <p className="text-lg font-semibold text-slate-200">{output.full_name}</p>
                <p className="text-sm text-slate-500">
                  ID: {output.id_number} • Generated {formatDistanceToNow(output.created_at)}
                </p>
              </div>
              <div className="flex gap-3">
                <Button
                  variant="secondary"
                  size="sm"
                  icon={ArrowsClockwise}
                  onClick={onRegenerate}
                >
                  Regenerate
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  icon={Eye}
                  onClick={onView}
                >
                  View Full
                </Button>
              </div>
            </div>
          </>
        ) : (
          <EmptyState />
        )}
      </div>
    </Card>
  )
}

function EmptyState() {
  return (
    <div className="py-16 text-center">
      <Image size={64} className="mx-auto text-slate-700 animate-pulse-slow" weight="thin" />
      <p className="mt-4 text-base font-medium text-slate-400">Waiting for first capture...</p>
      <p className="text-sm text-slate-600">Generated IDs will appear here</p>
    </div>
  )
}
