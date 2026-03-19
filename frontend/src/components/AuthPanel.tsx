import { FormEvent, useState } from 'react'

import { useAuth } from '../hooks/useAuth'

const USERNAME_PATTERN = /^[A-Za-z0-9_.]{3,20}$/

export function AuthPanel() {
  const { login, register } = useAuth()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const usernameValid = USERNAME_PATTERN.test(username.trim())
  const passwordChecks = {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /\d/.test(password),
  }
  const passwordValid = Object.values(passwordChecks).every(Boolean)
  const passwordsMatch = mode === 'login' || password === confirmPassword

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)

    if (mode === 'register') {
      if (!usernameValid) {
        setError('Username must be 3-20 characters using letters, numbers, underscores, or periods.')
        return
      }
      if (!passwordValid) {
        setError('Password must be at least 8 characters and include uppercase, lowercase, and a number.')
        return
      }
      if (!passwordsMatch) {
        setError('Password confirmation does not match.')
        return
      }
    }

    setLoading(true)
    try {
      if (mode === 'login') {
        await login(email, password)
      } else {
        await register(email, username, password)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto grid w-full max-w-6xl overflow-hidden rounded-[36px] border border-white/50 bg-white/80 shadow-[0_40px_120px_rgba(15,23,42,0.18)] backdrop-blur lg:grid-cols-[1.15fr_0.85fr]">
      <section className="relative overflow-hidden bg-[linear-gradient(145deg,#0f172a_0%,#1d4ed8_55%,#0f766e_100%)] px-8 py-10 text-white sm:px-10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(255,255,255,0.18),transparent_28%),radial-gradient(circle_at_bottom_right,rgba(125,211,252,0.2),transparent_28%)]" />
        <div className="relative">
          <p className="text-[11px] uppercase tracking-[0.32em] text-sky-100/70">Social Graph Platform</p>
          <h1 className="mt-4 max-w-lg font-display text-4xl leading-tight sm:text-5xl">
            A sharper network feed with live updates, reactions, and trusted identity.
          </h1>
          <p className="mt-4 max-w-xl text-sm leading-7 text-sky-50/80">
            Join a tighter, faster social surface with real-time notifications, friend graph visibility, role-aware controls, and hardened session management.
          </p>

          <div className="mt-8 grid gap-3 sm:grid-cols-3">
            {['Live feed', 'Friend graph', 'Rotating tokens'].map((item) => (
              <div key={item} className="rounded-3xl border border-white/10 bg-white/10 px-4 py-4">
                <div className="text-[11px] uppercase tracking-[0.2em] text-white/60">Feature</div>
                <div className="mt-3 text-lg font-semibold">{item}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="px-6 py-8 sm:px-8 sm:py-10">
        <p className="text-[11px] uppercase tracking-[0.24em] text-sky-700">{mode === 'login' ? 'Welcome back' : 'Create account'}</p>
        <h2 className="mt-2 font-display text-3xl text-slate-950">
          {mode === 'login' ? 'Sign in to your feed' : 'Build your profile'}
        </h2>
        <p className="mt-2 text-sm text-slate-600">
          {mode === 'login'
            ? 'Use your existing credentials to continue where your network left off.'
            : 'Create a username and a password with uppercase, lowercase, a number, and at least 8 characters.'}
        </p>

        <form className="mt-8 space-y-4" onSubmit={onSubmit}>
          <input
            className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-400 focus:bg-white"
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            required
          />

          {mode === 'register' && (
            <input
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-400 focus:bg-white"
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              minLength={3}
              maxLength={20}
              autoComplete="username"
              required
            />
          )}

          <div className="relative">
            <input
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 pr-24 text-sm text-slate-900 outline-none transition focus:border-sky-400 focus:bg-white"
              type={showPassword ? 'text' : 'password'}
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              minLength={8}
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword((value) => !value)}
              className="absolute right-3 top-1/2 -translate-y-1/2 rounded-full border border-slate-200 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-slate-600 transition hover:border-slate-300 hover:text-slate-900"
            >
              {showPassword ? 'Hide' : 'Show'}
            </button>
          </div>

          {mode === 'register' && (
            <input
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-400 focus:bg-white"
              type={showPassword ? 'text' : 'password'}
              placeholder="Confirm password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              minLength={8}
              autoComplete="new-password"
              required
            />
          )}

          {mode === 'register' && (
            <div className="rounded-3xl border border-slate-200 bg-slate-50 px-4 py-4 text-sm text-slate-600">
              <div className={passwordChecks.length ? 'text-emerald-700' : 'text-slate-500'}>At least 8 characters</div>
              <div className={passwordChecks.uppercase ? 'text-emerald-700' : 'text-slate-500'}>One uppercase letter</div>
              <div className={passwordChecks.lowercase ? 'text-emerald-700' : 'text-slate-500'}>One lowercase letter</div>
              <div className={passwordChecks.number ? 'text-emerald-700' : 'text-slate-500'}>One number</div>
              <div className={passwordsMatch ? 'text-emerald-700' : 'text-slate-500'}>Passwords match</div>
            </div>
          )}

          {error && <p className="rounded-2xl bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</p>}

          <button
            className="w-full rounded-full bg-slate-950 px-5 py-3 text-sm font-semibold uppercase tracking-[0.18em] text-white transition hover:bg-sky-700 disabled:opacity-50"
            type="submit"
            disabled={loading}
          >
            {loading ? 'Processing...' : mode === 'login' ? 'Sign in' : 'Create account'}
          </button>
        </form>

        <div className="mt-6 rounded-3xl border border-slate-200 bg-slate-50 px-4 py-4 text-sm text-slate-600">
          Registration rules: username must be `3-20` characters using letters, numbers, `_` or `.`. Passwords must be `8+` characters with uppercase, lowercase, and a number.
        </div>

        <button
          className="mt-6 text-sm font-medium text-sky-700 transition hover:text-sky-900"
          onClick={() => {
            setMode(mode === 'login' ? 'register' : 'login')
            setError(null)
            setPassword('')
            setConfirmPassword('')
            setShowPassword(false)
          }}
        >
          {mode === 'login' ? 'Need an account? Register now' : 'Already have an account? Sign in'}
        </button>
      </section>
    </div>
  )
}
