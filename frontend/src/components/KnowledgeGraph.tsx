import { useCallback, useMemo } from 'react'
import ReactFlow, {
  Node, Edge, Background, Controls, MiniMap,
  useNodesState, useEdgesState, MarkerType,
} from 'reactflow'
import 'reactflow/dist/style.css'
import type { GraphData } from '../types'

const NODE_COLORS: Record<string, string> = {
  ContextObject: '#1d4ed8',
  Person: '#7c3aed',
  Project: '#059669',
}

const EDGE_COLORS: Record<string, string> = {
  OWNS: '#6b7280',
  DEPENDS_ON: '#f59e0b',
  RELATED_TO: '#3b82f6',
  IMPLEMENTED_BY: '#10b981',
  CREATED_BY: '#8b5cf6',
  SUPERSEDES: '#ef4444',
  BLOCKS: '#f97316',
  REFERENCES: '#6366f1',
  BELONGS_TO: '#14b8a6',
}

interface Props {
  data: GraphData
  onNodeClick?: (nodeId: string) => void
}

function buildLayout(graphData: GraphData): { nodes: Node[]; edges: Edge[] } {
  const nodeTypes: Record<string, string[]> = {}
  graphData.nodes.forEach(n => {
    if (!nodeTypes[n.node_type]) nodeTypes[n.node_type] = []
    nodeTypes[n.node_type].push(n.id)
  })

  const positions: Record<string, { x: number; y: number }> = {}
  const typeOrder = ['Project', 'Person', 'ContextObject']
  let xOffset = 0

  typeOrder.forEach(type => {
    const ids = nodeTypes[type] || []
    ids.forEach((id, i) => {
      positions[id] = {
        x: xOffset + (i % 4) * 200,
        y: Math.floor(i / 4) * 120 + 50,
      }
    })
    xOffset += Math.ceil(ids.length / 4) * 200 + 100
  })

  const nodes: Node[] = graphData.nodes.map(n => ({
    id: n.id,
    position: positions[n.id] || { x: Math.random() * 800, y: Math.random() * 600 },
    data: {
      label: (
        <div className="text-center">
          <div className="text-xs font-medium truncate max-w-32">
            {n.label.length > 30 ? n.label.slice(0, 27) + '…' : n.label}
          </div>
          <div className="text-xs opacity-60">{n.node_type}</div>
        </div>
      ),
    },
    style: {
      background: (NODE_COLORS[n.node_type] || '#374151') + '33',
      border: `1px solid ${NODE_COLORS[n.node_type] || '#374151'}`,
      borderRadius: 8,
      color: '#f9fafb',
      fontSize: 11,
      padding: '6px 10px',
      minWidth: 140,
    },
  }))

  const edgeIdSet = new Set<string>()
  const edges: Edge[] = graphData.edges.flatMap(e => {
    const edgeId = `${e.source}-${e.relationship}-${e.target}`
    if (edgeIdSet.has(edgeId)) return []
    edgeIdSet.add(edgeId)
    return [{
      id: edgeId,
      source: e.source,
      target: e.target,
      label: e.relationship.replace(/_/g, ' ').toLowerCase(),
      labelStyle: { fill: '#9ca3af', fontSize: 9 },
      style: { stroke: EDGE_COLORS[e.relationship] || '#4b5563', strokeWidth: 1.5 },
      markerEnd: { type: MarkerType.ArrowClosed, color: EDGE_COLORS[e.relationship] || '#4b5563' },
      animated: e.relationship === 'BLOCKS',
    }]
  })

  return { nodes, edges }
}

export function KnowledgeGraph({ data, onNodeClick }: Props) {
  const { nodes: initialNodes, edges: initialEdges } = useMemo(() => buildLayout(data), [data])
  const [nodes, , onNodesChange] = useNodesState(initialNodes)
  const [edges, , onEdgesChange] = useEdgesState(initialEdges)

  const handleNodeClick = useCallback((_: unknown, node: Node) => {
    onNodeClick?.(node.id)
  }, [onNodeClick])

  return (
    <div className="w-full h-full bg-gray-950 rounded-xl overflow-hidden">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        fitView
        attributionPosition="bottom-right"
      >
        <Background color="#374151" gap={24} size={1} />
        <Controls className="!bg-gray-900 !border-gray-700" />
        <MiniMap
          nodeColor={n => {
            const nodeType = data.nodes.find(d => d.id === n.id)?.node_type || ''
            return NODE_COLORS[nodeType] || '#374151'
          }}
          style={{ background: '#111827', border: '1px solid #374151' }}
        />
      </ReactFlow>
    </div>
  )
}
