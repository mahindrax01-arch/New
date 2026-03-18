import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import SessionLocal
from app.models import ConversationMember, User
from app.schemas.chat import MessageCreate, TypingPayload
from app.services.chat import ChatService
from app.websocket.manager import manager

router = APIRouter(tags=['ws'])


@router.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket, token: str) -> None:
    db: Session = SessionLocal()
    try:
        payload = decode_token(token)
        user = db.get(User, payload.get('sub'))
        if not user:
            await websocket.close(code=4401)
            return
        await manager.connect(user.id, websocket)
        await manager.send_user(user.id, {'type': 'presence', 'userId': user.id, 'isOnline': True})
        while True:
            data = json.loads(await websocket.receive_text())
            match data.get('type'):
                case 'subscribe':
                    conversation_id = data['conversationId']
                    membership = db.scalar(select(ConversationMember).where(ConversationMember.conversation_id == conversation_id, ConversationMember.user_id == user.id))
                    if membership:
                        manager.join_room(conversation_id, websocket)
                case 'typing':
                    payload = TypingPayload(conversation_id=data['conversationId'], is_typing=bool(data.get('isTyping')))
                    await manager.broadcast_room(payload.conversation_id, {'type': 'typing', 'conversationId': payload.conversation_id, 'userId': user.id, 'isTyping': payload.is_typing})
                case 'message.create':
                    message = ChatService(db).create_message(user, MessageCreate(**data['payload']))
                    await manager.broadcast_room(message.conversation_id, {'type': 'message.created', 'payload': message.model_dump(mode='json')})
                case 'ping':
                    await websocket.send_json({'type': 'pong'})
    except WebSocketDisconnect:
        pass
    finally:
        if 'user' in locals():
            manager.disconnect(user.id, websocket)
        db.close()
