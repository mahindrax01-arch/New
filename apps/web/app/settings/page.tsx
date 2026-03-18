export default function SettingsPage() {
  return (
    <main className="mx-auto max-w-4xl p-6">
      <div className="card space-y-6 p-8">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-slate-400">Settings</p>
          <h1 className="mt-2 text-3xl font-semibold">Profile, security, theme, and key management</h1>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          <section className="rounded-3xl bg-white/5 p-5">Profile editing, avatar, and bio controls live here.</section>
          <section className="rounded-3xl bg-white/5 p-5">Notification toggles and privacy defaults are ready for wiring.</section>
          <section className="rounded-3xl bg-white/5 p-5">Theme and density preferences fit here.</section>
          <section className="rounded-3xl bg-white/5 p-5">Secret chat key export/import UX belongs here, keeping private keys client-controlled.</section>
        </div>
      </div>
    </main>
  )
}
