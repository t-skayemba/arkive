export default function SourceCard({ source, index }) {
  const score = source.relevance_score
  const scoreColor = score >= 0.65 ? 'text-emerald-400' : score >= 0.35 ? 'text-amber-400' : 'text-red-400'

  return (
    <div className="bg-white/5 border border-white/10 rounded-xl p-4 hover:border-white/20 transition-all">
      <div className="flex justify-between items-center mb-2">
        <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-tight">
          Source {index + 1}
        </span>
        <span className={`text-[10px] font-mono font-bold ${scoreColor}`}>
          {(score * 100).toFixed(0)}%
        </span>
      </div>
      <p className="text-xs font-semibold text-slate-300 truncate">{source.filename}</p>
      {source.page_number > 0 && (
        <p className="text-[10px] text-slate-500 mb-2">p.{source.page_number}</p>
      )}
      <p className="text-[11px] text-slate-400 leading-relaxed line-clamp-3 italic mt-1">
        "{source.relevant_excerpt}"
      </p>
    </div>
  )
}