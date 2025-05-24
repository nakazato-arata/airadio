# seikaku = "最新のニュースを挙げられますか？"
seikaku = "お便りを受け付けるやニュースを読み上げるラジオ番組のパーソナリティとなってください。制限として英語は使わないでください。センシティブは内容は避けてください"
# seikaku = seikaku + "「~かしら」、「~わよ」のような高飛車な口調"
# seikaku = "中二病の四国めたんとなり、手短に返答してください"

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
import rcev
import random
import os
import time

VOICE_VOX_API_URL = "http://host.docker.internal:50021"

HOST = "0.0.0.0"  # すべてのインターフェースで待ち受け
NOTIF_PORT = 9541

# OUTPUT_FILE = "output.wav"
WAV_DIR = "wav/"
XAI_API_KEY = os.getenv("XAI_API_KEY")

messages = []

messages.append({"role": "system", "content": seikaku})

clients = []

isAction = False

msgQueue = []

def openAiRequest(text):
    # クライアントの初期化
    client = OpenAI(
        api_key=XAI_API_KEY,
        base_url="https://api.x.ai/v1",
    )

    messages.append({"role": "user", "content": text})

    completion = client.chat.completions.create(
        model="grok-2-latest",
        # model="grok-2",
        messages= messages
    )

    print(completion.choices[0].message)

    messages.append({"role": "assistant", "content": completion.choices[0].message.content})

    # 10件以上のメッセージがあれば古いものから削除
    if len(messages) > 10:
        messages.pop(0)
        messages.pop(0)

    return completion.choices[0].message.content

def voicevoxRequest(text):
    # テキストを100文字ごとに分割
    text_chunks = [text[i:i+100] for i in range(0, len(text), 100)]


    # query_url = f"{VOICE_VOX_API_URL}/initialize_speaker?speaker=2"
    # query_response = requests.post(query_url, timeout=5)

    for idx, chunk in enumerate(text_chunks):
        encoded_text = urllib.parse.quote(chunk, encoding="utf-8")  # URLエンコード

        # 音声クエリ送信
        query_url = f"{VOICE_VOX_API_URL}/audio_query?text={encoded_text}&speaker=2"
        # query_url = f"{VOICE_VOX_API_URL}/audio_query?text=てすと&speaker=2"
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

        initialize_speaker_url = f"{VOICE_VOX_API_URL}/initialize_speaker?speaker=2"
        try:
            audio_response = requests.post(initialize_speaker_url, json=query_response.json(), timeout=10)
            audio_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"⚠️ ERROR: Failed to synthesize audio: {e}")
            return        

        data = {
            "action": "fileCreate",
            "value": file_name
        }

        # クライアントにファイル名を通知
        sends(data)

    # data = {
    #     "action": "fileCreate",
    #     "value": "end"
    # }

    # sends(data)    

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
            print("⚠️ ERROR: クライアントが正しく応答しませんでした　notif")
            return False

    except (ConnectionResetError, OSError) as e:
        print(f"⚠️ ERROR: クライアントとの通信中にエラー発生 - {e}")
        print(traceback.format_exc())

        # `client` が `clients` リストに含まれている場合のみ削除
        return False

    return True

# クライアント全体に送信
def sends(message):
    global clients

    errors = []

    for client in clients:
        if False == sendall(client, message):
            errors.append(client)

    for error in errors:
        clients.remove(error)

def listenNotif():
    global clients

    thread = threading.Thread(target=kokokara_message)
    thread.start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, NOTIF_PORT))
        server_socket.listen()
        print(f"Server listening on {HOST}:{NOTIF_PORT}")

        while True:
            conn, addr = server_socket.accept()
            clients.append(conn)

def huruiFileDelete():

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


def kokokara_message():
    global clients
    count = 0
    while True:
        time.sleep(1)  # 1秒待機

        # # 何かしら動作したらリセット
        # if rcev.isAction:
        #     count = 0
        #     # isAction = False
        #     continue

        # たまったお便りメッセージの文ループ
        while len(msgQueue) > 0:
            # 古いメッセージから処理する
            msg = msgQueue[0]
            airesponce = openAiRequest(msg)
            voicevoxRequest(airesponce)

            # 処理したメッセージを削除
            msgQueue.pop(0)

        if count < 60:
            count += 1
            continue

        # 何も通信がなくて1分経過したらメッセージを送信

        # message = "これは1分後に送信されるメッセージです"
        # client_socket.sendall(message.encode('utf-8'))
        # print(f"📤 1分後にメッセージ送信: {message}")

        if len(clients) < 1:
            continue

        # ここはランダムのトークを行う

        ramdamu = [
            "沖縄のニュースを読み上げてください",
            "沖縄の釣りスポットを教えてください",
            "春の花について話題を挙げてください",
            "春に釣れる魚について教えてください",
            "沖縄の観光スポットを教えてください",
            "沖縄の春のイベントについて教えてください",
            "沖縄の祭りについて教えてください",
            "沖縄の不思議な話をしてください",
            "ドラゴンクエストウォークでは現在ドラゴンボールのコラボレーションイベントが開催されています。筋斗雲にのって日本を駆け巡ることができます。",
            "ドラゴンクエストウォークではドラゴンボールのコラボレーションの一部で大猿とのギガモンが開催されます。",
            "欲求に抗うのは無図解しことです、体によく、費用もかからない欲求を満たす方法はありますか？",
            "日本のカレーとインドカレーの違いについて教えてください",
            "とんかつの歴史について教えてください",
            "ステーキの意味について教えてください",
            "沖縄の方言について教えてください",
            "GROKとXについて教えてください",
            "エアブラシの洗浄方法について教えてください",
            "イカ釣りのコツについて教えてください",
            "イカの欠点は美味しさなだと思いますがどうですか",
            "イノシシ鍋について教えてください",
            "イチゴの旬を教えてください。また栽培するコツはなんですか",
            "甘いトマトの栽培方法について教えてください",
            "タングステンはどのくらい固いですか。またどのような用途に使われていますか",
        ]

        # ランダムに1つ選択
        selected_text = random.choice(ramdamu)

        airesponce = openAiRequest(selected_text)
        voicevoxRequest(airesponce)
        count = 0
        huruiFileDelete()