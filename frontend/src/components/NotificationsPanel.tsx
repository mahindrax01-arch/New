import type { NotificationItem } from '../types'
import { formatRelativeTime } from '../lib/format'

type Props = {
  items: NotificationItem[]
  unreadCount: number
  onMarkRead: (id: string) => Promise<void>
  onMarkAllRead: () => Promise<void>
}

export function NotificationsPanel({ items, unreadCount, onMarkRead, onMarkAllRead }: Props) {
  return (
    <section className="rounded-[28px] border border-white/50 bg-white/85 p-5 shadow-[0_24px_80px_rgba(15,23,42,0.12)] backdrop-blur">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-[11px] uppercase tracking-[0.22em] text-sky-700">Inbox</p>
          <h2 className="mt-1 font-display text-2xl text-slate-950">Notifications</h2>
        </div>
        <button
          onClick={() => {
            void onMarkAllRead().catch(() => undefined)
          }}
          className="text-xs font-semibold uppercase tracking-[0.16em] text-sky-700 transition hover:text-sky-900"
        >
          Mark all read
        </button>
      </div>

      <div className="mt-3 rounded-3xl bg-slate-50 px-4 py-4 text-sm text-slate-600">
        {unreadCount} unread alerts
      </div>

      <div className="mt-4 space-y-3">
        {items.length === 0 && (
          <div className="rounded-3xl border border-dashed border-slate-200 px-4 py-6 text-center text-sm text-slate-500">
            No notifications yet.
          </div>
        )}

        {items.map((item) => (
          <div key={item.id} className={`rounded-3xl border p-4 text-sm ${item.is_read ? 'border-slate-200 bg-slate-50/70' : 'border-sky-200 bg-sky-50/80'}`}>
            <div className="flex items-center justify-between gap-3">
              <p className={item.is_read ? 'text-slate-500' : 'font-medium text-slate-900'}>{item.message}</p>
              <span className="shrink-0 text-[11px] uppercase tracking-[0.16em] text-slate-400">{formatRelativeTime(item.created_at)}</span>
            </div>
            {!item.is_read && (
              <button
                onClick={() => {
                  void onMarkRead(item.id).catch(() => undefined)
                }}
                className="mt-3 text-xs font-semibold uppercase tracking-[0.16em] text-sky-700 transition hover:text-sky-900"
              >
                Mark as read
              </button>
            )}
          </div>
        ))}
      </div>
    </section>
  )
}
