import { startTransition, useCallback, useDeferredValue, useEffect, useState } from 'react'

import { apiRequest } from './api/client'
import { AccountPanel } from './components/AccountPanel'
import { AuthPanel } from './components/AuthPanel'
import { DiscoveryPanel } from './components/DiscoveryPanel'
import { FeedPanel } from './components/FeedPanel'
import { FriendsPanel } from './components/FriendsPanel'
import { NotificationsPanel } from './components/NotificationsPanel'
import { ProfilePanel } from './components/ProfilePanel'
import { useAuth } from './hooks/useAuth'
import { useLiveSocket } from './hooks/useLiveSocket'
import type { DashboardSummary, DiscoverUser, Friend, NotificationItem, OutgoingRequest, PendingRequest, Post } from './types'

export default function App() {
  const { user, tokens, loading, logout, reloadUser, clearSession } = useAuth()
  const [posts, setPosts] = useState<Post[]>([])
  const [notifications, setNotifications] = useState<NotificationItem[]>([])
  const [friends, setFriends] = useState<Friend[]>([])
  const [pending, setPending] = useState<PendingRequest[]>([])
  const [outgoing, setOutgoing] = useState<OutgoingRequest[]>([])
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [discover, setDiscover] = useState<DiscoverUser[]>([])
  const [discoverQuery, setDiscoverQuery] = useState('')
  const [discoverLoading, setDiscoverLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const accessToken = tokens?.access_token
  const deferredDiscoverQuery = useDeferredValue(discoverQuery)

  const loadDashboard = useCallback(async () => {
    if (!accessToken) return
    try {
      const [feed, notif, friendList, pendingRequests, outgoingRequests, dashboardSummary] = await Promise.all([
        apiRequest<Post[]>('/posts/feed', { method: 'GET' }, accessToken),
        apiRequest<NotificationItem[]>('/notifications', { method: 'GET' }, accessToken),
        apiRequest<Friend[]>('/friends', { method: 'GET' }, accessToken),
        apiRequest<PendingRequest[]>('/friends/requests/pending', { method: 'GET' }, accessToken),
        apiRequest<OutgoingRequest[]>('/friends/requests/outgoing', { method: 'GET' }, accessToken),
        apiRequest<DashboardSummary>('/users/me/dashboard', { method: 'GET' }, accessToken),
      ])
      startTransition(() => {
        setPosts(feed)
        setNotifications(notif)
        setFriends(friendList)
        setPending(pendingRequests)
        setOutgoing(outgoingRequests)
        setSummary(dashboardSummary)
      })
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed loading app data')
    }
  }, [accessToken])

  useEffect(() => {
    loadDashboard().catch(() => undefined)
  }, [loadDashboard])

  const loadDiscover = useCallback(async (query: string) => {
    if (!accessToken) return
    setDiscoverLoading(true)
    try {
      const path = query.trim()
        ? `/users/discover?q=${encodeURIComponent(query.trim())}`
        : '/users/discover'
      const profiles = await apiRequest<DiscoverUser[]>(path, { method: 'GET' }, accessToken)
      startTransition(() => {
        setDiscover(profiles)
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed loading discovery')
    } finally {
      setDiscoverLoading(false)
    }
  }, [accessToken])

  useEffect(() => {
    loadDiscover(deferredDiscoverQuery).catch(() => undefined)
  }, [deferredDiscoverQuery, loadDiscover])

  useEffect(() => {
    if (!success) return
    const id = window.setTimeout(() => setSuccess(null), 3500)
    return () => window.clearTimeout(id)
  }, [success])

  const onSocketMessage = useCallback((msg: { event: string; payload: Record<string, unknown> }) => {
    if (msg.event === 'notification' || msg.event === 'feed:new_post') {
      loadDashboard().catch(() => undefined)
    }
  }, [loadDashboard])

  useLiveSocket(accessToken, onSocketMessage)

  async function createPost(content: string) {
    if (!accessToken) return
    try {
      await apiRequest('/posts', { method: 'POST', body: JSON.stringify({ content }) }, accessToken)
      setSuccess('Post published to your feed.')
      await loadDashboard()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to publish post')
      throw err
    }
  }

  async function react(postId: string, reaction: string) {
    if (!accessToken) return
    try {
      await apiRequest(`/posts/${postId}/reactions/${reaction}`, { method: 'POST' }, accessToken)
      await loadDashboard()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to react to post')
      throw err
    }
  }

  async function sendRequest(payload: { receiverId?: string; identifier?: string }) {
    if (!accessToken) return
    try {
      await apiRequest(
        '/friends/requests',
        {
          method: 'POST',
          body: JSON.stringify(
            payload.receiverId ? { receiver_id: payload.receiverId } : { identifier: payload.identifier }
          ),
        },
        accessToken
      )
      setSuccess('Friend request sent.')
      await Promise.all([loadDashboard(), loadDiscover(deferredDiscoverQuery)])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send friend request')
      throw err
    }
  }

  async function respondRequest(requestId: string, action: 'accept' | 'reject') {
    if (!accessToken) return
    try {
      await apiRequest(`/friends/requests/${requestId}`, { method: 'PATCH', body: JSON.stringify({ action }) }, accessToken)
      setSuccess(action === 'accept' ? 'Friend request accepted.' : 'Friend request rejected.')
      await Promise.all([loadDashboard(), loadDiscover(deferredDiscoverQuery)])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update friend request')
      throw err
    }
  }

  async function cancelRequest(requestId: string) {
    if (!accessToken) return
    try {
      await apiRequest(`/friends/requests/${requestId}`, { method: 'DELETE' }, accessToken)
      setSuccess('Friend request cancelled.')
      await Promise.all([loadDashboard(), loadDiscover(deferredDiscoverQuery)])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to cancel friend request')
      throw err
    }
  }

  async function updateProfile(headline: string, username: string) {
    if (!accessToken) return
    try {
      await apiRequest(
        '/users/me/profile',
        { method: 'PATCH', body: JSON.stringify({ headline, username }) },
        accessToken
      )
      await Promise.all([reloadUser(), loadDashboard(), loadDiscover(deferredDiscoverQuery)])
      setSuccess('Profile updated.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update profile')
      throw err
    }
  }

  async function changePassword(currentPassword: string, newPassword: string) {
    if (!accessToken) return
    try {
      await apiRequest(
        '/users/me/password',
        { method: 'POST', body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }) },
        accessToken
      )
      setSuccess('Password updated. Other sessions were revoked.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to change password')
      throw err
    }
  }

  async function deleteAccount(password: string) {
    if (!accessToken) return
    try {
      await apiRequest('/users/me', { method: 'DELETE', body: JSON.stringify({ password }) }, accessToken)
      clearSession()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete account')
      throw err
    }
  }

  async function markRead(notificationId: string) {
    if (!accessToken) return
    try {
      await apiRequest(`/notifications/${notificationId}/read`, { method: 'PATCH' }, accessToken)
      await loadDashboard()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to mark notification as read')
      throw err
    }
  }

  async function markAllRead() {
    if (!accessToken) return
    try {
      await apiRequest('/notifications/read-all', { method: 'PATCH' }, accessToken)
      await loadDashboard()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to mark notifications as read')
      throw err
    }
  }

  if (loading) {
    return <div className="flex min-h-screen items-center justify-center text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">Loading network...</div>
  }

  if (!user || !tokens) {
    return (
      <div className="flex min-h-screen items-center justify-center p-4">
        <AuthPanel />
      </div>
    )
  }

  return (
    <main className="min-h-screen px-4 py-6 md:px-8 md:py-10">
      <div className="mx-auto max-w-7xl">
        <header className="mb-6 overflow-hidden rounded-[32px] border border-white/40 bg-[linear-gradient(130deg,rgba(15,23,42,0.92),rgba(29,78,216,0.9),rgba(15,118,110,0.88))] px-6 py-8 text-white shadow-[0_40px_120px_rgba(15,23,42,0.22)] md:px-8">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-2xl">
              <p className="text-[11px] uppercase tracking-[0.32em] text-white/60">Community dashboard</p>
              <h1 className="mt-3 font-display text-4xl leading-tight md:text-5xl">A faster, sharper social layer for your circle.</h1>
              <p className="mt-3 max-w-xl text-sm leading-7 text-white/78">
                Track relationships, publish to your live feed, and manage a tighter social graph with stronger backend defaults underneath.
              </p>
            </div>
            <div className="grid gap-3 sm:grid-cols-3">
              {[
                { label: 'Friends', value: summary?.friends_count ?? 0 },
                { label: 'Posts', value: summary?.posts_count ?? 0 },
                { label: 'Unread', value: summary?.unread_notifications ?? 0 },
              ].map((item) => (
                <div key={item.label} className="rounded-3xl border border-white/10 bg-white/10 px-4 py-4">
                  <div className="text-[11px] uppercase tracking-[0.2em] text-white/60">{item.label}</div>
                  <div className="mt-2 text-2xl font-semibold">{item.value}</div>
                </div>
              ))}
            </div>
          </div>
        </header>

        {error && <p className="mb-4 rounded-3xl border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-700">{error}</p>}
        {success && <p className="mb-4 rounded-3xl border border-emerald-200 bg-emerald-50 px-5 py-4 text-sm text-emerald-700">{success}</p>}

        <div className="grid gap-5 xl:grid-cols-[300px_minmax(0,1fr)_360px]">
          <div className="space-y-5">
            <ProfilePanel user={user} summary={summary} onLogout={logout} />
            <FriendsPanel
              friends={friends}
              pending={pending}
              outgoing={outgoing}
              onSendRequest={(identifier) => sendRequest({ identifier })}
              onRespond={respondRequest}
              onCancel={cancelRequest}
            />
          </div>

          <div className="space-y-5">
            <FeedPanel posts={posts} onCreatePost={createPost} onReact={react} />
          </div>

          <div className="space-y-5">
            <DiscoveryPanel
              query={discoverQuery}
              results={discover}
              loading={discoverLoading}
              onQueryChange={setDiscoverQuery}
              onSendRequest={(receiverId) => sendRequest({ receiverId })}
            />
            <NotificationsPanel
              items={notifications}
              unreadCount={summary?.unread_notifications ?? 0}
              onMarkRead={markRead}
              onMarkAllRead={markAllRead}
            />
          </div>
        </div>

        <section className="mt-6 rounded-[32px] border border-white/50 bg-white/70 p-5 shadow-[0_24px_80px_rgba(15,23,42,0.1)] backdrop-blur md:p-6">
          <div className="mb-5 flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-[11px] uppercase tracking-[0.28em] text-sky-700">Settings section</p>
              <h2 className="mt-2 font-display text-3xl text-slate-950">Profile and account settings</h2>
            </div>
            <p className="max-w-xl text-sm text-slate-500">
              Sensitive account actions live here separately from the social dashboard so profile edits, password rotation, and account lifecycle controls stay isolated.
            </p>
          </div>

          <AccountPanel
            user={user}
            onUpdateProfile={updateProfile}
            onChangePassword={changePassword}
            onDeleteAccount={deleteAccount}
          />
        </section>
      </div>
    </main>
  )
}
