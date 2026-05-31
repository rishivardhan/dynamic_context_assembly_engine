interface Props {
  label: string
  value: number
  color?: string
  explanation?: string
}

export function ScoreBar({ label, value, color = 'bg-blue-500', explanation }: Props) {
  const pct = Math.round(value * 100)
  return (
    <div className="group">
      <div className="flex justify-between items-center mb-1">
        <span className="text-xs text-gray-400">{label}</span>
        <span className="text-xs font-mono text-gray-200">{pct}%</span>
      </div>
      <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      {explanation && (
        <p className="text-xs text-gray-600 mt-1 hidden group-hover:block leading-tight">
          {explanation}
        </p>
      )}
    </div>
  )
}
