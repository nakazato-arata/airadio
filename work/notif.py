import asyncio
import websockets
import json
import os
import requests
import urllib.parse
import traceback
import random
import time
from datetime import datetime
from openai import OpenAI
from datetime import datetime

VOICE_VOX_API_URL = "http://host.docker.internal:50021"

HOST = "0.0.0.0"
PORT = 9541  # WebSocket ポート

# 音声ファイルの保存先
WAV_DIR = "wav/"

# API キー・URL
XAI_API_KEY = os.getenv("XAI_API_KEY")
AI_URL = os.getenv("AI_URL")

# AI のキャラ設定
seikaku = "お便りを受け付けるやニュースを読み上げるラジオ番組のパーソナリティとなってください"

# メッセージ履歴
messages = [{"role": "system", "content": seikaku}]

# 接続中のクライアント
connected_clients = set()

# メッセージキュー
msgQueue = []

async def openAiRequest(text):
    """ OpenAI API へリクエストを送り、返答を取得する """
    client = OpenAI(api_key=XAI_API_KEY, base_url=AI_URL)
    messages.append({"role": "user", "content": text})

    completion = client.chat.completions.create(
        model="grok-2-latest",
        messages=messages
    )

    response_text = completion.choices[0].message.content
    messages.append({"role": "assistant", "content": response_text})

    # 履歴が10件以上なら古いものを削除
    if len(messages) > 10:
        messages.pop(1)
        messages.pop(1)

    return response_text

async def voicevoxRequest(text):

    # 声を時間で変える---------------------------------------------------
    # 現在の時刻を取得
    current_time = datetime.now().time()

    # 22:00（夜10時）と 3:00（朝3時）の基準時刻を定義
    start_night = datetime.strptime("22:00", "%H:%M").time()
    end_night = datetime.strptime("03:00", "%H:%M").time()

    # 条件に基づいて speaker の値を変更
    if current_time >= start_night or current_time < end_night:
        speaker = "37"
    else:
        speaker = "2"
    # 声を時間で変える---------------------------------------------------        

    """ VoiceVox にリクエストを送り、音声ファイルを生成する """
    text_chunks = [text[i:i+100] for i in range(0, len(text), 100)]

    for idx, chunk in enumerate(text_chunks):
        encoded_text = urllib.parse.quote(chunk, encoding="utf-8")
        query_url = f"{VOICE_VOX_API_URL}/audio_query?text={encoded_text}&speaker=" + speaker

        try:
            query_response = requests.post(query_url, timeout=5)
            query_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"⚠️ ERROR: Query request failed - {e}")
            return

        synthesis_url = f"{VOICE_VOX_API_URL}/synthesis?speaker=" + speaker
        try:
            audio_response = requests.post(synthesis_url, json=query_response.json(), timeout=10)
            audio_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"⚠️ ERROR: Synthesis request failed - {e}")
            return

        current_date = datetime.now().strftime("%Y%m%d%H%M%S") + f"{datetime.now().microsecond // 1000:03d}"
        file_name = f"output_{current_date}_{idx}.wav"

        with open(WAV_DIR + file_name, "wb") as f:
            f.write(audio_response.content)

        initialize_speaker_url = f"{VOICE_VOX_API_URL}/initialize_speaker?speaker=" + speaker

        try:
            audio_response = requests.post(initialize_speaker_url, json=query_response.json(), timeout=10)
            audio_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"⚠️ ERROR: Synthesis request failed - {e}")
            return        

        # クライアントへ通知
        data = {"action": "fileCreate", "value": file_name}
        await broadcast(data)

async def handle_client(websocket):
    """ WebSocket クライアントとの通信処理 """
    global connected_clients
    print(f"Client connected: {websocket.remote_address}")
    connected_clients.add(websocket)

    try:
        async for message in websocket:
            print(f"Received: {message}")
            try:
                data = json.loads(message)
                action = data.get("action")
                value = data.get("value")

                if action == "otayori":
                    msgQueue.append(value)
            except json.JSONDecodeError:
                print("⚠️ Invalid JSON received")
                await websocket.send(json.dumps({"error": "Invalid JSON"}))

    except websockets.exceptions.ConnectionClosed:
        print(f"Client disconnected: {websocket.remote_address}")

    finally:
        connected_clients.remove(websocket)

