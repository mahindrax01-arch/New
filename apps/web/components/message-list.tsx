'use client'

import { formatDistanceToNow } from 'date-fns'

import { Message } from '@/lib/types'
import { decodeFallbackMessage } from '@/lib/crypto'

export function MessageList({ messages, currentUserId }: { messages: Message[]; currentUserId: string }) {
  return (
    <div className="flex flex-1 flex-col gap-3 overflow-y-auto px-6 py-4">
      {messages.map((message) => {
        const mine = message.sender.id === currentUserId
        return (
          <div key={message.id} className={`flex ${mine ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[70%] rounded-3xl px-4 py-3 ${mine ? 'bg-indigo-500 text-white' : 'bg-white/5 text-slate-100'}`}>
              <div className="text-sm leading-6">{decodeFallbackMessage(message.body, message.plaintext_fallback)}</div>
              <div className="mt-2 flex items-center justify-between gap-4 text-[11px] text-white/70">
                <span>{message.sender.name}</span>
                <span>{formatDistanceToNow(new Date(message.created_at), { addSuffix: true })}</span>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
