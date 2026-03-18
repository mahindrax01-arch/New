import { z } from 'zod'

export const websocketEventSchema = z.discriminatedUnion('type', [
  z.object({ type: z.literal('subscribe'), conversationId: z.string() }),
  z.object({ type: z.literal('typing'), conversationId: z.string(), isTyping: z.boolean() }),
  z.object({ type: z.literal('message.created'), payload: z.any() }),
  z.object({ type: z.literal('presence'), userId: z.string(), isOnline: z.boolean() }),
  z.object({ type: z.literal('pong') })
])

export type WebsocketEvent = z.infer<typeof websocketEventSchema>