async def broadcast(message):
    """ すべてのクライアントへメッセージを送信 """
    global connected_clients
    data = json.dumps(message)

    if connected_clients:
        tasks = [asyncio.create_task(client.send(data)) for client in connected_clients]
        await asyncio.wait(tasks)

async def delete_old_files():
    """ 10分以上経過した古い音声ファイルを削除 """
    now = time.time()
    threshold = now - 600

    for filename in os.listdir(WAV_DIR):
        file_path = os.path.join(WAV_DIR, filename)
        if os.path.isfile(file_path) and os.path.getctime(file_path) < threshold:
            os.remove(file_path)
            print(f"Deleted: {file_path}")


# async def main():
#     """ WebSocket サーバーを起動 """
#     server = await websockets.serve(handle_client, HOST, PORT)
#     print(f"WebSocket Server started at ws://{HOST}:{PORT}")

#     # 並行タスクを実行
#     await asyncio.gather(
#         server.wait_closed(),
#         message_processing_task(),
#         random_message_task(),
#     )

# if __name__ == "__main__":
#     asyncio.run(main())

async def huruiFileDelete():


    # 現在の時刻（Unixタイム）
    now = time.time()

    # 10分前の時刻（300秒前）
    threshold = now - 300  

    # 指定ディレクトリ内のファイルを走査
    for filename in os.listdir(WAV_DIR):
        file_path = os.path.join(WAV_DIR, filename)
        
        # ファイルかどうかを確認
        if os.path.isfile(file_path):
            # 作成時刻を取得
            created_time = os.path.getctime(file_path)
            
            # 10分前以前のファイルを削除
            if created_time < threshold:
                os.remove(file_path)
                print(f"削除しました: {file_path}")

async def kokokara_message():
    global connected_clients

    count = 0
    while True:
        await asyncio.sleep(1)  # 非同期で1秒待機

        # 溜まったメッセージを処理
        while msgQueue:
            msg = msgQueue.pop(0)  # 先頭のメッセージを取得
            airesponce = await openAiRequest(msg)  # 非同期処理
            await voicevoxRequest(airesponce)  # 非同期処理

        if count < 60:
            count += 1
            continue

        # 1分間通信がなければ、ランダムメッセージを送信
        if len(connected_clients) > 0:
            ramdamu = [
                "トンカツがおいしいです。なぜおいしいのでしょう",
                "沖縄の釣りスポットを教えてください",
                "春の旬の野菜を教えてください",
                "春に釣れる魚について教えてください",
                "宇宙人はいますか？",
                "霊は存在しますか",
                "ポケモンで草タイプの最強はどのポケモンですか？",
                "犬はなぜ散歩が好きなのでしょうか",
                "人間はなぜ争いが絶えなのですか？",
                "テラフォーミングは可能ですか？",
                "最新のガンプラが売り切れていて買えません。予約もすぐに閉め切られてしまいます。どうしたらいいですか？",
                "沖縄の春のイベントについて教えてください",
                "沖縄の祭りについて教えてください",
                "沖縄の不思議な話をしてください",
                "ドラゴンクエストウォークでは現在ドラゴンボールのコラボレーションイベントが開催されています。筋斗雲にのって日本を駆け巡ることができます。",
                "日本のカレーとインドカレーの違いについて教えてください",
                "とんかつの歴史について教えてください",
                "ステーキの意味について教えてください",
                "沖縄の方言について教えてください",
                "GROKとXについて教えてください",
                "エアブラシの洗浄方法について教えてください",
                "イカ釣りのコツについて教えてください",
                "イカの生き物としての欠点は美味しさなだと思いますがどうですか",
                "イノシシ鍋について教えてください",
                "イチゴの旬を教えてください。また栽培するコツはなんですか",
                "甘いトマトの栽培方法について教えてください",
                "スマホを落としたが警察に届けられていた。助かった",
            ]
            selected_text = random.choice(ramdamu)

            airesponce = await openAiRequest(selected_text)  # 非同期処理
            await voicevoxRequest(airesponce)  # 非同期処理
            count = 0

        # 古いファイルの削除
        await huruiFileDelete()


async def listenNotif():
    """ WebSocket サーバーを起動 """
    server = await websockets.serve(handle_client, HOST, PORT)
    print(f"WebSocket Server started at ws://{HOST}:{PORT}")

    # サーバーを非同期で実行
    # asyncio.create_task(server.wait_closed())

    # 別の非同期タスクを並行実行（ここでブロックしないようにする）
    asyncio.create_task(kokokara_message())

    await server.wait_closed()