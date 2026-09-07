import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Zap, Eye, EyeOff } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { register, login } from '../api/auth'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'

export default function Register() {
  const { loginUser } = useAuth()
  const navigate      = useNavigate()

  const [form, setForm]       = useState({ email: '', password: '', full_name: '' })
  const [showPw, setShowPw]   = useState(false)
  const [error, setError]     = useState('')
  const [loading, setLoading] = useState(false)

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handle = async (e) => {
    e.preventDefault()
    setError('')
    if (form.password.length < 8) { setError('Password must be at least 8 characters.'); return }
    setLoading(true)
    try {
      await register(form)
      const tokens = await login(form.email, form.password)
      await loginUser(tokens)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-bg flex items-center justify-center p-4">
      <div className="w-full max-w-sm flex flex-col gap-8">

        <div className="flex flex-col items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-accent flex items-center justify-center shadow-glow">
            <Zap size={22} className="text-white" />
          </div>
          <div className="text-center">
            <h1 className="text-lg font-semibold text-primary">Cloud FinOps AI</h1>
            <p className="text-xs text-secondary mt-1">Create your account</p>
          </div>
        </div>

        <div className="card p-6 flex flex-col gap-5">
          <form onSubmit={handle} className="flex flex-col gap-4">
            <Input
              label="Full Name (optional)"
              value={form.full_name}
              onChange={set('full_name')}
              placeholder="Alice Smith"
            />
            <Input
              label="Email"
              type="email"
              value={form.email}
              onChange={set('email')}
              placeholder="you@company.com"
              required
            />
            <div className="relative">
              <Input
                label="Password"
                type={showPw ? 'text' : 'password'}
                value={form.password}
                onChange={set('password')}
                placeholder="Min 8 characters"
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
              {loading ? 'Creating account…' : 'Create Account'}
            </Button>
          </form>

          <p className="text-center text-xs text-secondary">
            Already have an account?{' '}
            <Link to="/login" className="text-accent hover:text-accent-light transition-colors">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
