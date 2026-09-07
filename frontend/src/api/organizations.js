import client from './client'

export const getOrganizations   = ()          => client.get('/organizations/').then(r => r.data)
export const getOrganization    = (id)        => client.get(`/organizations/${id}`).then(r => r.data)
export const createOrganization = (data)      => client.post('/organizations/', data).then(r => r.data)
export const updateOrganization = (id, data)  => client.put(`/organizations/${id}`, data).then(r => r.data)
export const deleteOrganization = (id)        => client.delete(`/organizations/${id}`)
