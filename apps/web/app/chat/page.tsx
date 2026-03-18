import { redirect } from 'next/navigation'

import { Sidebar } from '@/components/sidebar'
import { requireSession } from '@/lib/server/session'
import { apiFetch } from '@/lib/api'
import { Conversation } from '@/lib/types'

export default async function ChatIndexPage() {
  const session = await requireSession()
  if (!session) redirect('/auth/signin')
  const conversations = await apiFetch<Conversation[]>('/chat/conversations', undefined, (session as typeof session & { backendTokens: { accessToken: string } }).backendTokens.accessToken)
  return (
    <main className="grid min-h-screen grid-cols-[360px_1fr] gap-6 p-6">
      <Sidebar conversations={conversations} />
      <section className="card flex h-[calc(100vh-3rem)] items-center justify-center text-center">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Select a conversation</p>
          <h1 className="mt-3 text-4xl font-semibold">Your encrypted inbox is ready.</h1>
        </div>
      </section>
    </main>
  )
}
