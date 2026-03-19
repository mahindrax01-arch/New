# Social Media App (Vite + FastAPI + MongoDB)

Full-stack social media application with:
- Feed posting and Facebook-style reactions
- Friend request and connection system
- Live feed updates and notifications via WebSocket
- Access + refresh token auth with refresh-token rotation
- Role-based access control (`guest`, `user`, `admin`)
- Frontend ready for Clerk provider usage

## Tech Stack
- Backend: FastAPI, Motor, MongoDB, JWT
- Frontend: Vite, React, Tailwind CSS
- Optional Auth Provider Wrapper: Clerk (frontend)

## Project Structure
- `backend/`: FastAPI API server
- `frontend/`: Vite React app
- `docker-compose.yml`: MongoDB service

## 1) Start MongoDB

```bash
docker compose up -d
```

## 2) Run Backend

```bash
cd backend
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API base URL: `http://127.0.0.1:8000/api`

## 3) Run Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Frontend URL: `http://127.0.0.1:5173`

## Default Flow
1. Register users via frontend login/register panel.
2. Send friend requests using the receiver user ID.
3. Accept requests from pending list.
4. Create posts, react, and observe live notifications/feed updates.

## RBAC Notes
- `guest`: reserved role, no posting/reaction/friend request actions.
- `user`: standard social actions.
- `admin`: can do all user actions and update user roles.

Admin endpoint:
- `PATCH /api/auth/users/{user_id}/role?role=admin`

## WebSocket
- Endpoint: `ws://127.0.0.1:8000/ws?token=<access_token>`
- Event types:
  - `notification`
  - `feed:new_post`

## Clerk
`ClerkProvider` is pre-wired in `frontend/src/main.tsx` and enabled when `VITE_CLERK_PUBLISHABLE_KEY` is present. Backend currently uses JWT auth endpoints in `api/auth/*`.

## Local Dev Defaults
- Backend CORS accepts both `http://localhost:5173` and `http://127.0.0.1:5173`.
- Frontend falls back to the current browser hostname for API and WebSocket connections, so `localhost` and `127.0.0.1` both work without extra env changes.
