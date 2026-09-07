import client from './client'

const base = (orgId) => `/organizations/${orgId}/projects`

export const getProjects   = (orgId)           => client.get(`${base(orgId)}/`).then(r => r.data)
export const getProject    = (orgId, id)        => client.get(`${base(orgId)}/${id}`).then(r => r.data)
export const createProject = (orgId, data)      => client.post(`${base(orgId)}/`, data).then(r => r.data)
export const updateProject = (orgId, id, data)  => client.put(`${base(orgId)}/${id}`, data).then(r => r.data)
export const deleteProject = (orgId, id)        => client.delete(`${base(orgId)}/${id}`)
