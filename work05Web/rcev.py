# seikaku = "最新のニュースを挙げられますか？"
# seikaku = "中二病の四国めたんとなり、お便りを受け付けるやニュースを読み上げるラジオ番組のパーソナリティとなってください"
# seikaku = seikaku + "「~かしら」、「~わよ」のような高飛車な口調"

import socket
import threading
import requests
import os
from openai import OpenAI
from datetime import datetime
import json
import time
import urllib.parse
import traceback  # エラー情報取得のためのモジュール
import notif

VOICE_VOX_API_URL = "http://host.docker.internal:50021"

HOST = "0.0.0.0"  # すべてのインターフェースで待ち受け
PORT_RECV = 9540       # 使用するポート

# OUTPUT_FILE = "output.wav"
WAV_DIR = "wav/"
# XAI_API_KEY = os.getenv("MY_VAR")

messages = []

# messages.append({"role": "system", "content": seikaku})

connection = None

isAction = False

# def openAiRequest(text):
#     # クライアントの初期化
#     client = OpenAI(
#         api_key=XAI_API_KEY,
#         base_url="https://api.x.ai/v1",
#     )

#     messages.append({"role": "user", "content": text})

#     completion = client.chat.completions.create(
#         model="grok-2-latest",
#         # model="grok-2",
#         messages= messages
#     )

#     print(completion.choices[0].message)

#     return completion.choices[0].message

# def voicevoxRequest(text):
#     global isAction
#     # テキストを100文字ごとに分割
#     text_chunks = [text[i:i+100] for i in range(0, len(text), 100)]

#     for idx, chunk in enumerate(text_chunks):
#         encoded_text = urllib.parse.quote(chunk)  # URLエンコード

#         # 音声クエリ送信
#         query_url = f"{VOICE_VOX_API_URL}/audio_query?text={encoded_text}&speaker=2"
#         try:
#             query_response = requests.post(query_url, timeout=5)
#             query_response.raise_for_status()
#         except requests.exceptions.RequestException as e:
#             print(f"⚠️ ERROR: Failed to create query: {e}")
#             return

#         # 音声合成リクエスト
#         synthesis_url = f"{VOICE_VOX_API_URL}/synthesis?speaker=2"
#         try:
#             audio_response = requests.post(synthesis_url, json=query_response.json(), timeout=10)
#             audio_response.raise_for_status()
#         except requests.exceptions.RequestException as e:
#             print(f"⚠️ ERROR: Failed to synthesize audio: {e}")
#             return

#         # 音声ファイルを保存
#         current_date = datetime.now().strftime("%Y%m%d%H%M%S") + f"{datetime.now().microsecond // 1000:03d}"
#         file_name = f"output_{current_date}_{idx}.wav"

#         with open(WAV_DIR + file_name, "wb") as f:
#             f.write(audio_response.content)

#         # data = {
#         #     "action": "fileCreate",
#         #     "value": file_name
#         # }

#         # # クライアントにファイル名を通知
#         # sends(data)

#     # data = {
#     #     "action": "fileCreate",
#     #     "value": "end"
#     # }

#     # sends(data)
    # isAction = False

def sendall(client, message):

    try:
        # 既に閉じられたソケットでないかチェック
        if client.fileno() == -1:
            print("⚠️ ERROR: クライアントのファイルディスクリプタが無効です（接続が切れている可能性あり）")
            return False

        # メッセージ送信
        client.sendall(json.dumps(message).encode('utf-8'))

        # ACK 受信
        ack = client.recv(1024)  
        if ack.decode() != "OK":
            print("⚠️ ERROR: クライアントが正しく応答しませんでした rcev")

    except (ConnectionResetError, OSError) as e:
        print(f"⚠️ ERROR: クライアントとの通信中にエラー発生 - {e}")
        print(traceback.format_exc())

        return False

    return True

# クライアント全体に送信
def sends(message):
    global connection
    errors = []

    sendall(connection, message)

def listenRcev():
    global connection
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT_RECV))
        server_socket.listen()
        print(f"Server listening on {HOST}:{PORT_RECV}")

        while True:
            conn, addr = server_socket.accept()

            thread = threading.Thread(target=handle_client_rcev, args=(conn, addr))
            thread.start()
            connection = conn

def handle_client_rcev(client_socket, addr):

    global isAction
    """クライアントごとに実行される処理"""
    print(f"Connected by {addr}")
    # with client_socket:
    #     while True:
    #         try:
    #             data = client_socket.recv(1024).decode("utf-8")
    #             if not data:
    #                 break
    #             print(f"Received from {addr}: {data}")
                

    #             # 受信データの取得--------------------------------------------------------↓

    #             # JSONデータの解析
    #             try:
    #                 json_data = json.loads(data)
    #                 print("Received JSON:", json_data)

    #                 # 処理の分岐
    #                 if json_data["action"] == "otayori":
    #                     isAction = True

    #                     # お便りの場合
    #                     # airesponce = openAiRequest(json_data['value'])
    #                     notif.messages.append(json_data['value'])
    #                     # messages.append({"role": "assistant", "content": airesponce.content})

    #                     # voicevoxRequest(airesponce.content)
    #                     # response = f"Hello, {json_data['name']}!"
    #                     sendall(client_socket, {"action": "otayori", "value": "end"})

    #             except json.JSONDecodeError:
    #                 response = "Invalid JSON received"


    #         except ConnectionResetError:
    #             break


    try:
        data = client_socket.recv(1024).decode("utf-8")

        print(f"Received from {addr}: {data}")
        

        # 受信データの取得--------------------------------------------------------↓

        # JSONデータの解析
        try:
            json_data = json.loads(data)
            print("Received JSON:", json_data)

            # 処理の分岐
            if json_data["action"] == "otayori":
                isAction = True

                # お便りの場合
                # airesponce = openAiRequest(json_data['value'])
                notif.msgQueue.append(json_data['value'])
                # messages.append({"role": "assistant", "content": airesponce.content})

                # voicevoxRequest(airesponce.content)
                # response = f"Hello, {json_data['name']}!"
                # sendall(client_socket, {"action": "otayori", "value": "end"})

        except json.JSONDecodeError:
            response = "Invalid JSON received"


    except ConnectionResetError:
        print("ConnectionResetError")
    finally:
        client_socket.close()

            # 受信データの取得--------------------------------------------------------↑