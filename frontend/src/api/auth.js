import client from './client'
import axios from 'axios'

export const register = (data) =>
  client.post('/auth/register', data).then(r => r.data)

export const login = (email, password) =>
  client.post('/auth/login', { email, password }).then(r => r.data)

export const refresh = (refresh_token) =>
  client.post('/auth/refresh', { refresh_token }).then(r => r.data)

export const getMe = () =>
  client.get('/auth/me').then(r => r.data)

export const getMyOrganizations = () =>
  client.get('/auth/me/organizations').then(r => r.data)

export const joinOrganization = (orgId) =>
  client.post(`/auth/me/organizations/${orgId}`).then(r => r.data)

export const getDashboardSummary = (orgId) =>
  client.get(`/organizations/${orgId}/dashboard/summary`).then(r => r.data)
