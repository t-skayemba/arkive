import { useState, useRef } from 'react'
import { CloudUpload, Loader2 } from 'lucide-react'
import { uploadDocument } from '../utils/api'

export default function DocumentUpload({ onUploadSuccess }) {
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState(null)
  const fileInputRef = useRef(null)

  const handleFile = async (file) => {
    if (!file) return

    const MAX_MB = 20
    if (file.size > MAX_MB * 1024 * 1024) {
      setError(`File is too large. Maximum size is ${MAX_MB}MB.`)
      return
    }

    setIsUploading(true)
    setError(null)
    try {
      await uploadDocument(file)
      onUploadSuccess()
    } catch (err) {
      const msg = err.response?.data?.detail || 'Upload failed. Please try again.'
      setError(msg)
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="space-y-2">
      <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest px-1">Upload</h3>
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => { e.preventDefault(); setIsDragging(false); handleFile(e.dataTransfer.files[0]) }}
        onClick={() => fileInputRef.current.click()}
        className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all
          ${isDragging ? 'border-brand-accent bg-brand-accent/10' : 'border-slate-700 hover:border-slate-500'}`}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept=".pdf,.docx,.txt"
          onChange={(e) => handleFile(e.target.files[0])}
        />
        {isUploading ? (
          <Loader2 className="animate-spin mx-auto text-brand-accent" size={24} />
        ) : (
          <div className="flex flex-col items-center gap-2">
            <CloudUpload className="text-slate-500" size={28} />
            <p className="text-sm text-slate-400 font-medium">Drop a file or click to upload</p>
            <p className="text-[10px] text-slate-600">PDF · DOCX · TXT · max 20MB</p>
          </div>
        )}
      </div>

      {error && (
        <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-xs text-red-400">
          {error}
        </div>
      )}
    </div>
  )
}