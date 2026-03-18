'use client'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useSession } from 'next-auth/react'
import { useMemo, useState } from 'react'

import { apiFetch } from '@/lib/api'
import { encryptSecretMessage } from '@/lib/crypto'
import { Conversation, Message } from '@/lib/types'

import { MessageList } from './message-list'

export function ChatShell({ conversation }: { conversation: Conversation }) {
  const { data: session } = useSession()
  const [text, setText] = useState('')
  const queryClient = useQueryClient()
  const token = session?.backendTokens?.accessToken

  const messagesQuery = useQuery({
    queryKey: ['messages', conversation.id],
    queryFn: () => apiFetch<Message[]>(`/chat/conversations/${conversation.id}/messages`, undefined, token),
    enabled: Boolean(token)
  })

  const members = useMemo(() => conversation.members.filter((member) => member.id !== session?.user.id), [conversation.members, session?.user.id])

  const sendMessage = useMutation({
    mutationFn: async () => {
      const payload = conversation.is_secret
        ? await encryptSecretMessage(text, members.map((member) => ({ recipientId: member.id, publicKey: member.public_key ?? '' })).filter((member) => member.publicKey))
        : { body: text, secret_keys: [] }
      return apiFetch<Message>('/chat/messages', {
        method: 'POST',
        body: JSON.stringify({
          conversation_id: conversation.id,
          plaintext_fallback: conversation.is_secret ? 'Encrypted message' : text,
          client_nonce: crypto.randomUUID(),
          ...payload
        })
      }, token)
    },
    onSuccess: async () => {
      setText('')
      await queryClient.invalidateQueries({ queryKey: ['messages', conversation.id] })
    }
  })

  return (
    <section className="card flex h-[calc(100vh-3rem)] flex-1 flex-col overflow-hidden">
      <div className="border-b border-white/10 px-6 py-4">
        <p className="text-xs uppercase tracking-[0.3em] text-slate-400">{conversation.is_secret ? 'Secret chat' : conversation.kind}</p>
        <h1 className="mt-2 text-2xl font-semibold">{conversation.title ?? 'Conversation'}</h1>
      </div>
      <MessageList messages={messagesQuery.data ?? []} currentUserId={session?.user.id ?? ''} />
      <div className="border-t border-white/10 p-4">
        <div className="flex gap-3 rounded-3xl bg-white/5 p-2">
          <input value={text} onChange={(event) => setText(event.target.value)} placeholder={conversation.is_secret ? 'Write an encrypted message…' : 'Write a message…'} className="flex-1 bg-transparent px-4 py-3 outline-none" />
          <button onClick={() => sendMessage.mutate()} disabled={!text.trim() || sendMessage.isPending} className="rounded-2xl bg-indigo-500 px-5 py-3 font-medium text-white disabled:opacity-50">Send</button>
        </div>
      </div>
    </section>
  )
}
