import debugpy



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

# seikaku = ""
# seikaku = seikaku + "あなたはラジオパーソナリティとして、中二病である四国めたんのロールプレイを行います"
# seikaku = seikaku + "「~かしら」、「~わよ」のような高飛車な口調"

import socket
import threading
import requests
import os
from datetime import datetime
import json
import time
import urllib.parse
import traceback  # エラー情報取得のためのモジュール


HOST = "0.0.0.0"  # すべてのインターフェースで待ち受け
FILE_PORT = 9542

WAV_DIR = "wav/"

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
            print("⚠️ ERROR: クライアントが正しく応答しませんでした fileDownload")

    except (ConnectionResetError, OSError) as e:
        print(f"⚠️ ERROR: クライアントとの通信中にエラー発生 - {e}")
        print(traceback.format_exc())

        return False

    return True

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
    client_socket.recv(2) 

    # クライアントに音声ファイルを送信
    with open(WAV_DIR + file_name, "rb") as f:
        while chunk := f.read(65536):
            client_socket.sendall(chunk)

    client_socket.recv(2)

def listenFileDownload():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, FILE_PORT))
        server_socket.listen()
        print(f"Server listening on {HOST}:{FILE_PORT}")

        while True:
            conn, addr = server_socket.accept()

            thread = threading.Thread(target=threadListenFileDownload, args=(conn, addr))
            thread.start()


def threadListenFileDownload(client_socket, addr):

    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

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

                    if json_data["action"] == "download":
                        downloadFile(json_data['value'], client_socket)
                        # response = f"Hello, {json_data['name']}!"

                except json.JSONDecodeError:
                    response = "Invalid JSON received"


            except ConnectionResetError:
                break

            # 受信データの取得--------------------------------------------------------↑

kokokara_message_dousa = False

# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

#     listen = threading.Thread(target=threadListenFileDownload)
#     threadListenFileDownload.start()

