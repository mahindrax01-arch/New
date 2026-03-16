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
