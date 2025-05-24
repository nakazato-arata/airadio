import debugpy

# デバッグ用のポートを開放（VSCode から接続可能） VScodeでデバッグを行う。　本番稼働時はコメントアウト
debugpy.listen(("0.0.0.0", 5001))
print("Waiting for debugger to attach...")  # デバッガが接続されるまで待機
debugpy.wait_for_client()


# import ptvsd
# ptvsd.enable_attach("my_secret", address = ('0.0.0.0', 5001))
# ptvsd.wait_for_attach()
# ptvsd.break_into_debugger()

# # Flask のインポート
# from flask import Flask

# app = Flask(__name__)

# @app.route("/")
# def home():
#     return "Hello, Docker with Debugger!"

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=9540)

seikaku = ""
seikaku = seikaku + "あなたはラジオパーソナリティとして、中二病である四国めたんのロールプレイを行います"
seikaku = seikaku + "「~かしら」、「~わよ」のような高飛車な口調"

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

VOICE_VOX_API_URL = "http://host.docker.internal:50021"

HOST = "0.0.0.0"  # すべてのインターフェースで待ち受け
PORT = 9540       # 使用するポート

FILE_PORT = 9541

# OUTPUT_FILE = "output.wav"
WAV_DIR = "wav/"
XAI_API_KEY = 'xai-OsnW4Jd4YJFXiuPz7q5bR69ScQHBwB1lnc0BPIAFpUn88UkshxaSB6rjvcCOLLGpp2sKUuIiWqQSgiRN'

messages = []

messages.append({"role": "system", "content": seikaku})

clients = []

isAction = False

def openAiRequest(text):
    # クライアントの初期化
    client = OpenAI(
        api_key=XAI_API_KEY,
        base_url="https://api.x.ai/v1",
    )

    messages.append({"role": "user", "content": text})

    completion = client.chat.completions.create(
        model="grok-2-latest",
        messages= messages
    )

    print(completion.choices[0].message)

    return completion.choices[0].message

def voicevoxRequest(text):
    # テキストを100文字ごとに分割
    text_chunks = [text[i:i+100] for i in range(0, len(text), 100)]

    for idx, chunk in enumerate(text_chunks):
        encoded_text = urllib.parse.quote(chunk)  # URLエンコード

        # 音声クエリ送信
        query_url = f"{VOICE_VOX_API_URL}/audio_query?text={encoded_text}&speaker=2"
        try:
            query_response = requests.post(query_url, timeout=5)
            query_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"⚠️ ERROR: Failed to create query: {e}")
            return

        # 音声合成リクエスト
        synthesis_url = f"{VOICE_VOX_API_URL}/synthesis?speaker=2"
        try:
            audio_response = requests.post(synthesis_url, json=query_response.json(), timeout=10)
            audio_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"⚠️ ERROR: Failed to synthesize audio: {e}")
            return

        # 音声ファイルを保存
        current_date = datetime.now().strftime("%Y%m%d%H%M%S") + f"{datetime.now().microsecond // 1000:03d}"
        file_name = f"output_{current_date}_{idx}.wav"

        with open(WAV_DIR + file_name, "wb") as f:
            f.write(audio_response.content)

        data = {
            "action": "fileCreate",
            "value": file_name
        }

        # クライアントにファイル名を通知
        sends(data)

    data = {
        "action": "fileCreate",
        "value": "end"
    }

    sends(data)            

def downloadFile(file_name, client_socket):

    file_size = os.path.getsize(WAV_DIR + file_name)

    data = {
        "action": "fileDownload",
        "value": file_size
    }

    # client_socket.sendall(json.dumps(data).encode('utf-8'))  # 文字列をエンコード

    # # クライアントからの "OK" を待つ
    # client_socket.recv(1024)
    sendall(client_socket, data)

    # クライアントに音声ファイルを送信
    with open(WAV_DIR + file_name, "rb") as f:
        while chunk := f.read(1024):
            client_socket.sendall(chunk)
            client_socket.recv(1024)

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
            print("⚠️ ERROR: クライアントが正しく応答しませんでした")

    except (ConnectionResetError, OSError) as e:
        print(f"⚠️ ERROR: クライアントとの通信中にエラー発生 - {e}")
        print(traceback.format_exc())

        # `client` が `clients` リストに含まれている場合のみ削除
        return False

    return True

# クライアント全体に送信
def sends(message):

    errors = []

    for client in clients:
        if False == sendall(client, message):
            errors.append(client)

    for error in errors:
        clients.remove(error)     

def handle_client(client_socket, addr):
    """クライアントごとに実行される処理"""
    print(f"Connected by {addr}")
    with client_socket:
        while True:
            try:
                data = client_socket.recv(1024).decode("utf-8")
                if not data:
                    break
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
                        airesponce = openAiRequest(json_data['value'])

                        messages.append({"role": "assistant", "content": airesponce.content})

                        voicevoxRequest(airesponce.content)
                        # response = f"Hello, {json_data['name']}!"
                    elif json_data["action"] == "download":
                        downloadFile(json_data['value'], client_socket)

                    elif json_data["action"] == "downloadsEnd":
                        isAction = False
                    else:
                        response = "Unknown action"

                except json.JSONDecodeError:
                    response = "Invalid JSON received"


            except ConnectionResetError:
                #  接続が終了したらリストから外す
                clients.remove(client_socket)
                break


            # 受信データの取得--------------------------------------------------------↑

    print(f"Connection closed: {addr}")
    
def kokokara_message():
    
    global isAction

    count = 0
    while True:
        time.sleep(1)  # 1秒待機

        # 何かしら動作したらリセット
        if isAction:
            count = 0
            # isAction = False
            continue

        if count < 10:
            count += 1
            continue

        # 何も通信がなくて1分経過したらメッセージを送信

        # message = "これは1分後に送信されるメッセージです"
        # client_socket.sendall(message.encode('utf-8'))
        # print(f"📤 1分後にメッセージ送信: {message}")

        if len(clients) < 1:
            continue

        airesponce = openAiRequest("面白いニュースはありますか？")
        voicevoxRequest(airesponce.content)

kokokara_message_dousa = False

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        conn, addr = server_socket.accept()

        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        clients.append(conn)


        if len(clients) == 1 and not kokokara_message_dousa:
            # サーバから発言するスレッド
            kokokaraThread = threading.Thread(target=kokokara_message)
            kokokaraThread.start()
            kokokara_message_dousa = True