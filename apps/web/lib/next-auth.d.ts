import 'next-auth'
import 'next-auth/jwt'

declare module 'next-auth' {
  interface Session {
    backendTokens: {
      accessToken: string
      refreshToken: string
    }
    user: {
      id: string
      email: string
      name: string
      username: string
      avatar_url?: string | null
      bio?: string | null
      public_key?: string | null
      encrypted_private_key?: string | null
      private_key_salt?: string | null
    }
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    user?: unknown
    backendTokens?: {
      accessToken: string
      refreshToken: string
    }
  }
}
