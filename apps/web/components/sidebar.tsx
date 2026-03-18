'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'

import { Conversation } from '@/lib/types'
import { decodeFallbackMessage } from '@/lib/crypto'

export function Sidebar({ conversations }: { conversations: Conversation[] }) {
  return (
    <aside className="card flex h-[calc(100vh-3rem)] w-full max-w-sm flex-col overflow-hidden p-3">
      <div className="mb-4 px-3 pt-3">
        <p className="text-xs uppercase tracking-[0.3em] text-slate-400">CipherChat</p>
        <h2 className="mt-2 text-2xl font-semibold">Inbox</h2>
      </div>
      <div className="space-y-2 overflow-y-auto">
        {conversations.map((conversation) => (
          <Link key={conversation.id} href={`/chat/${conversation.id}`}>
            <motion.div whileHover={{ x: 4 }} className="rounded-2xl border border-white/5 bg-white/5 p-3 transition hover:border-white/10">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-white">{conversation.title ?? conversation.members.map((m) => m.name).join(', ')}</p>
                  <p className="mt-1 text-sm text-slate-400">{conversation.last_message ? decodeFallbackMessage(conversation.last_message.body, conversation.last_message.plaintext_fallback) : 'No messages yet'}</p>
                </div>
                {conversation.unread_count > 0 ? <span className="rounded-full bg-indigo-500 px-2 py-1 text-xs">{conversation.unread_count}</span> : null}
              </div>
            </motion.div>
          </Link>
        ))}
      </div>
    </aside>
  )
}
