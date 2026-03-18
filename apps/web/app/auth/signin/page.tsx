'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import { signIn } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
})

type Values = z.infer<typeof schema>

export default function SignInPage() {
  const router = useRouter()
  const form = useForm<Values>({ resolver: zodResolver(schema), defaultValues: { email: 'alice@example.com', password: 'Password123!' } })

  return (
    <main className="mx-auto flex min-h-screen max-w-md items-center px-6">
      <form
        className="card w-full space-y-4 p-8"
        onSubmit={form.handleSubmit(async (values) => {
          const result = await signIn('credentials', { ...values, redirect: false })
          if (result?.ok) router.push('/chat')
        })}
      >
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-slate-400">Welcome back</p>
          <h1 className="mt-2 text-3xl font-semibold">Sign in to CipherChat</h1>
        </div>
        <input {...form.register('email')} className="w-full rounded-2xl bg-white/5 px-4 py-3 outline-none" placeholder="Email" />
        <input {...form.register('password')} type="password" className="w-full rounded-2xl bg-white/5 px-4 py-3 outline-none" placeholder="Password" />
        <button className="w-full rounded-2xl bg-indigo-500 px-4 py-3 font-medium">Sign in</button>
      </form>
    </main>
  )
}
