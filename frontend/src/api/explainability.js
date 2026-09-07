import client from './client'

export const getExplainability = (orgId) =>
  client.get(`/organizations/${orgId}/explainability/`).then(r => r.data)
