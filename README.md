# Social Media App (Vite + FastAPI + MongoDB-ready)

A starter social media application with:

- Feed posts + reactions
- Friend connections
- Live feed/notifications over WebSocket
- Access + refresh token rotation
- Role-based access control (guest/user/admin)

## Stack
- Backend: FastAPI
- Frontend: Vite + React + Tailwind
- Auth-ready: Clerk integration points
- DB-ready: MongoDB repositories (currently in-memory for local bootstrap)

## Environment files

Create local env files from examples before running:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### Backend env vars (`backend/.env`)
- `SECRET_KEY`: JWT signing key
- `ACCESS_TOKEN_EXPIRES_MINUTES`: access token TTL in minutes
- `REFRESH_TOKEN_EXPIRES_MINUTES`: refresh token TTL in minutes
- `CORS_ALLOW_ORIGINS`: comma-separated frontend origins

### Frontend env vars (`frontend/.env`)
- `VITE_API_URL`: backend API base URL (e.g. `http://localhost:8000` or deployed backend URL)

## Run

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Notes
- This repository is intentionally scaffold-first so you can swap in Mongo collections and Clerk JWT verification quickly.
- See inline TODO notes for production hardening steps.


## Deploy (Render backend + Vercel frontend)

### Backend on Render
1. Create a **Web Service** from this repo.
2. Set Root Directory to `backend`.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Use **Python 3.12.x** (important for compatibility with pinned dependencies).

This repo includes `render.yaml` and `runtime.txt` to pin Python 3.12.8 and standardize Render deployment.

### Frontend on Vercel
1. Create a Vercel project with Root Directory `frontend`.
2. Add env var `VITE_API_URL=<your-render-backend-url>`.
3. Deploy and verify requests go to your backend URL.
