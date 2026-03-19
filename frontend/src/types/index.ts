export type User = {
  id: string
  email: string
  username: string
  role: 'guest' | 'user' | 'admin'
  headline: string
}

export type AuthTokens = {
  access_token: string
  refresh_token: string
  token_type: 'bearer'
}

export type Post = {
  id: string
  author_id: string
  author_username: string
  author_headline: string
  content: string
  created_at: string
  reactions: Record<string, number>
  total_reactions: number
  user_reaction?: string | null
}

export type NotificationItem = {
  id: string
  type: string
  message: string
  data: Record<string, unknown>
  is_read: boolean
  created_at: string
}

export type Friend = {
  id: string
  username: string
  email: string
  headline: string
}

export type PendingRequest = {
  id: string
  sender_id: string
  sender_username: string
  sender_headline: string
  created_at: string
}

export type OutgoingRequest = {
  id: string
  receiver_id: string
  receiver_username: string
  receiver_headline: string
  created_at: string
}

export type DashboardSummary = {
  friends_count: number
  posts_count: number
  unread_notifications: number
  pending_requests: number
}

export type DiscoverUser = {
  id: string
  username: string
  email: string
  role: 'guest' | 'user' | 'admin'
  headline: string
  relationship_status: 'friend' | 'incoming_request' | 'outgoing_request' | 'none'
}
