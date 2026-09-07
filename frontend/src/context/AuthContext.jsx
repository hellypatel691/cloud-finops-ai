import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import client from '../api/client'
import { getMe, refresh } from '../api/auth'

const AuthContext = createContext(null)

const TOKEN_KEY   = 'cfai_access_token'
const REFRESH_KEY = 'cfai_refresh_token'

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null)
  const [loading, setLoading] = useState(true)

  // ── Attach token to every axios request ──────────────────────────────────
  useEffect(() => {
    const interceptor = client.interceptors.request.use((config) => {
      const token = localStorage.getItem(TOKEN_KEY)
      if (token) config.headers.Authorization = `Bearer ${token}`
      return config
    })
    return () => client.interceptors.request.eject(interceptor)
  }, [])

  // ── Auto-refresh on 401 ───────────────────────────────────────────────────
  useEffect(() => {
    const interceptor = client.interceptors.response.use(
      (res) => res,
      async (err) => {
        const original = err.config
        if (err.response?.status === 401 && !original._retry) {
          original._retry = true
          const rt = localStorage.getItem(REFRESH_KEY)
          if (rt) {
            try {
              const tokens = await refresh(rt)
              localStorage.setItem(TOKEN_KEY,   tokens.access_token)
              localStorage.setItem(REFRESH_KEY, tokens.refresh_token)
              original.headers.Authorization = `Bearer ${tokens.access_token}`
              return client(original)
            } catch {
              logout()
            }
          }
        }
        const message = err.response?.data?.detail ?? err.message ?? 'Unknown error'
        return Promise.reject(new Error(message))
      }
    )
    return () => client.interceptors.response.eject(interceptor)
  }, [])

  // ── Restore session on mount ──────────────────────────────────────────────
  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (token) {
      getMe()
        .then(setUser)
        .catch(() => { localStorage.removeItem(TOKEN_KEY); localStorage.removeItem(REFRESH_KEY) })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const saveTokens = useCallback((tokens) => {
    localStorage.setItem(TOKEN_KEY,   tokens.access_token)
    localStorage.setItem(REFRESH_KEY, tokens.refresh_token)
  }, [])

  const loginUser = useCallback(async (tokens) => {
    saveTokens(tokens)
    const me = await getMe()
    setUser(me)
    return me
  }, [saveTokens])

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_KEY)
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, loginUser, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
