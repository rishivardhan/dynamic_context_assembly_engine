import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import { QueryPage } from './pages/QueryPage'
import { GraphPage } from './pages/GraphPage'
import { ComparisonPage } from './pages/ComparisonPage'
import { BrainCircuit, Network, GitCompare } from 'lucide-react'
import clsx from 'clsx'

const navItems = [
  { to: '/', label: 'Query Engine', icon: BrainCircuit, end: true },
  { to: '/graph', label: 'Knowledge Graph', icon: Network },
  { to: '/compare', label: 'RAG vs DCAE', icon: GitCompare },
]

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen overflow-hidden">
        {/* Sidebar */}
        <aside className="w-56 flex-shrink-0 bg-gray-900 border-r border-gray-800 flex flex-col">
          <div className="p-4 border-b border-gray-800">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
                <BrainCircuit className="w-4 h-4 text-white" />
              </div>
              <div>
                <p className="text-sm font-bold text-white leading-none">DCAE</p>
                <p className="text-xs text-gray-500 leading-none mt-0.5">v1.0.0</p>
              </div>
            </div>
          </div>
          <nav className="flex-1 p-3 space-y-1">
            {navItems.map(({ to, label, icon: Icon, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) =>
                  clsx(
                    'flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors',
                    isActive
                      ? 'bg-blue-600/20 text-blue-400 font-medium'
                      : 'text-gray-400 hover:text-gray-100 hover:bg-gray-800'
                  )
                }
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                {label}
              </NavLink>
            ))}
          </nav>
          <div className="p-3 border-t border-gray-800">
            <p className="text-xs text-gray-600 text-center">
              Dynamic Context Assembly Engine
            </p>
          </div>
        </aside>

        {/* Main content */}
        <main className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<QueryPage />} />
            <Route path="/graph" element={<GraphPage />} />
            <Route path="/compare" element={<ComparisonPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
