import { z } from 'zod'

import { apiBaseUrl } from './utils'

const signInSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
})

export async function apiFetch<T>(path: string, init?: RequestInit, token?: string): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init?.headers ?? {})
    },
    cache: 'no-store'
  })
  if (!response.ok) {
    throw new Error(await response.text())
  }
  return response.json() as Promise<T>
}

export async function signInRequest(values: z.infer<typeof signInSchema>) {
  return apiFetch<{ user: unknown; tokens: { access_token: string; refresh_token: string } }>('/auth/signin', {
    method: 'POST',
    body: JSON.stringify(signInSchema.parse(values))
  })
}
