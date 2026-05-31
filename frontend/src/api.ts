import axios from 'axios'
import type { QueryRequest, QueryResponse, GraphData, Project, UserProfile } from './types'

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const api = axios.create({ baseURL: `${BASE}/api/v1` })

export const runQuery = (req: QueryRequest) =>
  api.post<QueryResponse>('/query', req).then(r => r.data)

export const fetchGraph = () =>
  api.get<GraphData>('/graph').then(r => r.data)

export const fetchNodeNeighborhood = (id: string, depth = 2) =>
  api.get<GraphData>(`/graph/node/${id}?depth=${depth}`).then(r => r.data)

export const fetchProjects = () =>
  api.get<Project[]>('/projects').then(r => r.data)

export const fetchProfiles = () =>
  api.get<UserProfile[]>('/profiles').then(r => r.data)

export const fetchContextList = (params?: { source_type?: string; project?: string }) =>
  api.get('/context', { params }).then(r => r.data)

export const fetchContextDetail = (id: string) =>
  api.get(`/context/${id}`).then(r => r.data)

export const checkHealth = () =>
  api.get('/health').then(r => r.data)
