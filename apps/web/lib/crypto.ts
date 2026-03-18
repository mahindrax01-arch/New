const enc = new TextEncoder()

function toBase64(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer)
  let binary = ''
  bytes.forEach((byte) => {
    binary += String.fromCharCode(byte)
  })
  return btoa(binary)
}

function fromBase64(value: string): ArrayBuffer {
  const binary = atob(value)
  const bytes = Uint8Array.from(binary, (char) => char.charCodeAt(0))
  return bytes.buffer
}

export async function generateUserKeyBundle(password: string) {
  const encryption = await crypto.subtle.generateKey(
    { name: 'RSA-OAEP', modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: 'SHA-256' },
    true,
    ['encrypt', 'decrypt']
  )
  const signing = await crypto.subtle.generateKey(
    { name: 'RSA-PSS', modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: 'SHA-256' },
    true,
    ['sign', 'verify']
  )
  const salt = crypto.getRandomValues(new Uint8Array(16))
  const baseKey = await crypto.subtle.importKey('raw', enc.encode(password), 'PBKDF2', false, ['deriveKey'])
  const wrappingKey = await crypto.subtle.deriveKey(
    { name: 'PBKDF2', salt, iterations: 120000, hash: 'SHA-256' },
    baseKey,
    { name: 'AES-GCM', length: 256 },
    true,
    ['encrypt', 'decrypt']
  )
  const privateKey = await crypto.subtle.exportKey('pkcs8', encryption.privateKey)
  const iv = crypto.getRandomValues(new Uint8Array(12))
  const encryptedPrivateKey = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, wrappingKey, privateKey)
  return {
    publicKey: toBase64(await crypto.subtle.exportKey('spki', encryption.publicKey)),
    signingPublicKey: toBase64(await crypto.subtle.exportKey('spki', signing.publicKey)),
    encryptedPrivateKey: `${toBase64(iv.buffer)}.${toBase64(encryptedPrivateKey)}`,
    privateKeySalt: toBase64(salt.buffer)
  }
}

export async function encryptSecretMessage(
  plaintext: string,
  recipientPublicKeys: { recipientId: string; publicKey: string }[]
) {
  const contentKey = await crypto.subtle.generateKey({ name: 'AES-GCM', length: 256 }, true, ['encrypt', 'decrypt'])
  const iv = crypto.getRandomValues(new Uint8Array(12))
  const ciphertext = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, contentKey, enc.encode(plaintext))
  const rawContentKey = await crypto.subtle.exportKey('raw', contentKey)
  const wrappedKeys = await Promise.all(
    recipientPublicKeys.map(async (recipient) => {
      const publicKey = await crypto.subtle.importKey('spki', fromBase64(recipient.publicKey), { name: 'RSA-OAEP', hash: 'SHA-256' }, false, ['encrypt'])
      const wrapped = await crypto.subtle.encrypt({ name: 'RSA-OAEP' }, publicKey, rawContentKey)
      return { recipient_id: recipient.recipientId, wrapped_key: toBase64(wrapped) }
    })
  )
  return {
    body: JSON.stringify({ ciphertext: toBase64(ciphertext), iv: toBase64(iv.buffer), algorithm: 'AES-GCM' }),
    secret_keys: wrappedKeys
  }
}

export function decodeFallbackMessage(body: string, fallback?: string | null) {
  if (fallback) return fallback
  try {
    const parsed = JSON.parse(body) as { ciphertext?: string }
    if (parsed.ciphertext) return 'Encrypted message'
  } catch {
    return body
  }
  return body
}
