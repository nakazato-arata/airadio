import asyncio
import websockets
import json
import traceback
import stream

HOST = "0.0.0.0"
PORT = 9540

connected_clients = set()

async def handle_client(websocket):
    """ クライアントとの接続を処理 """
    print(f"Client connected: {websocket.remote_address}")
    connected_clients.add(websocket)

    try:
        async for message in websocket:
            print(f"Received: {message}")

            try:
                # JSON を解析
                data = json.loads(message)
                action = data.get("action")
                value = data.get("value")

                if action == "otayori":
                    print(f"📩 お便り受信: {value}")
                    
                    # # 送信メッセージ作成
                    # response = {"action": "otayori", "value": "end"}
                    
                    # # クライアントに返信
                    # await websocket.send(json.dumps(response))

                    stream.msgQueue.append(value)

            except json.JSONDecodeError:
                print("⚠️ JSON の解析に失敗")
                await websocket.send(json.dumps({"error": "Invalid JSON"}))

    except websockets.exceptions.ConnectionClosed as e:
        print(f"rcev Connection closed: {e}")

    finally:
        connected_clients.remove(websocket)

# async def main():
#     """ WebSocket サーバーを起動 """
#     server = await websockets.serve(handle_client, HOST, PORT)
#     print(f"WebSocket Server started at ws://{HOST}:{PORT}")
#     await server.wait_closed()

# if __name__ == "__main__":
#     asyncio.run(main())

async def listenRcev():
    server = await websockets.serve(handle_client, HOST, PORT)
    print(f"WebSocket Server started at ws://{HOST}:{PORT}")
    await server.wait_closed()