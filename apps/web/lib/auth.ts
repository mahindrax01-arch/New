import CredentialsProvider from 'next-auth/providers/credentials'
import { NextAuthOptions } from 'next-auth'

const apiBaseUrl = process.env.API_BASE_URL ?? 'http://localhost:8000'

export const authOptions: NextAuthOptions = {
  session: { strategy: 'jwt' },
  pages: { signIn: '/auth/signin' },
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials.password) return null
        const response = await fetch(`${apiBaseUrl}/auth/signin`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: credentials.email, password: credentials.password })
        })
        if (!response.ok) return null
        const payload = await response.json()
        return {
          ...payload.user,
          backendTokens: {
            accessToken: payload.tokens.access_token,
            refreshToken: payload.tokens.refresh_token
          }
        }
      }
    })
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.user = user
        token.backendTokens = (user as { backendTokens: { accessToken: string; refreshToken: string } }).backendTokens
      }
      return token
    },
    async session({ session, token }) {
      session.user = token.user as typeof session.user
      ;(session as typeof session & { backendTokens: { accessToken: string; refreshToken: string } }).backendTokens = token.backendTokens as { accessToken: string; refreshToken: string }
      return session
    }
  }
}
