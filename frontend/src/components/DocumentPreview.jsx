import { useState, useEffect } from 'react'
import { X, FileText, Loader2 } from 'lucide-react'
import { getDocumentContent } from '../utils/api'

const HighlightedText = ({ text, excerpts = [] }) => {
  if (!excerpts.length) {
    return <span className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">{text}</span>
  }

  let parts = [{ content: text, highlighted: false }]

  for (const excerpt of excerpts) {
    const search = excerpt.trim().substring(0, 80)
    if (!search) continue

    const nextParts = []
    for (const part of parts) {
      if (part.highlighted) {
        nextParts.push(part)
        continue
      }
      const idx = part.content.indexOf(search)
      if (idx === -1) {
        nextParts.push(part)
      } else {
        if (idx > 0) {
          nextParts.push({ content: part.content.substring(0, idx), highlighted: false })
        }
        nextParts.push({ content: part.content.substring(idx, idx + search.length), highlighted: true })
        nextParts.push({ content: part.content.substring(idx + search.length), highlighted: false })
      }
    }
    parts = nextParts
  }

  return (
    <span className="text-sm leading-relaxed whitespace-pre-wrap">
      {parts.map((part, i) =>
        part.highlighted
          ? <mark key={i} className="bg-indigo-500/30 text-indigo-200 rounded px-0.5 not-italic">{part.content}</mark>
          : <span key={i} className="text-slate-300">{part.content}</span>
      )}
    </span>
  )
}

export default function DocumentPreview({ documentId, filename, excerpts = [], onClose }) {
  const [content, setContent] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    setError(null)
    getDocumentContent(documentId)
      .then(data => setContent(data.content))
      .catch(() => setError('Could not load document content.'))
      .finally(() => setLoading(false))
  }, [documentId])

  return (
    <div
      className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-6"
      onClick={onClose}
    >
      <div
        className="bg-brand-surface border border-white/10 rounded-2xl w-full max-w-3xl max-h-[80vh] flex flex-col shadow-2xl"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 shrink-0">
          <div className="flex items-center gap-3">
            <FileText size={18} className="text-brand-accent" />
            <div>
              <p className="font-semibold text-slate-200 text-sm">{filename}</p>
              {excerpts.length > 0 && (
                <p className="text-[10px] text-indigo-400">
                  {excerpts.length} relevant passage{excerpts.length > 1 ? 's' : ''} highlighted
                </p>
              )}
            </div>
          </div>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-300 transition-colors">
            <X size={18} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-5">
          {loading && (
            <div className="flex items-center justify-center py-12 gap-3 text-slate-500">
              <Loader2 size={20} className="animate-spin" />
              <span className="text-sm">Loading document...</span>
            </div>
          )}
          {error && (
            <p className="text-red-400 text-sm text-center py-8">{error}</p>
          )}
          {content && (
            <HighlightedText text={content} excerpts={excerpts} />
          )}
        </div>

        {/* Footer */}
        {excerpts.length > 0 && (
          <div className="px-6 py-3 border-t border-white/10 bg-indigo-500/5 shrink-0">
            <p className="text-[10px] text-indigo-400">
              ◆ Highlighted passages were used to answer your last question
            </p>
          </div>
        )}
      </div>
    </div>
  )
}