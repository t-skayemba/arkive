import { useState, useRef } from 'react'
import { CloudUpload, FileText, Loader2 } from 'lucide-react'
import { uploadDocument } from '../utils/api'

export default function DocumentUpload({ onUploadSuccess }) {
    const [isDragging, setIsDragging] = useState(false)
    const [isUploading, setIsUploading] = useState(false)
    const fileInputRef = useRef(null)

    const handleFile = async (file) => {
        if (!file) return
        setIsUploading(true)
        try {
            await uploadDocument(file)
            onUploadSuccess()
        } catch (err) {
            console.error(err)
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
                <input ref={fileInputRef} type="file" className="hidden" onChange={(e) => handleFile(e.target.files[0])} />
                {isUploading ? (
                    <Loader2 className="animate-spin mx-auto text-brand-accent" size={24} />
                ) : (
                    <div className="flex flex-col items-center gap-2">
                        <CloudUpload className="text-slate-500" size={28} />
                        <p className="text-sm text-slate-400 font-medium">Drop a file or click to upload</p>
                        <p className="text-[10px] text-slate-600">PDF • DOCX • TXT</p>
                    </div>
                )}
            </div>
        </div>
    )
}