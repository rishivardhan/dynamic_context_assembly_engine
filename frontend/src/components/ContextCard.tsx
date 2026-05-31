import { useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'
import type { ScoredContext } from '../types'
import { ScoreBar } from './ScoreBar'
import { SourceBadge, RiskBadge } from './SourceBadge'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, Tooltip,
} from 'recharts'

interface Props {
  item: ScoredContext
  highlight?: boolean
}

const SCORE_COLORS: Record<string, string> = {
  semantic: 'bg-blue-500',
  temporal: 'bg-green-500',
  authority: 'bg-purple-500',
  risk: 'bg-red-500',
  project: 'bg-yellow-500',
}

export function ContextCard({ item, highlight }: Props) {
  const [expanded, setExpanded] = useState(false)
  const [showScores, setShowScores] = useState(false)

  const radarData = [
    { dim: 'Semantic', value: Math.round(item.scores.semantic * 100) },
    { dim: 'Temporal', value: Math.round(item.scores.temporal * 100) },
    { dim: 'Authority', value: Math.round(item.scores.authority * 100) },
    { dim: 'Risk', value: Math.round(item.scores.risk * 100) },
    { dim: 'Project', value: Math.round(item.scores.project * 100) },
  ]

  return (
    <div className={`card transition-all ${highlight ? 'border-blue-600' : ''}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <span className="text-xs font-bold text-gray-500">#{item.rank}</span>
            <SourceBadge sourceType={item.source_type} />
            <RiskBadge risk={item.risk_level} />
            <span className="text-xs text-gray-500">{item.age_days}d old</span>
            {item.tags.slice(0, 3).map(t => (
              <span key={t} className="badge bg-gray-800 text-gray-500">{t}</span>
            ))}
          </div>
          <h3 className="text-sm font-semibold text-gray-100 leading-snug truncate">
            {item.title}
          </h3>
          <p className="text-xs text-gray-500 mt-0.5">
            {item.project} · {item.owner}
          </p>
        </div>
        <div className="flex-shrink-0 text-right">
          <div className="text-lg font-bold text-blue-400">
            {(item.scores.final * 100).toFixed(1)}
          </div>
          <div className="text-xs text-gray-600">score</div>
        </div>
      </div>

      {/* Score bars */}
      <div className="mt-3 grid grid-cols-5 gap-2">
        {Object.entries(SCORE_COLORS).map(([dim, color]) => (
          <ScoreBar
            key={dim}
            label={dim.charAt(0).toUpperCase() + dim.slice(1)}
            value={(item.scores as Record<string, number>)[dim]}
            color={color}
            explanation={item.scores.explanation?.[dim]}
          />
        ))}
      </div>

      {/* Expand content */}
      <div className="mt-3 flex gap-2">
        <button
          onClick={() => setExpanded(v => !v)}
          className="text-xs text-gray-500 hover:text-gray-300 flex items-center gap-1"
        >
          {expanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          {expanded ? 'Hide content' : 'Show content'}
        </button>
        <button
          onClick={() => setShowScores(v => !v)}
          className="text-xs text-gray-500 hover:text-gray-300 flex items-center gap-1 ml-3"
        >
          {showScores ? 'Hide radar' : 'Score radar'}
        </button>
      </div>

      {expanded && (
        <p className="mt-2 text-xs text-gray-400 leading-relaxed border-t border-gray-800 pt-2 line-clamp-6">
          {item.content}
        </p>
      )}

      {showScores && (
        <div className="mt-2 border-t border-gray-800 pt-2">
          <ResponsiveContainer width="100%" height={180}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#374151" />
              <PolarAngleAxis dataKey="dim" tick={{ fill: '#9ca3af', fontSize: 10 }} />
              <Radar
                name="Score"
                dataKey="value"
                stroke="#3b82f6"
                fill="#3b82f6"
                fillOpacity={0.25}
              />
              <Tooltip
                contentStyle={{ background: '#111827', border: '1px solid #374151', borderRadius: 6 }}
                labelStyle={{ color: '#f9fafb' }}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
