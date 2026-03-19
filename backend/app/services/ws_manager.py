from collections import defaultdict
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[user_id].add(websocket)

    def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal(self, user_id: str, message: dict[str, Any]) -> None:
        sockets = list(self.active_connections.get(user_id, set()))
        for socket in sockets:
            try:
                await socket.send_json(message)
            except Exception:
                self.disconnect(user_id, socket)


ws_manager = ConnectionManager()
