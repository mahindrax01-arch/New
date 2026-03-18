import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...values: Parameters<typeof clsx>) {
  return twMerge(clsx(values))
}

export const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000'
export const wsBaseUrl = process.env.NEXT_PUBLIC_WS_BASE_URL ?? 'ws://localhost:8000'
