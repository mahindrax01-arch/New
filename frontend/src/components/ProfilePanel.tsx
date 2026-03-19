import type { DashboardSummary, User } from '../types'
import { getInitials } from '../lib/format'

type Props = {
  user: User
  summary: DashboardSummary | null
  onLogout: () => Promise<void>
}

const SUMMARY_ITEMS = [
  { key: 'friends_count', label: 'Friends' },
  { key: 'posts_count', label: 'Posts' },
  { key: 'pending_requests', label: 'Requests' },
  { key: 'unread_notifications', label: 'Unread' },
] as const

export function ProfilePanel({ user, summary, onLogout }: Props) {
  return (
    <section className="rounded-[28px] border border-white/50 bg-white/85 p-5 shadow-[0_24px_80px_rgba(15,23,42,0.12)] backdrop-blur">
      <div className="rounded-[24px] bg-[linear-gradient(135deg,#1d4ed8_0%,#0f766e_100%)] p-5 text-white">
        <div className="flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-white/15 text-xl font-semibold tracking-[0.18em]">
            {getInitials(user.username)}
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.28em] text-white/70">Personal profile</p>
            <h2 className="font-display text-2xl">{user.username}</h2>
            <p className="mt-1 text-sm text-white/80">{user.headline}</p>
          </div>
        </div>

        <div className="mt-5 flex items-center justify-between rounded-2xl border border-white/10 bg-white/10 px-4 py-3 text-sm">
          <div>
            <div className="text-[11px] uppercase tracking-[0.22em] text-white/65">Role</div>
            <div className="mt-1 font-semibold capitalize">{user.role}</div>
          </div>
          <button
            onClick={() => {
              void onLogout().catch(() => undefined)
            }}
            className="rounded-full border border-white/20 px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-white transition hover:bg-white/10"
          >
            Sign out
          </button>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3">
        {SUMMARY_ITEMS.map((item) => (
          <div key={item.key} className="rounded-3xl border border-slate-200/70 bg-slate-50/80 px-4 py-4">
            <div className="text-[11px] uppercase tracking-[0.2em] text-slate-500">{item.label}</div>
            <div className="mt-2 text-2xl font-semibold text-slate-900">
              {summary ? summary[item.key] : '--'}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 rounded-3xl border border-amber-200 bg-amber-50 px-4 py-4 text-sm text-amber-900">
        Stronger defaults are active: strict password policy, write rate limiting, security headers, and safer backend ID validation.
      </div>
    </section>
  )
}
