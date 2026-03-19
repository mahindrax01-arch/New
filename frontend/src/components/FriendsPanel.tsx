import { FormEvent, useState } from 'react'

import type { Friend, OutgoingRequest, PendingRequest } from '../types'
import { formatRelativeTime, getInitials } from '../lib/format'

type Props = {
  friends: Friend[]
  pending: PendingRequest[]
  outgoing: OutgoingRequest[]
  onSendRequest: (identifier: string) => Promise<void>
  onRespond: (requestId: string, action: 'accept' | 'reject') => Promise<void>
  onCancel: (requestId: string) => Promise<void>
}

export function FriendsPanel({ friends, pending, outgoing, onSendRequest, onRespond, onCancel }: Props) {
  const [identifier, setIdentifier] = useState('')

  async function submitRequest(event: FormEvent) {
    event.preventDefault()
    const value = identifier.trim()
    if (!value) return
    try {
      await onSendRequest(value)
      setIdentifier('')
    } catch {
      // Global error banner is handled by the parent container.
    }
  }

  return (
    <section className="space-y-5 rounded-[28px] border border-white/50 bg-white/85 p-5 shadow-[0_24px_80px_rgba(15,23,42,0.12)] backdrop-blur">
      <div>
        <p className="text-[11px] uppercase tracking-[0.22em] text-sky-700">Connections</p>
        <h2 className="mt-1 font-display text-2xl text-slate-950">Friend graph</h2>
      </div>

      <form onSubmit={submitRequest} className="rounded-3xl border border-slate-200 bg-slate-50/80 p-4">
        <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Send request directly</div>
        <input
          className="mt-3 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-400"
          placeholder="Enter username or email"
          value={identifier}
          onChange={(event) => setIdentifier(event.target.value)}
        />
        <button className="mt-3 rounded-full bg-sky-600 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-white transition hover:bg-sky-500">
          Send request
        </button>
      </form>

      <div>
        <h3 className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Pending requests</h3>
        <div className="mt-3 space-y-3">
          {pending.length === 0 && (
            <div className="rounded-3xl border border-dashed border-slate-200 px-4 py-5 text-sm text-slate-500">
              No pending requests.
            </div>
          )}

          {pending.map((req) => (
            <div key={req.id} className="rounded-3xl border border-slate-200 bg-slate-50/80 p-4 text-sm">
              <div className="flex items-start gap-3">
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-slate-900 text-xs font-semibold tracking-[0.16em] text-white">
                  {getInitials(req.sender_username)}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="font-semibold text-slate-950">{req.sender_username}</div>
                  <div className="mt-1 text-slate-500">{req.sender_headline || 'Wants to connect with you.'}</div>
                  <div className="mt-2 text-[11px] uppercase tracking-[0.16em] text-slate-400">
                    {formatRelativeTime(req.created_at)}
                  </div>
                </div>
              </div>
              <div className="mt-4 flex gap-2">
                <button
                  onClick={() => {
                    void onRespond(req.id, 'accept').catch(() => undefined)
                  }}
                  className="rounded-full bg-emerald-600 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-white"
                >
                  Accept
                </button>
                <button
                  onClick={() => {
                    void onRespond(req.id, 'reject').catch(() => undefined)
                  }}
                  className="rounded-full border border-rose-200 bg-rose-50 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-rose-700"
                >
                  Reject
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Outgoing requests</h3>
        <div className="mt-3 space-y-3">
          {outgoing.length === 0 && (
            <div className="rounded-3xl border border-dashed border-slate-200 px-4 py-5 text-sm text-slate-500">
              No outgoing requests.
            </div>
          )}

          {outgoing.map((req) => (
            <div key={req.id} className="rounded-3xl border border-slate-200 bg-slate-50/80 p-4 text-sm">
              <div className="flex items-start gap-3">
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-sky-700 text-xs font-semibold tracking-[0.16em] text-white">
                  {getInitials(req.receiver_username)}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="font-semibold text-slate-950">{req.receiver_username}</div>
                  <div className="mt-1 text-slate-500">{req.receiver_headline || 'Awaiting response.'}</div>
                  <div className="mt-2 text-[11px] uppercase tracking-[0.16em] text-slate-400">
                    {formatRelativeTime(req.created_at)}
                  </div>
                </div>
              </div>
              <button
                onClick={() => {
                  void onCancel(req.id).catch(() => undefined)
                }}
                className="mt-4 rounded-full border border-slate-300 bg-white px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-slate-700"
              >
                Cancel
              </button>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Active friends</h3>
        <ul className="mt-3 space-y-3 text-sm text-slate-700">
          {friends.length === 0 && (
            <li className="rounded-3xl border border-dashed border-slate-200 px-4 py-5 text-slate-500">
              Start with discovery to build your network.
            </li>
          )}
          {friends.map((friend) => (
            <li key={friend.id} className="rounded-3xl border border-slate-200 bg-slate-50/80 px-4 py-4">
              <div className="flex items-start gap-3">
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-sky-700 text-xs font-semibold tracking-[0.16em] text-white">
                  {getInitials(friend.username)}
                </div>
                <div className="min-w-0">
                  <div className="font-semibold text-slate-950">{friend.username}</div>
                  <div className="mt-1 text-slate-500">{friend.headline || friend.email}</div>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}
