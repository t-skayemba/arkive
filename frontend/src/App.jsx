import { useState, useEffect } from 'react'
import DocumentUpload from './components/DocumentUpload'
import DocumentLibrary from './components/DocumentLibrary'
import QueryInterface from './components/QueryInterface'
import { LayoutGrid, Database, MessageSquare, Target, ShieldCheck } from 'lucide-react'
import { listDocuments } from './utils/api'
import logoIcon from './assets/logo-icon.svg'

const Stat = ({ label, val, Icon }) => (
  <div className="bg-white/5 border border-white/5 rounded-xl p-4">
    <div className="flex justify-between items-start mb-1">
      <span className="text-2xl font-bold">{val}</span>
      <Icon size={14} className="text-slate-600" />
    </div>
    <p className="text-[10px] font-bold text-slate-500 uppercase">{label}</p>
  </div>
)

export default function App() {
  const [refresh, setRefresh] = useState(0)
  const [stats, setStats] = useState({ docs: 0, chunks: 0 })
  const [queryCount, setQueryCount] = useState(0)
  const [avgRelevance, setAvgRelevance] = useState(null)
  const [activeSourcesByDoc, setActiveSourcesByDoc] = useState({})

  useEffect(() => {
    listDocuments()
      .then(data => {
        const totalChunks = data.documents.reduce((sum, d) => sum + d.total_chunks, 0)
        setStats({ docs: data.documents.length, chunks: totalChunks })
      })
      .catch(console.error)
  }, [refresh])

  const handleNewQuery = (relevanceScores, sources) => {
    setQueryCount(n => n + 1)
    if (relevanceScores?.length > 0) {
      const avg = relevanceScores.reduce((a, b) => a + b, 0) / relevanceScores.length
      setAvgRelevance(prev => prev === null ? avg : (prev * 0.7 + avg * 0.3))
    }
    if (sources?.length) {
      const byDoc = {}
      sources.forEach(s => {
        const key = s.filename
        if (!byDoc[key]) byDoc[key] = []
        byDoc[key].push(s.relevant_excerpt)
      })
      setActiveSourcesByDoc(byDoc)
    }
  }

  return (
    <div className="flex min-h-screen bg-brand-dark text-slate-200 font-sans">

      {/* Sidebar */}
      <aside className="w-80 border-r border-white/5 p-8 flex flex-col gap-8 overflow-y-auto shrink-0">

        {/* Logo */}
        <div className="flex items-center gap-3">
          <img src={logoIcon} alt="Arkive" className="w-10 h-10 rounded-xl" />
          <div>
            <h1 className="text-xl font-bold leading-none">Arkive</h1>
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-tighter mt-1">Knowledge Base</p>
          </div>
        </div>

        {/* Privacy badge */}
        <div className="flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 rounded-lg px-3 py-2">
          <ShieldCheck size={14} className="text-emerald-400 shrink-0" />
          <div>
            <p className="text-[10px] font-bold text-emerald-400">Local Storage</p>
            <p className="text-[10px] text-slate-500">Files & vectors stored on your machine</p>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-3">
          <Stat label="Documents" val={stats.docs} Icon={Database} />
          <Stat label="Chunks" val={stats.chunks} Icon={LayoutGrid} />
          <Stat label="Queries" val={queryCount} Icon={MessageSquare} />
          <Stat
            label="Avg Relevance"
            val={avgRelevance !== null ? `${(avgRelevance * 100).toFixed(0)}%` : '—'}
            Icon={Target}
          />
        </div>

        <DocumentUpload onUploadSuccess={() => setRefresh(n => n + 1)} />

        {/* DocumentLibrary gets activeSourcesByDoc for highlighting */}
        <DocumentLibrary
          refreshTrigger={refresh}
          activeSourcesByDoc={activeSourcesByDoc}
        />

        <div className="mt-auto pt-8 border-t border-white/5 text-[10px] text-slate-600 font-medium">
          Built by <span className="text-slate-400">Tiana Kayemba</span><br />
          Arkive v1.0 — 2026
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 p-10 flex flex-col min-w-0">
        {/* QueryInterface gets handleNewQuery which now accepts both scores AND sources */}
        <QueryInterface onQuery={handleNewQuery} />
      </main>
    </div>
  )
}