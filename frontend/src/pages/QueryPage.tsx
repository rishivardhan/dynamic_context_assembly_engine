import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { runQuery, fetchProjects, fetchProfiles } from '../api'
import type { QueryRequest } from '../types'
import { useAppStore } from '../store'
import { ContextCard } from '../components/ContextCard'
import { PromptViewer } from '../components/PromptViewer'
import { Send, Loader2, Zap, Settings2 } from 'lucide-react'

const EXAMPLE_QUERIES = [
  'What is the current status of the Postgres migration?',
  'Are there any critical incidents related to the API Gateway?',
  'What security policies govern database access?',
  'What architectural decisions have been made for Zero Trust?',
  'What is the cutover plan for the Oracle to PostgreSQL migration?',
]

const SCORE_WEIGHT_DEFAULTS = {
  semantic: 0.30,
  temporal: 0.25,
  authority: 0.15,
  risk: 0.20,
  project: 0.10,
}

export function QueryPage() {
  const [query, setQuery] = useState('')
  const [showSettings, setShowSettings] = useState(false)
  const [weights, setWeights] = useState(SCORE_WEIGHT_DEFAULTS)
  const { setLastResponse, setLastQuery } = useAppStore()
  const selectedProfileId = useAppStore(s => s.selectedProfileId)
  const setSelectedProfileId = useAppStore(s => s.setSelectedProfileId)

  const { data: projects } = useQuery({ queryKey: ['projects'], queryFn: fetchProjects })
  const { data: profiles } = useQuery({ queryKey: ['profiles'], queryFn: fetchProfiles })

  const mutation = useMutation({
    mutationFn: (req: QueryRequest) => runQuery(req),
    onSuccess: (data) => {
      setLastResponse(data)
    },
  })

  const submit = (q?: string) => {
    const text = q || query
    if (!text.trim()) return
    const req: QueryRequest = {
      query: text,
      user_profile_id: selectedProfileId || undefined,
      weights,
      include_rag_comparison: true,
      top_k: 8,
    }
    setLastQuery(req)
    setQuery(text)
    mutation.mutate(req)
  }

  const response = mutation.data

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="border-b border-gray-800 px-6 py-4 flex-shrink-0">
        <h1 className="text-lg font-bold text-white">Query Engine</h1>
        <p className="text-xs text-gray-500 mt-0.5">
          Multi-dimensional context assembly with explainable scoring
        </p>
      </div>

      <div className="flex-1 overflow-auto p-6 space-y-6">
        {/* Query Console */}
        <div className="card">
          <div className="flex gap-2 mb-3">
            <div className="flex-1 relative">
              <textarea
                value={query}
                onChange={e => setQuery(e.target.value)}
                onKeyDown={e => {
                  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) submit()
                }}
                placeholder="Ask a question about your enterprise systems..."
                rows={2}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-100
                           placeholder-gray-600 resize-none focus:outline-none focus:border-blue-500"
              />
            </div>
            <div className="flex flex-col gap-2">
              <button
                onClick={() => submit()}
                disabled={!query.trim() || mutation.isPending}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {mutation.isPending
                  ? <Loader2 className="w-4 h-4 animate-spin" />
                  : <Send className="w-4 h-4" />}
                Run
              </button>
              <button
                onClick={() => setShowSettings(v => !v)}
                className="btn-ghost text-xs"
              >
                <Settings2 className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Settings panel */}
          {showSettings && (
            <div className="border-t border-gray-800 pt-3 mt-2 grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs text-gray-500 block mb-1">User Profile</label>
                <select
                  value={selectedProfileId}
                  onChange={e => setSelectedProfileId(e.target.value)}
                  className="w-full bg-gray-800 border border-gray-700 rounded text-xs text-gray-200 px-2 py-1"
                >
                  <option value="">Default (no profile)</option>
                  {profiles?.map(p => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs text-gray-500 block mb-2">Scoring Weights</label>
                <div className="space-y-1">
                  {Object.entries(weights).map(([dim, val]) => (
                    <div key={dim} className="flex items-center gap-2">
                      <span className="text-xs text-gray-400 w-16">{dim}</span>
                      <input
                        type="range" min={0} max={1} step={0.05}
                        value={val}
                        onChange={e => setWeights(w => ({ ...w, [dim]: parseFloat(e.target.value) }))}
                        className="flex-1 h-1"
                      />
                      <span className="text-xs font-mono text-gray-400 w-8">{val.toFixed(2)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Example queries */}
          <div className="flex flex-wrap gap-2 mt-3">
            {EXAMPLE_QUERIES.map(q => (
              <button
                key={q}
                onClick={() => submit(q)}
                className="text-xs bg-gray-800 hover:bg-gray-700 text-gray-400 px-2 py-1 rounded-full transition-colors"
              >
                {q.length > 55 ? q.slice(0, 52) + '…' : q}
              </button>
            ))}
          </div>
        </div>

        {mutation.isPending && (
          <div className="flex items-center gap-3 text-gray-500 text-sm">
            <Loader2 className="w-4 h-4 animate-spin" />
            Assembling context... running semantic search, scoring, and prompt assembly...
          </div>
        )}

        {mutation.isError && (
          <div className="card border-red-800 text-red-400 text-sm">
            Error: {(mutation.error as Error).message}
          </div>
        )}

        {response && (
          <>
            {/* Summary bar */}
            <div className="card flex flex-wrap items-center gap-4 text-sm">
              <div>
                <span className="text-gray-500 text-xs">Project detected</span>
                <p className="text-blue-400 font-medium">
                  {response.project_detected || 'None'}
                </p>
              </div>
              <div>
                <span className="text-gray-500 text-xs">Candidates evaluated</span>
                <p className="text-gray-200 font-medium">{response.total_candidates}</p>
              </div>
              <div>
                <span className="text-gray-500 text-xs">Context selected</span>
                <p className="text-gray-200 font-medium">{response.selected_context.length}</p>
              </div>
              <div>
                <span className="text-gray-500 text-xs">Processing time</span>
                <p className="text-gray-200 font-medium">{response.processing_time_ms.toFixed(0)}ms</p>
              </div>
              <div>
                <span className="text-gray-500 text-xs">Prompt tokens</span>
                <p className="text-gray-200 font-medium">
                  ~{response.assembled_prompt.context_window_used.toLocaleString()}
                </p>
              </div>
              <div className="ml-auto flex items-center gap-1 text-blue-400">
                <Zap className="w-4 h-4" />
                <span className="text-xs font-medium">DCAE Active</span>
              </div>
            </div>

            <div className="grid grid-cols-5 gap-6">
              {/* Context results */}
              <div className="col-span-3 space-y-3">
                <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide">
                  Selected Context ({response.selected_context.length})
                </h2>
                {response.selected_context.map(item => (
                  <ContextCard key={item.id} item={item} highlight={item.rank === 1} />
                ))}
              </div>

              {/* Right panel */}
              <div className="col-span-2 space-y-4">
                <PromptViewer prompt={response.assembled_prompt} />
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
