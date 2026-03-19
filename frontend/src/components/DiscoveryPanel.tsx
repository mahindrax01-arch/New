import type { DiscoverUser } from '../types'
import { getInitials } from '../lib/format'

type Props = {
  query: string
  results: DiscoverUser[]
  loading: boolean
  onQueryChange: (value: string) => void
  onSendRequest: (receiverId: string) => Promise<void>
}

const STATUS_COPY: Record<DiscoverUser['relationship_status'], string> = {
  friend: 'Connected',
  incoming_request: 'Needs response',
  outgoing_request: 'Request sent',
  none: 'Available',
}

export function DiscoveryPanel({ query, results, loading, onQueryChange, onSendRequest }: Props) {
  return (
    <section className="rounded-[28px] border border-white/50 bg-white/85 p-5 shadow-[0_24px_80px_rgba(15,23,42,0.12)] backdrop-blur">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-[11px] uppercase tracking-[0.22em] text-sky-700">Discover people</p>
          <h2 className="mt-1 font-display text-2xl text-slate-950">Grow your network</h2>
        </div>
        {loading && <span className="text-xs font-medium text-slate-500">Searching...</span>}
      </div>

      <input
        className="mt-4 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-400 focus:bg-white"
        placeholder="Search by username or email"
        value={query}
        onChange={(event) => onQueryChange(event.target.value)}
      />

      <div className="mt-4 space-y-3">
        {results.length === 0 && (
          <div className="rounded-3xl border border-dashed border-slate-200 px-4 py-6 text-center text-sm text-slate-500">
            No profiles match that search yet.
          </div>
        )}

        {results.map((profile) => (
          <article key={profile.id} className="flex items-start gap-4 rounded-3xl border border-slate-200/80 bg-slate-50/70 px-4 py-4">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-slate-900 text-sm font-semibold tracking-[0.16em] text-white">
              {getInitials(profile.username)}
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <h3 className="font-semibold text-slate-950">{profile.username}</h3>
                <span className="rounded-full bg-slate-900 px-2 py-1 text-[10px] uppercase tracking-[0.18em] text-white/80">
                  {STATUS_COPY[profile.relationship_status]}
                </span>
              </div>
              <p className="mt-1 text-sm text-slate-600">{profile.headline || profile.email}</p>
              <p className="mt-1 text-xs uppercase tracking-[0.16em] text-slate-400">{profile.role}</p>
            </div>
            <button
              onClick={() => {
                void onSendRequest(profile.id).catch(() => undefined)
              }}
              disabled={profile.relationship_status !== 'none'}
              className="rounded-full bg-sky-600 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-white transition hover:bg-sky-500 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-500"
            >
              Add
            </button>
          </article>
        ))}
      </div>
    </section>
  )
}
