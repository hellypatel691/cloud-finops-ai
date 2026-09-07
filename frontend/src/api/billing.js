import client from './client'

export const getBilling         = (orgId)         => client.get(`/organizations/${orgId}/billing/`).then(r => r.data)
export const getForecast = (orgId) =>
  client.get(`/organizations/${orgId}/forecast/`).then(r => r.data)
