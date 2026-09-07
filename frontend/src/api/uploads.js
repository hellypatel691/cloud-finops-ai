import client from './client'
import axios from 'axios'

const base = (orgId) => `/organizations/${orgId}/uploads`

export const getUploads = (orgId)      => client.get(`${base(orgId)}/`).then(r => r.data)
export const getUpload  = (orgId, id)  => client.get(`${base(orgId)}/${id}`).then(r => r.data)

export const uploadCSV = (orgId, file, projectId = null) => {
  const form = new FormData()
  form.append('file', file)
  const qs  = projectId ? `?project_id=${projectId}` : ''
  return axios.post(`/api/v1${base(orgId)}/${qs}`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then(r => r.data)
}
