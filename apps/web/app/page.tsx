import Link from 'next/link'

export default function LandingPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-6xl items-center gap-16 px-6 py-20">
      <section className="max-w-2xl">
        <p className="text-sm uppercase tracking-[0.4em] text-indigo-300">Realtime • Secure • Premium</p>
        <h1 className="mt-6 text-6xl font-semibold leading-tight">Messenger-grade collaboration with practical secret chats.</h1>
        <p className="mt-6 text-lg text-slate-300">CipherChat combines Next.js, FastAPI, PostgreSQL, authenticated WebSockets, polished motion, and hybrid encryption for privacy-sensitive direct messages.</p>
        <div className="mt-10 flex gap-4">
          <Link href="/auth/signin" className="rounded-2xl bg-indigo-500 px-6 py-3 font-medium text-white">Open app</Link>
          <Link href="/auth/signup" className="rounded-2xl border border-white/15 px-6 py-3 font-medium">Create account</Link>
        </div>
      </section>
      <section className="card flex-1 p-8">
        <div className="space-y-4">
          <div className="rounded-3xl bg-white/5 p-4">Direct and group conversations with delivery state, reactions, unread counters, and search-ready APIs.</div>
          <div className="rounded-3xl bg-white/5 p-4">Client-side generated RSA keypairs wrap per-message AES content keys for secret inboxes.</div>
          <div className="rounded-3xl bg-white/5 p-4">Deployment-ready Docker Compose, Alembic migrations, seed data, pytest, Vitest, and Playwright scaffolding.</div>
        </div>
      </section>
    </main>
  )
}
