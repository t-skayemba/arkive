import axios from 'axios'

const api = axios.create({ baseURL: '' })

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

export const queryKnowledgeBase = async (question, topK = 5) => {
  const res = await api.post('/query/', { question, top_k: topK })
  return res.data
}