import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { runQuery, fetchProfiles } from '../api'
import type { QueryRequest, ScoredContext, RAGResult } from '../types'
import { SourceBadge, RiskBadge } from '../components/SourceBadge'
import { ScoreBar } from '../components/ScoreBar'
import { Send, Loader2, TrendingUp, Search, Zap } from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'

const EXAMPLE_QUERIES = [
  'What is the current status of the Postgres migration?',
  'What security incidents occurred recently?',
  'What architectural decisions govern API authentication?',
]

export function ComparisonPage() {
  const [query, setQuery] = useState('')
  const [selectedProfileId, setSelectedProfileId] = useState('')

  const { data: profiles } = useQuery({ queryKey: ['profiles'], queryFn: fetchProfiles })

  const mutation = useMutation({
    mutationFn: (req: QueryRequest) => runQuery(req),
  })

  const submit = (q?: string) => {
    const text = q || query
    if (!text.trim()) return
    setQuery(text)
    mutation.mutate({
      query: text,
      user_profile_id: selectedProfileId || undefined,
      include_rag_comparison: true,
      top_k: 8,
    })
  }

  const response = mutation.data
  const dcaeItems = response?.selected_context ?? []
  const ragItems = response?.rag_comparison ?? []

  const comparisonData = dcaeItems.slice(0, 8).map((dcae, i) => {
    const rag = ragItems[i]
    return {
      name: `#${i + 1}`,
      DCAE: Math.round(dcae.scores.final * 100),
      RAG: rag ? Math.round(rag.semantic_score * 100) : 0,
      dcaeTitle: dcae.title.slice(0, 40),
      ragTitle: rag?.title?.slice(0, 40) ?? '',
    }
  })

  const dcaeTokens = response?.assembled_prompt.context_window_used ?? 0
  const dcaeCount = dcaeItems.length

  return (
    <div className="h-full flex flex-col">
      <div className="border-b border-gray-800 px-6 py-4 flex-shrink-0">
        <h1 className="text-lg font-bold text-white">RAG vs DCAE Comparison</h1>
        <p className="text-xs text-gray-500 mt-0.5">
          Compare traditional semantic-only RAG with multi-dimensional DCAE context assembly
        </p>
      </div>

      <div className="flex-1 overflow-auto p-6 space-y-6">
        {/* Query input */}
        <div className="card">
          <div className="flex gap-2 mb-3">
            <input
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && submit()}
              placeholder="Enter a query to compare RAG vs DCAE..."
              className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm
                         text-gray-100 placeholder-gray-600 focus:outline-none focus:border-blue-500"
            />
            <select
              value={selectedProfileId}
              onChange={e => setSelectedProfileId(e.target.value)}
              className="bg-gray-800 border border-gray-700 rounded-lg px-2 py-2 text-xs text-gray-300"
            >
              <option value="">No profile</option>
              {profiles?.map(p => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
            <button
              onClick={() => submit()}
              disabled={!query.trim() || mutation.isPending}
              className="btn-primary disabled:opacity-50"
            >
              {mutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {EXAMPLE_QUERIES.map(q => (
              <button
                key={q}
                onClick={() => submit(q)}
                className="text-xs bg-gray-800 hover:bg-gray-700 text-gray-400 px-2 py-1 rounded-full"
              >
                {q}
              </button>
            ))}
          </div>
        </div>

        {mutation.isPending && (
          <div className="flex items-center gap-2 text-gray-500 text-sm">
            <Loader2 className="w-4 h-4 animate-spin" />
            Running both retrieval strategies...
          </div>
        )}

        {response && (
          <>
            {/* Stats comparison */}
            <div className="grid grid-cols-2 gap-4">
              {/* RAG stats */}
              <div className="card border-gray-700">
                <div className="flex items-center gap-2 mb-3">
                  <Search className="w-4 h-4 text-gray-400" />
                  <h2 className="text-sm font-semibold text-gray-200">Traditional RAG</h2>
                  <span className="badge bg-gray-800 text-gray-400 ml-auto">Semantic Only</span>
                </div>
                <div className="grid grid-cols-3 gap-3 text-center">
                  <div>
                    <p className="text-xl font-bold text-gray-100">{ragItems.length}</p>
                    <p className="text-xs text-gray-500">Results</p>
                  </div>
                  <div>
                    <p className="text-xl font-bold text-gray-100">1</p>
                    <p className="text-xs text-gray-500">Dimensions</p>
                  </div>
                  <div>
                    <p className="text-xl font-bold text-gray-100">
                      {ragItems[0] ? (ragItems[0].semantic_score * 100).toFixed(0) : '—'}
                    </p>
                    <p className="text-xs text-gray-500">Top Score</p>
                  </div>
                </div>
                <div className="mt-2 text-xs text-gray-600 bg-gray-800/50 rounded p-2">
                  Ranks purely by vector cosine similarity. No temporal, authority, risk, or
                  project context is considered.
                </div>
              </div>

              {/* DCAE stats */}
              <div className="card border-blue-800">
                <div className="flex items-center gap-2 mb-3">
                  <Zap className="w-4 h-4 text-blue-400" />
                  <h2 className="text-sm font-semibold text-blue-300">DCAE</h2>
                  <span className="badge bg-blue-900 text-blue-300 ml-auto">Multi-Dimensional</span>
                </div>
                <div className="grid grid-cols-3 gap-3 text-center">
                  <div>
                    <p className="text-xl font-bold text-blue-300">{dcaeCount}</p>
                    <p className="text-xs text-gray-500">Results</p>
                  </div>
                  <div>
                    <p className="text-xl font-bold text-blue-300">5</p>
                    <p className="text-xs text-gray-500">Dimensions</p>
                  </div>
                  <div>
                    <p className="text-xl font-bold text-blue-300">
                      {dcaeItems[0] ? (dcaeItems[0].scores.final * 100).toFixed(0) : '—'}
                    </p>
                    <p className="text-xs text-gray-500">Top Score</p>
                  </div>
                </div>
                <div className="mt-2 text-xs text-gray-600 bg-blue-900/20 rounded p-2">
                  Semantic + Temporal + Authority + Risk + Project dimensions, with
                  behavioral adaptation per user profile.
                </div>
              </div>
            </div>

            {/* Score comparison chart */}
            {comparisonData.length > 0 && (
              <div className="card">
                <div className="flex items-center gap-2 mb-4">
                  <TrendingUp className="w-4 h-4 text-gray-400" />
                  <h2 className="text-sm font-semibold text-gray-200">Score Comparison by Rank</h2>
                </div>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={comparisonData} barGap={2}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 11 }} />
                    <YAxis tick={{ fill: '#9ca3af', fontSize: 11 }} domain={[0, 100]} />
                    <Tooltip
                      contentStyle={{ background: '#111827', border: '1px solid #374151', borderRadius: 6 }}
                      labelStyle={{ color: '#f9fafb' }}
                      formatter={(value: number, name: string, props: { payload?: { dcaeTitle?: string; ragTitle?: string } }) => [
                        `${value}%${name === 'DCAE' ? ` — ${props.payload?.dcaeTitle}` : ` — ${props.payload?.ragTitle}`}`,
                        name,
                      ]}
                    />
                    <Legend wrapperStyle={{ color: '#9ca3af', fontSize: 12 }} />
                    <Bar dataKey="RAG" fill="#4b5563" radius={[3, 3, 0, 0]} />
                    <Bar dataKey="DCAE" fill="#3b82f6" radius={[3, 3, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Side by side results */}
            <div className="grid grid-cols-2 gap-6">
              {/* RAG results */}
              <div>
                <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">
                  RAG Results (Semantic Only)
                </h2>
                <div className="space-y-2">
                  {ragItems.map(item => (
                    <RAGCard key={item.id} item={item} />
                  ))}
                </div>
              </div>

              {/* DCAE results */}
              <div>
                <h2 className="text-sm font-semibold text-blue-400 uppercase tracking-wide mb-3">
                  DCAE Results (Multi-Dimensional)
                </h2>
                <div className="space-y-2">
                  {dcaeItems.map(item => (
                    <DCEACard key={item.id} item={item} />
                  ))}
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

function RAGCard({ item }: { item: RAGResult }) {
  return (
    <div className="card border-gray-700 text-sm">
      <div className="flex items-center gap-2 mb-1">
        <span className="text-xs text-gray-500">#{item.rank}</span>
        <SourceBadge sourceType={item.source_type} />
        <span className="ml-auto text-xs font-mono text-gray-400">
          {(item.semantic_score * 100).toFixed(1)}%
        </span>
      </div>
      <p className="text-xs text-gray-300 leading-snug truncate">{item.title}</p>
      <div className="mt-1">
        <ScoreBar label="Semantic" value={item.semantic_score} color="bg-gray-500" />
      </div>
    </div>
  )
}

function DCEACard({ item }: { item: ScoredContext }) {
  return (
    <div className="card border-blue-900/50 text-sm">
      <div className="flex items-center gap-2 mb-1">
        <span className="text-xs text-gray-500">#{item.rank}</span>
        <SourceBadge sourceType={item.source_type} />
        <RiskBadge risk={item.risk_level} />
        <span className="ml-auto text-xs font-bold text-blue-400">
          {(item.scores.final * 100).toFixed(1)}%
        </span>
      </div>
      <p className="text-xs text-gray-200 leading-snug truncate">{item.title}</p>
      <div className="mt-2 grid grid-cols-5 gap-1">
        {[
          ['S', item.scores.semantic, 'bg-blue-500'],
          ['T', item.scores.temporal, 'bg-green-500'],
          ['A', item.scores.authority, 'bg-purple-500'],
          ['R', item.scores.risk, 'bg-red-500'],
          ['P', item.scores.project, 'bg-yellow-500'],
        ].map(([label, val, color]) => (
          <div key={label as string} title={label as string}>
            <div className="text-xs text-gray-600 text-center mb-0.5">{label}</div>
            <div className="h-1 bg-gray-800 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full ${color}`}
                style={{ width: `${Math.round((val as number) * 100)}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
