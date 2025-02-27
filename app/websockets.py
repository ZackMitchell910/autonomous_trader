# app/websockets.py
from fastapi import WebSocket
import json

async def websocket_endpoint(websocket: WebSocket, user: User):
    await websocket.accept()
    while True:
        trade = await get_new_trade(user)  # Hypothetical function
        await websocket.send_text(json.dumps(trade))