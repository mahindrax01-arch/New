'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { apiFetch } from '@/lib/api'
import { generateUserKeyBundle } from '@/lib/crypto'

const schema = z.object({
  name: z.string().min(2),
  username: z.string().min(3),
  email: z.string().email(),
  password: z.string().min(8)
})

type Values = z.infer<typeof schema>

export default function SignUpPage() {
  const router = useRouter()
  const form = useForm<Values>({ resolver: zodResolver(schema) })

  return (
    <main className="mx-auto flex min-h-screen max-w-md items-center px-6">
      <form
        className="card w-full space-y-4 p-8"
        onSubmit={form.handleSubmit(async (values) => {
          const keys = await generateUserKeyBundle(values.password)
          await apiFetch('/auth/signup', { method: 'POST', body: JSON.stringify({ ...values, public_key: keys.publicKey, encrypted_private_key: keys.encryptedPrivateKey, private_key_salt: keys.privateKeySalt }) })
          router.push('/auth/signin')
        })}
      >
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-slate-400">Create account</p>
          <h1 className="mt-2 text-3xl font-semibold">Set up your secure workspace</h1>
        </div>
        <input {...form.register('name')} className="w-full rounded-2xl bg-white/5 px-4 py-3 outline-none" placeholder="Name" />
        <input {...form.register('username')} className="w-full rounded-2xl bg-white/5 px-4 py-3 outline-none" placeholder="Username" />
        <input {...form.register('email')} className="w-full rounded-2xl bg-white/5 px-4 py-3 outline-none" placeholder="Email" />
        <input {...form.register('password')} type="password" className="w-full rounded-2xl bg-white/5 px-4 py-3 outline-none" placeholder="Password" />
        <button className="w-full rounded-2xl bg-indigo-500 px-4 py-3 font-medium">Create account</button>
      </form>
    </main>
  )
}
