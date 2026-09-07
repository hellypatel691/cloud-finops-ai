import client from './client'

export const getAnomalies = (orgId) =>
  client.get(`/organizations/${orgId}/anomalies/`).then(r => r.data)
