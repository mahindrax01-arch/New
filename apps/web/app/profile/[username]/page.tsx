export default async function ProfilePage({ params }: { params: Promise<{ username: string }> }) {
  const { username } = await params
  return (
    <main className="mx-auto max-w-3xl p-6">
      <div className="card p-8">
        <p className="text-sm uppercase tracking-[0.3em] text-slate-400">Profile</p>
        <h1 className="mt-2 text-4xl font-semibold">@{username}</h1>
        <p className="mt-4 text-slate-300">Public profile route for richer presence, bios, and mutual conversation actions.</p>
      </div>
    </main>
  )
}
