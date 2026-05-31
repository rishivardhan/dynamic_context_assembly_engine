import { create } from 'zustand'
import type { QueryResponse, QueryRequest } from './types'

interface AppState {
  lastQuery: QueryRequest | null
  lastResponse: QueryResponse | null
  selectedProfileId: string
  selectedContextId: string | null
  setLastQuery: (q: QueryRequest) => void
  setLastResponse: (r: QueryResponse) => void
  setSelectedProfileId: (id: string) => void
  setSelectedContextId: (id: string | null) => void
}

export const useAppStore = create<AppState>((set) => ({
  lastQuery: null,
  lastResponse: null,
  selectedProfileId: '',
  selectedContextId: null,
  setLastQuery: (q) => set({ lastQuery: q }),
  setLastResponse: (r) => set({ lastResponse: r }),
  setSelectedProfileId: (id) => set({ selectedProfileId: id }),
  setSelectedContextId: (id) => set({ selectedContextId: id }),
}))
