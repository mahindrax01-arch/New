import { describe, expect, it } from 'vitest'

import { decodeFallbackMessage } from './crypto'

describe('decodeFallbackMessage', () => {
  it('prefers plaintext fallback', () => {
    expect(decodeFallbackMessage('cipher', 'Readable text')).toBe('Readable text')
  })
})
