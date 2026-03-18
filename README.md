# CipherChat

## 1. Architecture summary
CipherChat is a monorepo with a Next.js 15 App Router frontend and a FastAPI backend. Authentication is handled in the web app with Auth.js credentials provider delegating password verification to the API. The API owns authorization, persistence, and WebSocket fan-out. PostgreSQL stores users, conversations, delivery state, and secret-message key metadata. Secret inboxes use browser-side hybrid encryption: the browser encrypts message content with AES-GCM and wraps the content key per recipient with RSA-OAEP. The server stores ciphertext and wrapped keys only.

## 2. Folder structure
- `apps/web`: Next.js app, Auth.js integration, Tailwind UI, TanStack Query, Web Crypto helpers, Playwright/Vitest config.
- `apps/api`: FastAPI app, SQLAlchemy models, Alembic migration, seed script, pytest.
- `packages/types`: shared Zod websocket event schema.

## 3. Environment variables
Copy `.env.example` and adjust values as needed.
- `NEXTAUTH_URL`
- `NEXTAUTH_SECRET`
- `API_BASE_URL`
- `NEXT_PUBLIC_API_BASE_URL`
- `NEXT_PUBLIC_WS_BASE_URL`
- `APP_ENV`
- `APP_SECRET_KEY`
- `DATABASE_URL`
- `CORS_ORIGINS`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `REFRESH_TOKEN_EXPIRE_MINUTES`
- `FRONTEND_URL`

## 4. Database schema
Core tables:
- `users`
- `conversations`
- `conversation_members`
- `messages`
- `delivery_states`
- `reactions`
- `attachments`
- `secret_message_keys`
- `blocks`
- `notification_preferences`

The schema is defined in SQLAlchemy models and created through Alembic migration `20260318_0001_init`.

## 5. Backend implementation
FastAPI modules:
- `app/api/routes/auth.py`: signup/signin/refresh/me.
- `app/api/routes/chat.py`: conversations, messages, reactions, user search.
- `app/api/routes/ws.py`: authenticated websocket subscribe/typing/message events.
- `app/services/chat.py`: conversation and messaging domain logic.
- `app/websocket/manager.py`: room and per-user socket fan-out abstraction.

Security notes:
- Passwords are bcrypt-hashed.
- JWT access/refresh tokens protect HTTP and WebSocket access.
- Membership checks guard conversation and message APIs.
- Client nonce supports idempotent message creation.
- Secret-chat bodies are stored as ciphertext payload JSON with wrapped keys in `secret_message_keys`.

## 6. Frontend implementation
Next.js App Router routes include:
- `/`
- `/auth/signin`
- `/auth/signup`
- `/chat`
- `/chat/[conversationId]`
- `/settings`
- `/profile/[username]`

Frontend responsibilities implemented:
- credentials auth via Auth.js
- protected chat dashboard and conversation route
- premium sidebar/message shell UI with Tailwind and Framer Motion
- TanStack Query message fetching and optimistic-ready mutation flow
- browser-side key generation and hybrid-encryption helper functions

## 7. WebSocket protocol / event contract
Client -> server:
- `subscribe`: `{ type: 'subscribe', conversationId }`
- `typing`: `{ type: 'typing', conversationId, isTyping }`
- `message.create`: `{ type: 'message.create', payload: MessageCreate }`
- `ping`: `{ type: 'ping' }`

Server -> client:
- `presence`: `{ type: 'presence', userId, isOnline }`
- `typing`: `{ type: 'typing', conversationId, userId, isTyping }`
- `message.created`: `{ type: 'message.created', payload }`
- `pong`: `{ type: 'pong' }`

## 8. Encryption flow design
Implemented safe minimum viable secret-chat model:
1. Browser generates RSA-OAEP encryption keys and RSA-PSS signing keys.
2. Browser derives an AES-GCM wrapping key from the user password using PBKDF2.
3. Browser encrypts the private RSA key before any persistence.
4. For each secret message, browser generates a fresh AES-GCM content key.
5. Browser encrypts plaintext with the AES key.
6. Browser wraps that AES key separately for each recipient with recipient RSA public keys.
7. API stores ciphertext in `messages.body` and wrapped per-recipient keys in `secret_message_keys`.

Tradeoffs:
- This is an “end-to-end-style” practical v1. Recovery and multi-device key sync are not solved serverlessly here.
- Signature verification plumbing is scaffolded in the schema but not fully enforced end-to-end.
- Secret group chat is intentionally left as future work to avoid unsafe key-management shortcuts.

## 9. Docker setup
Run the full stack locally:
```bash
docker-compose up --build
```
This starts PostgreSQL, applies Alembic migrations, seeds demo data, launches FastAPI on `:8000`, and serves Next.js on `:3000`.

## 10. Seed script
The API seed script creates demo users:
- `alice@example.com`
- `bob@example.com`
- `carol@example.com`

Default password for all demo users:
```text
Password123!
```

It also creates:
- a direct chat
- a secret direct chat
- a launch-team group chat
- realistic starter messages

## 11. Tests
Backend:
```bash
cd apps/api
uv sync --group dev
uv run pytest
```

Frontend unit test:
```bash
pnpm --dir apps/web test
```

Frontend E2E:
```bash
pnpm --dir apps/web test:e2e
```

## 12. Setup, run, and security notes
Local development without Docker:
```bash
# API
cd apps/api
uv sync --group dev
uv run alembic upgrade head
uv run python -m app.seed
uv run uvicorn app.main:app --reload

# Web
cd apps/web
pnpm install
pnpm dev
```

Security guidance:
- keep `.env` secrets out of version control
- use HTTPS and secure cookies outside local development
- attach Redis pub/sub behind `ConnectionManager` for multi-instance websocket broadcast
- store attachments in object storage with signed URLs and server-side MIME validation
- never log secret message plaintext or wrapped key material
- expand rate limiting, audit logging, device-key management, and signature verification before production launch
