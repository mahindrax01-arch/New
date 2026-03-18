export default function NotFound() {
  return (
    <main className="flex min-h-screen items-center justify-center">
      <div className="card p-8 text-center">
        <h1 className="text-3xl font-semibold">Conversation not found</h1>
        <p className="mt-3 text-slate-400">The requested resource is unavailable or you do not have access.</p>
      </div>
    </main>
  )
}
