import clsx from 'clsx'

const SOURCE_CONFIG: Record<string, { label: string; color: string }> = {
  jira_story: { label: 'Jira', color: 'bg-blue-900 text-blue-300' },
  incident: { label: 'Incident', color: 'bg-red-900 text-red-300' },
  architecture_decision: { label: 'ADR', color: 'bg-purple-900 text-purple-300' },
  architecture_document: { label: 'Arch Doc', color: 'bg-violet-900 text-violet-300' },
  meeting_note: { label: 'Meeting', color: 'bg-yellow-900 text-yellow-300' },
  sprint_report: { label: 'Sprint', color: 'bg-green-900 text-green-300' },
  email: { label: 'Email', color: 'bg-orange-900 text-orange-300' },
  git_commit: { label: 'Git', color: 'bg-gray-800 text-gray-300' },
  security_policy: { label: 'Policy', color: 'bg-pink-900 text-pink-300' },
  standup: { label: 'Standup', color: 'bg-cyan-900 text-cyan-300' },
}

const RISK_CONFIG: Record<string, string> = {
  LOW: 'bg-gray-800 text-gray-400',
  MEDIUM: 'bg-yellow-900/50 text-yellow-400',
  HIGH: 'bg-orange-900/50 text-orange-400',
  CRITICAL: 'bg-red-900/50 text-red-400',
}

interface SourceBadgeProps { sourceType: string }
interface RiskBadgeProps { risk: string }

export function SourceBadge({ sourceType }: SourceBadgeProps) {
  const cfg = SOURCE_CONFIG[sourceType] ?? { label: sourceType, color: 'bg-gray-800 text-gray-300' }
  return <span className={clsx('badge', cfg.color)}>{cfg.label}</span>
}

export function RiskBadge({ risk }: RiskBadgeProps) {
  return (
    <span className={clsx('badge', RISK_CONFIG[risk] ?? 'bg-gray-800 text-gray-400')}>
      {risk}
    </span>
  )
}
