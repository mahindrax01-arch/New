import { FormEvent, useEffect, useState } from 'react'

import type { User } from '../types'

type Props = {
  user: User
  onUpdateProfile: (headline: string, username: string) => Promise<void>
  onChangePassword: (currentPassword: string, newPassword: string) => Promise<void>
  onDeleteAccount: (password: string) => Promise<void>
}

export function AccountPanel({ user, onUpdateProfile, onChangePassword, onDeleteAccount }: Props) {
  const [username, setUsername] = useState(user.username)
  const [headline, setHeadline] = useState(user.headline)
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmNewPassword, setConfirmNewPassword] = useState('')
  const [deletePassword, setDeletePassword] = useState('')
  const [localError, setLocalError] = useState<string | null>(null)

  useEffect(() => {
    setUsername(user.username)
    setHeadline(user.headline)
  }, [user.headline, user.username])

  async function submitProfile(event: FormEvent) {
    event.preventDefault()
    setLocalError(null)
    try {
      await onUpdateProfile(headline, username)
    } catch {
      // Global error banner is handled by the parent container.
    }
  }

  async function submitPassword(event: FormEvent) {
    event.preventDefault()
    setLocalError(null)
    if (newPassword !== confirmNewPassword) {
      setLocalError('New password confirmation does not match.')
      return
    }
    try {
      await onChangePassword(currentPassword, newPassword)
      setCurrentPassword('')
      setNewPassword('')
      setConfirmNewPassword('')
    } catch {
      // Global error banner is handled by the parent container.
    }
  }

  async function submitDelete(event: FormEvent) {
    event.preventDefault()
    setLocalError(null)
    try {
      await onDeleteAccount(deletePassword)
    } catch {
      // Global error banner is handled by the parent container.
    }
  }

  return (
    <section className="space-y-5 rounded-[28px] border border-white/50 bg-white/85 p-5 shadow-[0_24px_80px_rgba(15,23,42,0.12)] backdrop-blur">
      <div>
        <p className="text-[11px] uppercase tracking-[0.22em] text-sky-700">Account controls</p>
        <h2 className="mt-1 font-display text-2xl text-slate-950">Profile and security</h2>
      </div>

      {localError && <p className="rounded-3xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{localError}</p>}

      <form onSubmit={submitProfile} className="rounded-3xl border border-slate-200 bg-slate-50/80 p-4">
        <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Profile details</div>
        <input
          className="mt-3 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-400"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          placeholder="Username"
          minLength={3}
          maxLength={20}
        />
        <textarea
          className="mt-3 w-full resize-none rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-400"
          value={headline}
          onChange={(event) => setHeadline(event.target.value)}
          placeholder="Headline"
          rows={3}
          maxLength={120}
        />
        <button className="mt-3 rounded-full bg-slate-900 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-white">
          Save profile
        </button>
      </form>

      <form onSubmit={submitPassword} className="rounded-3xl border border-slate-200 bg-slate-50/80 p-4">
        <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Change password</div>
        <input
          className="mt-3 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-400"
          type="password"
          value={currentPassword}
          onChange={(event) => setCurrentPassword(event.target.value)}
          placeholder="Current password"
          minLength={8}
        />
        <input
          className="mt-3 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-400"
          type="password"
          value={newPassword}
          onChange={(event) => setNewPassword(event.target.value)}
          placeholder="New password"
          minLength={8}
        />
        <input
          className="mt-3 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-400"
          type="password"
          value={confirmNewPassword}
          onChange={(event) => setConfirmNewPassword(event.target.value)}
          placeholder="Confirm new password"
          minLength={8}
        />
        <button className="mt-3 rounded-full bg-sky-600 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-white">
          Rotate password
        </button>
      </form>

      <form onSubmit={submitDelete} className="rounded-3xl border border-rose-200 bg-rose-50/80 p-4">
        <div className="text-xs font-semibold uppercase tracking-[0.18em] text-rose-600">Danger zone</div>
        <p className="mt-2 text-sm text-rose-700">
          Deleting this account removes your profile, posts, reactions, tokens, friendships, requests, and notifications tied to your user record.
        </p>
        <input
          className="mt-3 w-full rounded-2xl border border-rose-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-rose-400"
          type="password"
          value={deletePassword}
          onChange={(event) => setDeletePassword(event.target.value)}
          placeholder="Confirm with password"
          minLength={8}
        />
        <button className="mt-3 rounded-full bg-rose-600 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-white">
          Delete account
        </button>
      </form>
    </section>
  )
}
