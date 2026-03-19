import { FormEvent, useState } from 'react'

import { formatRelativeTime, getInitials } from '../lib/format'
import type { Post } from '../types'

type Props = {
  posts: Post[]
  onCreatePost: (content: string) => Promise<void>
  onReact: (postId: string, reaction: string) => Promise<void>
}

const REACTIONS = ['like', 'love', 'haha', 'wow', 'sad', 'angry']

export function FeedPanel({ posts, onCreatePost, onReact }: Props) {
  const [content, setContent] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function submitPost(e: FormEvent) {
    e.preventDefault()
    if (!content.trim()) return
    setSubmitting(true)
    try {
      await onCreatePost(content.trim())
      setContent('')
    } catch {
      // Global error banner is handled by the parent container.
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="rounded-[28px] border border-white/50 bg-white/85 p-5 shadow-[0_24px_80px_rgba(15,23,42,0.12)] backdrop-blur">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-[11px] uppercase tracking-[0.22em] text-sky-700">Home feed</p>
          <h2 className="mt-1 font-display text-3xl text-slate-950">Your community pulse</h2>
        </div>
        <div className="rounded-full bg-slate-900 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-white">
          {posts.length} stories
        </div>
      </div>

      <form className="mt-5 rounded-[28px] border border-slate-200 bg-slate-50/80 p-4" onSubmit={submitPost}>
        <textarea
          className="w-full resize-none rounded-2xl border border-slate-200 bg-white px-4 py-4 text-sm text-slate-900 outline-none transition focus:border-sky-400"
          rows={4}
          placeholder="Share a milestone, thought, or update with your network..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
          maxLength={1200}
        />
        <div className="mt-3 flex items-center justify-between gap-3">
          <p className="text-xs uppercase tracking-[0.16em] text-slate-400">{content.length}/1200 characters</p>
          <button
            disabled={submitting || !content.trim()}
            className="rounded-full bg-sky-600 px-5 py-3 text-xs font-semibold uppercase tracking-[0.18em] text-white transition hover:bg-sky-500 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-500"
          >
            {submitting ? 'Publishing...' : 'Publish post'}
          </button>
        </div>
      </form>

      <div className="mt-5 space-y-4">
        {posts.length === 0 && (
          <div className="rounded-[28px] border border-dashed border-slate-200 px-5 py-12 text-center text-sm text-slate-500">
            Your feed is empty right now. Connect with people from the discovery panel to unlock a fuller timeline.
          </div>
        )}

        {posts.map((post) => (
          <article key={post.id} className="rounded-[28px] border border-slate-200/70 bg-slate-50/70 p-5 transition hover:border-slate-300 hover:bg-white">
            <div className="flex items-start gap-4">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-slate-900 text-sm font-semibold tracking-[0.16em] text-white">
                {getInitials(post.author_username)}
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
                  <h3 className="font-semibold text-slate-950">{post.author_username}</h3>
                  <span className="text-xs uppercase tracking-[0.16em] text-slate-400">{formatRelativeTime(post.created_at)}</span>
                </div>
                <p className="mt-1 text-sm text-slate-500">{post.author_headline}</p>
              </div>
            </div>

            <p className="mt-4 whitespace-pre-wrap text-[15px] leading-7 text-slate-900">{post.content}</p>

            <div className="mt-4 flex items-center justify-between gap-3 border-t border-slate-200 pt-4">
              <div className="text-xs uppercase tracking-[0.18em] text-slate-400">
                {post.total_reactions} total reactions
              </div>
            </div>

            <div className="mt-3 flex flex-wrap gap-2">
              {REACTIONS.map((reaction) => (
                <button
                  key={reaction}
                  onClick={() => {
                    void onReact(post.id, reaction).catch(() => undefined)
                  }}
                  className={`rounded-full border px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.14em] transition ${
                    post.user_reaction === reaction
                      ? 'border-sky-200 bg-sky-50 text-sky-700'
                      : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:text-slate-900'
                  }`}
                >
                  {reaction} ({post.reactions[reaction] || 0})
                </button>
              ))}
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}
