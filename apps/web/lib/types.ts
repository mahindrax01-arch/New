export type SessionUser = {
  id: string
  email: string
  username: string
  name: string
  avatar_url?: string | null
  bio?: string | null
  public_key?: string | null
  encrypted_private_key?: string | null
  private_key_salt?: string | null
  theme: string
  is_online: boolean
}

export type SecretKeyPayload = {
  recipient_id: string
  wrapped_key: string
  signature?: string | null
}

export type Message = {
  id: string
  conversation_id: string
  body: string
  plaintext_fallback?: string | null
  kind: string
  reply_to_message_id?: string | null
  created_at: string
  edited_at?: string | null
  sender: SessionUser
  reactions: Record<string, number>
  secret_keys: SecretKeyPayload[]
}

export type Conversation = {
  id: string
  title?: string | null
  kind: string
  description?: string | null
  is_secret: boolean
  avatar_url?: string | null
  members: SessionUser[]
  unread_count: number
  last_message?: Message | null
}
