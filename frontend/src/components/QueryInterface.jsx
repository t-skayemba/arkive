import { useState, useRef, useEffect } from 'react'
import { Send, Sparkles, Copy, Check, ShieldCheck } from 'lucide-react'
import { queryKnowledgeBase } from '../utils/api'
import SourceCard from './SourceCard'
import ReactMarkdown from 'react-markdown'

const SkeletonResponse = () => (
  <div className="flex flex-col items-start gap-3 w-full max-w-2xl">
    <div className="flex items-center gap-2">
      <div className="w-6 h-6 rounded bg-brand-accent/50 animate-pulse" />
      <div className="h-3 w-16 bg-white/10 rounded animate-pulse" />
    </div>
    <div className="bg-white/5 border border-white/10 rounded-2xl rounded-tl-none px-5 py-4 w-full space-y-2">
      <div className="h-3 bg-white/10 rounded animate-pulse w-full" />
      <div className="h-3 bg-white/10 rounded animate-pulse w-4/5" />
      <div className="h-3 bg-white/10 rounded animate-pulse w-3/5" />
    </div>
    <div className="grid grid-cols-2 gap-3 w-full">
      {[1, 2].map(i => (
        <div key={i} className="bg-white/5 border border-white/10 rounded-xl p-4 space-y-2">
          <div className="h-2 bg-white/10 rounded animate-pulse w-1/3" />
          <div className="h-3 bg-white/10 rounded animate-pulse w-2/3" />
          <div className="h-2 bg-white/10 rounded animate-pulse w-full" />
        </div>
      ))}
    </div>
  </div>
)

const getConfidence = (sources) => {
  if (!sources?.length) return null
  const topScore = Math.max(...sources.map(s => s.relevance_score))
  if (topScore >= 0.55) return { label: 'High Confidence', color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' }
  if (topScore >= 0.30) return { label: 'Medium Confidence', color: 'text-amber-400 bg-amber-500/10 border-amber-500/20' }
  return { label: 'Low Confidence', color: 'text-red-400 bg-red-500/10 border-red-500/20' }
}

const CopyButton = ({ text }) => {
  const [copied, setCopied] = useState(false)
  const copy = () => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  return (
    <button onClick={copy} className="text-slate-600 hover:text-slate-300 transition-colors mt-1" title="Copy to clipboard">
      {copied ? <Check size={13} className="text-emerald-400" /> : <Copy size={13} />}
    </button>
  )
}

export default function QueryInterface({ onQuery }) {
  const [input, setInput] = useState('')
  const [chat, setChat] = useState([])
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chat, loading])

  const ask = async () => {
    if (!input.trim() || loading) return
    const q = input.trim()
    setInput('')
    setChat(p => [...p, { role: 'user', content: q }])
    setLoading(true)

    try {
      const res = await queryKnowledgeBase(q)
      setChat(p => [...p, {
        role: 'assistant',
        content: res.answer,
        sources: res.sources
      }])
      // ← passes BOTH scores and full sources back to App
      onQuery?.(res.sources?.map(s => s.relevance_score) || [], res.sources || [])
    } catch (err) {
      const errMsg = err.response?.data?.detail || 'Something went wrong. Check that your backend is running.'
      setChat(p => [...p, { role: 'error', content: errMsg }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-80px)] bg-brand-surface rounded-2xl border border-white/5 shadow-2xl overflow-hidden">

      <div className="p-6 border-b border-white/5 flex items-center justify-between shrink-0">
        <h2 className="text-lg font-bold flex items-center gap-3">
          <Sparkles className="text-brand-accent" size={20} />
          Ask your knowledge base
        </h2>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-[10px] text-slate-500">
            <ShieldCheck size={12} className="text-slate-600" /> Powered by Anthropic API
          </div>
          <div className="flex items-center gap-2 bg-emerald-500/10 text-emerald-500 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest border border-emerald-500/20">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" /> Live
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-8 space-y-8">
        {chat.length === 0 && !loading && (
          <div className="flex flex-col items-center justify-center h-full text-center gap-4 opacity-40">
            <Sparkles size={40} className="text-brand-accent" />
            <div>
              <p className="font-semibold text-slate-300">Ready to answer questions</p>
              <p className="text-sm text-slate-500 mt-1">Upload documents, then ask anything about them</p>
            </div>
          </div>
        )}

        {chat.map((msg, i) => (
          <div key={i} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>

            {msg.role === 'user' && (
              <div className="bg-brand-accent text-white rounded-2xl rounded-tr-none px-5 py-3 max-w-lg text-sm leading-relaxed">
                {msg.content}
              </div>
            )}

            {msg.role === 'assistant' && (() => {
              const confidence = getConfidence(msg.sources)
              return (
                <div className="flex flex-col items-start gap-3 w-full max-w-2xl">
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded bg-brand-accent flex items-center justify-center text-[10px] font-bold shrink-0">A</div>
                    <span className="text-[11px] font-bold text-slate-400 uppercase tracking-widest">Arkive</span>
                    {confidence && (
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${confidence.color}`}>
                        {confidence.label}
                      </span>
                    )}
                  </div>
                  <div className="flex items-start gap-2 w-full">
                    {/* ← ReactMarkdown renders **bold**, ## headers, lists properly */}
                    <div className="bg-white/5 border border-white/10 rounded-2xl rounded-tl-none px-5 py-4 text-sm leading-relaxed flex-1 prose prose-invert prose-sm max-w-none">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                    <CopyButton text={msg.content} />
                  </div>
                  {msg.sources?.length > 0 && (
                    <div className="w-full">
                      <p className="text-[10px] text-slate-600 uppercase font-bold mb-2 ml-1">Sources used</p>
                      <div className="grid grid-cols-2 gap-3">
                        {msg.sources.map((s, j) => <SourceCard key={j} source={s} index={j} />)}
                      </div>
                    </div>
                  )}
                </div>
              )
            })()}

            {msg.role === 'error' && (
              <div className="bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl px-5 py-3 text-sm max-w-lg">
                ⚠️ {msg.content}
              </div>
            )}
          </div>
        ))}

        {loading && <SkeletonResponse />}
        <div ref={bottomRef} />
      </div>

      <div className="p-6 bg-white/[0.02] border-t border-white/5 shrink-0">
        <div className="flex gap-3 items-center bg-black/30 border border-white/10 rounded-xl px-4 py-3 focus-within:border-brand-accent/50 transition-all">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && ask()}
            placeholder="Ask a question about your documents..."
            className="flex-1 bg-transparent text-sm text-slate-200 placeholder-slate-600 outline-none border-none ring-0 focus:ring-0"
          />
          <button
            onClick={ask}
            disabled={!input.trim() || loading}
            className="bg-brand-accent hover:bg-indigo-500 disabled:bg-slate-700 disabled:cursor-not-allowed p-2 rounded-lg transition-all shadow-lg shadow-indigo-500/20 shrink-0"
          >
            <Send size={16} />
          </button>
        </div>
        <p className="text-[10px] text-slate-700 mt-2 text-center">
          Answers are grounded in your uploaded documents only
        </p>
      </div>
    </div>
  )
}