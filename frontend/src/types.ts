export interface ScoreBreakdown {
  semantic: number
  temporal: number
  half_life?: number
  authority: number
  risk: number
  project: number
  final: number
  explanation: Record<string, string>
}

export interface ScoredContext {
  id: string
  title: string
  content: string
  source_type: string
  owner: string
  project: string
  risk_level: string
  age_days: number
  created_at: string
  scores: ScoreBreakdown
  rank: number
  tags: string[]
}

export interface RAGResult {
  id: string
  title: string
  content: string
  source_type: string
  semantic_score: number
  rank: number
}

export interface AssembledPrompt {
  system_prompt: string
  user_prompt: string
  context_window_used: number
  context_items_count: number
  profile_adaptation: string
}

export interface QueryResponse {
  query: string
  query_id: string
  project_detected: string | null
  selected_context: ScoredContext[]
  assembled_prompt: AssembledPrompt
  rag_comparison: RAGResult[] | null
  processing_time_ms: number
  total_candidates: number
}

export interface GraphNode {
  id: string
  label: string
  node_type: string
  properties: Record<string, unknown>
}

export interface GraphEdge {
  source: string
  target: string
  relationship: string
  weight: number
}

export interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
  node_count: number
  edge_count: number
}

export interface Project {
  id: string
  name: string
  description: string | null
  status: string
  context_count: number
}

export interface UserProfile {
  id: string
  name: string
  role: string
  verbosity: string
  output_style: string
  risk_tolerance: string
}

export interface QueryRequest {
  query: string
  user_profile_id?: string
  project_filter?: string
  top_k?: number
  weights?: Record<string, number>
  include_rag_comparison?: boolean
}
