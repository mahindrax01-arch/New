from collections import defaultdict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()
clients: dict[str, set[WebSocket]] = defaultdict(set)


@router.websocket("/notifications/{user_id}")
async def notifications(user_id: str, ws: WebSocket) -> None:
    await ws.accept()
    clients[user_id].add(ws)
    try:
        while True:
            message = await ws.receive_text()
            for client in clients[user_id]:
                await client.send_text(f"live:{message}")
    except WebSocketDisconnect:
        clients[user_id].discard(ws)
