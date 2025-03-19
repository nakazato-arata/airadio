import asyncio
import websockets
import json
import os
import traceback
from datetime import datetime

HOST = "0.0.0.0"
FILE_PORT = 9542
WAV_DIR = "wav/"

async def send_json(websocket, message):
    """ クライアントへJSONメッセージを送信し、ACKを待つ """
    try:
        await websocket.send(json.dumps(message))
        ack = await websocket.recv()
        if ack != "OK":
            print("⚠️ ERROR: クライアントが正しく応答しませんでした fileDownload")
            return False
    except Exception as e:
        print(f"⚠️ ERROR: クライアントとの通信エラー - {e}")
        print(traceback.format_exc())
        return False
    return True

async def download_file(websocket, file_name):
    """ 指定されたファイルをクライアントに送信 """
    file_path = os.path.join(WAV_DIR, file_name)
    
    if not os.path.exists(file_path):
        print(f"⚠️ ERROR: ファイルが見つかりません - {file_path}")
        return
    
    # file_size = os.path.getsize(file_path)
    # data = {"action": "fileDownload", "value": file_size}
    # success = await send_json(websocket, data)
    # if not success:
    #     return

    # await websocket.recv()  # クライアントの準備OK待ち
    
    try:
        with open(file_path, "rb") as f:
            file_data = f.read()  # 一度に全データを読み込む
            await websocket.send(file_data)  # 1回で送信
            print(f"📤 ファイル送信完了: {file_name} ({len(file_data)} bytes)")
            
    except Exception as e:
        print(f"⚠️ ERROR: ファイル送信エラー - {e}")
        print(traceback.format_exc())

async def handle_client(websocket):
    """ クライアント接続ごとの処理 """
    print(f"Client connected: {websocket.remote_address}")
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                print(f"Received: {data}")
                
                if data.get("action") == "download":
                    await download_file(websocket, data["value"])
            except json.JSONDecodeError:
                print("⚠️ ERROR: Invalid JSON received")
                await websocket.send(json.dumps({"error": "Invalid JSON"}))
    except websockets.exceptions.ConnectionClosed:
        print(f"Client disconnected: {websocket.remote_address}")

# async def main():
#     """ WebSocketサーバーを起動 """
#     server = await websockets.serve(handle_client, HOST, FILE_PORT)
#     print(f"WebSocket Server started at ws://{HOST}:{FILE_PORT}")
#     await server.wait_closed()

# if __name__ == "__main__":
#     asyncio.run(main())

async def listenFileDownload():
    """ WebSocketサーバーを起動 """
    server = await websockets.serve(handle_client, HOST, FILE_PORT)
    print(f"WebSocket Server started at ws://{HOST}:{FILE_PORT}")
    await server.wait_closed()    