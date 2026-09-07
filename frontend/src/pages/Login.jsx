import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { Zap, Eye, EyeOff } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { login } from '../api/auth'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'

export default function Login() {
  const { loginUser } = useAuth()
  const navigate      = useNavigate()
  const location      = useLocation()
  const from          = location.state?.from?.pathname ?? '/dashboard'

  const [email, setEmail]     = useState('')
  const [password, setPassword] = useState('')
  const [showPw, setShowPw]   = useState(false)
  const [error, setError]     = useState('')
  const [loading, setLoading] = useState(false)

  const handle = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const tokens = await login(email, password)
      await loginUser(tokens)
      navigate(from, { replace: true })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-bg flex items-center justify-center p-4">
      <div className="w-full max-w-sm flex flex-col gap-8">

        {/* Logo */}
        <div className="flex flex-col items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-accent flex items-center justify-center shadow-glow">
            <Zap size={22} className="text-white" />
          </div>
          <div className="text-center">
            <h1 className="text-lg font-semibold text-primary">Cloud FinOps AI</h1>
            <p className="text-xs text-secondary mt-1">Sign in to your account</p>
          </div>
        </div>

        {/* Card */}
        <div className="card p-6 flex flex-col gap-5">
          <form onSubmit={handle} className="flex flex-col gap-4">
            <Input
              label="Email"
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="you@company.com"
              required
            />

            <div className="relative">
              <Input
                label="Password"
                type={showPw ? 'text' : 'password'}
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
              <button
                type="button"
                onClick={() => setShowPw(p => !p)}
                className="absolute right-3 top-7 text-secondary hover:text-primary transition-colors"
              >
                {showPw ? <EyeOff size={14} /> : <Eye size={14} />}
              </button>
            </div>

            {error && (
              <p className="text-xs text-danger bg-danger/10 rounded-xl px-3 py-2">{error}</p>
            )}

            <Button type="submit" disabled={loading} className="w-full justify-center mt-1">
              {loading ? 'Signing in…' : 'Sign In'}
            </Button>
          </form>

          <p className="text-center text-xs text-secondary">
            Don't have an account?{' '}
            <Link to="/register" className="text-accent hover:text-accent-light transition-colors">
              Create one
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
