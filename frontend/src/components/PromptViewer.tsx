import { useState } from 'react'
import { Copy, Check } from 'lucide-react'
import type { AssembledPrompt } from '../types'

interface Props {
  prompt: AssembledPrompt
}

export function PromptViewer({ prompt }: Props) {
  const [copied, setCopied] = useState(false)
  const [tab, setTab] = useState<'system' | 'user'>('user')

  const copy = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-semibold text-gray-200">Assembled Prompt</h2>
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-500">
            ~{prompt.context_window_used.toLocaleString()} tokens · {prompt.context_items_count} items
          </span>
          <button
            onClick={() => copy(tab === 'user' ? prompt.user_prompt : prompt.system_prompt)}
            className="btn-ghost text-xs py-1 px-2"
          >
            {copied ? <Check className="w-3 h-3 text-green-400" /> : <Copy className="w-3 h-3" />}
          </button>
        </div>
      </div>

      {/* Profile adaptation */}
      <p className="text-xs text-gray-500 mb-3 bg-gray-800/50 rounded px-2 py-1">
        Profile: {prompt.profile_adaptation}
      </p>

      {/* Tabs */}
      <div className="flex gap-1 mb-3">
        {(['user', 'system'] as const).map(t => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-3 py-1 text-xs rounded-md transition-colors ${
              tab === t ? 'bg-blue-600/20 text-blue-400' : 'text-gray-500 hover:text-gray-300'
            }`}
          >
            {t === 'user' ? 'User Prompt' : 'System Prompt'}
          </button>
        ))}
      </div>

      <pre className="text-xs text-gray-300 bg-gray-950 rounded-lg p-3 overflow-auto max-h-96 whitespace-pre-wrap font-mono leading-relaxed">
        {tab === 'user' ? prompt.user_prompt : prompt.system_prompt}
      </pre>
    </div>
  )
}
