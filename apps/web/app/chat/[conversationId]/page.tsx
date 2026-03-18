import { notFound, redirect } from 'next/navigation'

import { ChatShell } from '@/components/chat-shell'
import { Sidebar } from '@/components/sidebar'
import { apiFetch } from '@/lib/api'
import { requireSession } from '@/lib/server/session'
import { Conversation } from '@/lib/types'

export default async function ConversationPage({ params }: { params: Promise<{ conversationId: string }> }) {
  const session = await requireSession()
  if (!session) redirect('/auth/signin')
  const { conversationId } = await params
  const accessToken = (session as typeof session & { backendTokens: { accessToken: string } }).backendTokens.accessToken
  const [conversations, conversation] = await Promise.all([
    apiFetch<Conversation[]>('/chat/conversations', undefined, accessToken),
    apiFetch<Conversation>(`/chat/conversations/${conversationId}`, undefined, accessToken).catch(() => null)
  ])
  if (!conversation) notFound()
  return (
    <main className="grid min-h-screen grid-cols-[360px_1fr] gap-6 p-6">
      <Sidebar conversations={conversations} />
      <ChatShell conversation={conversation} />
    </main>
  )
}
