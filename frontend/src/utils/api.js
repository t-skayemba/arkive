import axios from 'axios'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || ''

const api = axios.create({
  baseURL: BACKEND_URL,
})

export const uploadDocument = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  const res = await api.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return res.data
}

export const listDocuments = async () => {
  const res = await api.get('/documents/list')
  return res.data
}

export const deleteDocument = async (documentId) => {
  const res = await api.delete(`/documents/${documentId}`)
  return res.data
}

export const getDocumentContent = async (documentId) => {
  const res = await api.get(`/documents/${documentId}/content`)
  return res.data
}

export const queryKnowledgeBase = async (question, topK = 5, documentId = null) => {
  const body = { question, top_k: topK }
  if (documentId) body.document_id = documentId
  const res = await api.post('/query/', body)
  return res.data
}