from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.chat import router as chat_router
from app.api.routes.ws import router as ws_router
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(title='CipherChat API', version='0.1.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.cors_origins],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(ws_router)


@app.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}
