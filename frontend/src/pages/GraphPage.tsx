import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchGraph, fetchNodeNeighborhood, fetchContextDetail } from '../api'
import { KnowledgeGraph } from '../components/KnowledgeGraph'
import { SourceBadge, RiskBadge } from '../components/SourceBadge'
import { Loader2, X } from 'lucide-react'

export function GraphPage() {
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [graphMode, setGraphMode] = useState<'full' | 'neighborhood'>('full')

  const { data: fullGraph, isLoading } = useQuery({
    queryKey: ['graph'],
    queryFn: fetchGraph,
    staleTime: 60_000,
  })

  const { data: neighborhood } = useQuery({
    queryKey: ['neighborhood', selectedId],
    queryFn: () => fetchNodeNeighborhood(selectedId!, 2),
    enabled: !!selectedId && graphMode === 'neighborhood',
  })

  const { data: contextDetail } = useQuery({
    queryKey: ['context', selectedId],
    queryFn: () => fetchContextDetail(selectedId!),
    enabled: !!selectedId,
  })

  const displayGraph = graphMode === 'neighborhood' && neighborhood ? neighborhood : fullGraph

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="border-b border-gray-800 px-6 py-4 flex-shrink-0 flex items-center justify-between">
        <div>
          <h1 className="text-lg font-bold text-white">Knowledge Graph</h1>
          <p className="text-xs text-gray-500 mt-0.5">
            {fullGraph
              ? `${fullGraph.node_count} nodes · ${fullGraph.edge_count} edges`
              : 'Loading...'}
          </p>
        </div>
        <div className="flex gap-2">
          {(['full', 'neighborhood'] as const).map(m => (
            <button
              key={m}
              onClick={() => setGraphMode(m)}
              disabled={m === 'neighborhood' && !selectedId}
              className={`px-3 py-1 text-xs rounded-lg transition-colors disabled:opacity-30 ${
                graphMode === m ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-400 hover:text-gray-200'
              }`}
            >
              {m === 'full' ? 'Full Graph' : 'Neighborhood'}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Graph */}
        <div className="flex-1 relative">
          {isLoading && (
            <div className="absolute inset-0 flex items-center justify-center">
              <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
            </div>
          )}
          {displayGraph && (
            <KnowledgeGraph
              data={displayGraph}
              onNodeClick={(id) => {
                setSelectedId(id)
                setGraphMode('neighborhood')
              }}
            />
          )}
        </div>

        {/* Node detail panel */}
        {selectedId && contextDetail && (
          <div className="w-80 flex-shrink-0 border-l border-gray-800 overflow-auto">
            <div className="p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-gray-200">Node Detail</h3>
                <button
                  onClick={() => { setSelectedId(null); setGraphMode('full') }}
                  className="text-gray-600 hover:text-gray-300"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="space-y-3">
                <div className="flex flex-wrap gap-1">
                  <SourceBadge sourceType={contextDetail.source_type} />
                  <RiskBadge risk={contextDetail.risk_level} />
                </div>

                <h4 className="text-sm font-medium text-gray-100 leading-snug">
                  {contextDetail.title}
                </h4>

                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-gray-500">Project</span>
                    <p className="text-gray-300">{contextDetail.project}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Owner</span>
                    <p className="text-gray-300">{contextDetail.owner}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Importance</span>
                    <p className="text-gray-300">{'★'.repeat(contextDetail.importance)}</p>
                  </div>
                </div>

                <p className="text-xs text-gray-400 leading-relaxed line-clamp-6">
                  {contextDetail.content}
                </p>

                {contextDetail.tags?.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {contextDetail.tags.map((t: string) => (
                      <span key={t} className="badge bg-gray-800 text-gray-500">{t}</span>
                    ))}
                  </div>
                )}

                {contextDetail.related_nodes?.length > 0 && (
                  <div>
                    <p className="text-xs text-gray-500 mb-1">
                      Connected nodes ({contextDetail.related_nodes.length})
                    </p>
                    <div className="space-y-1">
                      {contextDetail.related_nodes.slice(0, 5).map((n: { id: string; node_type: string; label: string }) => (
                        <button
                          key={n.id}
                          onClick={() => setSelectedId(n.id)}
                          className="w-full text-left text-xs bg-gray-800 hover:bg-gray-700 px-2 py-1.5 rounded flex items-center gap-2"
                        >
                          <span className="text-gray-500">{n.node_type}</span>
                          <span className="text-gray-300 truncate">{n.label}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
