import client from './client'

export const getForecast = (orgId) =>
  client.get(`/organizations/${orgId}/forecast/`).then(r => r.data)
