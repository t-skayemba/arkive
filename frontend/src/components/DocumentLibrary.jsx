import { useState, useEffect } from 'react'
import { Trash2, Eye } from 'lucide-react'
import { listDocuments, deleteDocument } from '../utils/api'
import DocumentPreview from './DocumentPreview'

export default function DocumentLibrary({ refreshTrigger, activeSourcesByDoc }) {
  const [docs, setDocs] = useState([])
  const [preview, setPreview] = useState(null) // { documentId, filename, excerpts }

  const fetchDocs = () => {
    listDocuments().then(data => setDocs(data.documents)).catch(console.error)
  }

  useEffect(() => { fetchDocs() }, [refreshTrigger])

  const remove = async (e, id) => {
    e.stopPropagation()
    if (confirm('Remove from knowledge base?')) {
      await deleteDocument(id)
      fetchDocs()
    }
  }

  const openPreview = (doc) => {
    const excerpts = activeSourcesByDoc?.[doc.filename] || []
    setPreview({ documentId: doc.document_id, filename: doc.filename, excerpts })
  }

  return (
    <>
      <div className="space-y-4">
        <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest px-1">
          Library
        </h3>

        {docs.length === 0 && (
          <p className="text-[11px] text-slate-600 px-1">No documents uploaded yet.</p>
        )}

        <div className="space-y-2">
          {docs.map((doc, i) => {
            const hasHighlights = activeSourcesByDoc?.[doc.filename]?.length > 0
            return (
              <div
                key={doc.document_id}
                onClick={() => openPreview(doc)}
                className={`group flex items-center justify-between p-2 rounded-lg cursor-pointer transition-all
                  ${hasHighlights
                    ? 'bg-indigo-500/10 border border-indigo-500/20'
                    : 'hover:bg-white/5 border border-transparent'
                  }`}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className={`w-2 h-2 rounded-full shrink-0 ${['bg-purple-500', 'bg-emerald-500', 'bg-amber-500'][i % 3]}`} />
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-slate-200 leading-tight truncate">{doc.filename}</p>
                    <p className="text-[11px] text-slate-500">
                      {doc.total_chunks} chunks
                      {hasHighlights && <span className="text-indigo-400 ml-1">· cited</span>}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-1 shrink-0">
                  <Eye size={12} className="text-slate-600 opacity-0 group-hover:opacity-100 transition-all" />
                  <button
                    onClick={(e) => remove(e, doc.document_id)}
                    className="opacity-0 group-hover:opacity-100 text-slate-600 hover:text-red-400 transition-all p-1"
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Preview modal */}
      {preview && (
        <DocumentPreview
          documentId={preview.documentId}
          filename={preview.filename}
          excerpts={preview.excerpts}
          onClose={() => setPreview(null)}
        />
      )}
    </>
  )
}