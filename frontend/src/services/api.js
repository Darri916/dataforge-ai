import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({ baseURL: BASE_URL })

export const uploadFile = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/api/upload/', formData)
}

export const generateSynthetic = (fileId, synthesizer, numRows) =>
  api.post('/api/generate/', { file_id: fileId, synthesizer, num_rows: numRows })

export const getQuality = (fileId) => api.get(`/api/quality/${fileId}`)

export const getPrivacy = (fileId) => api.get(`/api/privacy/${fileId}`)

export const downloadCSV = (fileId) =>
  api.get(`/api/export/${fileId}/csv`, { responseType: 'blob' })

export const downloadReport = (fileId) =>
  api.get(`/api/export/${fileId}/report`, { responseType: 'blob' })