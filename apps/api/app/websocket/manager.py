from collections import defaultdict
from dataclasses import dataclass

from fastapi import WebSocket


@dataclass
class SocketClient:
    user_id: str
    websocket: WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.connections: dict[str, set[WebSocket]] = defaultdict(set)
        self.rooms: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections[user_id].add(websocket)

    def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        self.connections[user_id].discard(websocket)
        for room in self.rooms.values():
            room.discard(websocket)

    def join_room(self, conversation_id: str, websocket: WebSocket) -> None:
        self.rooms[conversation_id].add(websocket)

    async def send_user(self, user_id: str, payload: dict) -> None:
        for socket in list(self.connections[user_id]):
            await socket.send_json(payload)

    async def broadcast_room(self, conversation_id: str, payload: dict) -> None:
        for socket in list(self.rooms[conversation_id]):
            await socket.send_json(payload)


manager = ConnectionManager()
