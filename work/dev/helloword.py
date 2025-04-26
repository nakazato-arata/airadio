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
from pydub import AudioSegment
import ffmpeg
import subprocess
import aiohttp

import re
import json

VOICE_VOX_API_URL = "http://host.docker.internal:50021"

os.environ['TZ'] = 'Asia/Tokyo'

HOST = "0.0.0.0"
PORT = 9541  # WebSocket ポート

# 音声ファイルの保存先
WAV_DIR = "wav/"

# 文字列を登場人物とセリフに分ける
# 例：
# A「それでは、リスナーの皆さんからいただいたお便りをご紹介しますね。ペンネーム"おくら"さんからのお便りです。『今日は休日出勤です。涼しいです。明日は休みなので頑張ろうと思います。』というお便りをいただきました。おくらさん、休日出勤お疲れ様です。涼しい中でのお仕事、気持ちよさそうですね。明日はしっかり休んでくださいね。」 B「そうですね、涼しいと仕事もはかどりますよね。おくらさん、明日の休みの予定は何かありますか？リラックスして楽しむといいですね。」
# 処理結果
# [
# 	{"Speaker": "A", "value": "それでは、リスナーの皆さんからいただいたお便りをご紹介しますね..."},
# 	{"Speaker": "A", "value": "明日はしっかり休んでくださいね"},
# 	{"Speaker": "B", "value": "そうですね、涼しいと仕事もはかどりますよね..."},
def splitTextBySpeaker(text, max_length=100):
    # スピーカーとセリフのペアを抽出
    pattern = r'([A-Z])「(.*?)」'
    matches = re.findall(pattern, text)

    result = []

    for speaker, value in matches:
        # 100文字ごとに分割
        chunks = [value[i:i+max_length] for i in range(0, len(value), max_length)]
        for chunk in chunks:
            result.append({
                "Speaker": speaker,
                "value": chunk
            })
    

    # return json.dumps(result, indent=2, ensure_ascii=False)
    return result

def merge_wav_to_mp3(files, file_list):
    current_date = datetime.now().strftime("%Y%m%d%H%M%S") + f"{datetime.now().microsecond // 1000:03d}"
    # list_file_path = os.path.join(WAV_DIR, f"file_list{current_date}.txt")
    # output_mp3_path = os.path.join(WAV_DIR, f"output_{current_date}.mp3")
    output_ogg_path = os.path.join(WAV_DIR, f"output_{current_date}.ogg")

    # file_list.txt を作成
    with open(WAV_DIR + file_list, "w") as f:
        for file in files:
            f.write(f"file '{os.path.join(file)}'\n")

    # ffmpeg コマンドを実行 mp3
    # command = [
    #     "ffmpeg",
    #     "-f", "concat",
    #     "-safe", "0",
    #     "-i", WAV_DIR + file_list,
    #     "-c:a", "libmp3lame",
    #     "-q:a", "5",  # MP3の品質設定（2は高品質、値が小さいほど高品質）
    #     output_mp3_path
    # ]

    # ogg
    command = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", WAV_DIR + file_list,
        "-c:a", "libopus",  # or libvorbis if you prefer
        "-b:a", "24k",
        output_ogg_path
    ]
    

    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # print("✅ MP3 変換成功:", output_mp3_path)
        print("✅ MP3 変換成功:", output_ogg_path)        
    except subprocess.CalledProcessError as e:
        print("⚠️ ffmpegエラー:", e.stderr)

    # 作成したリストファイルを削除
    os.remove(WAV_DIR + file_list)

    # return output_mp3_path
    return output_ogg_path

# 2人で掛け合いを行う
# Aさん「発言」Bさん「発言」を受け取り、音声を作成それを結合してoggに結合する
async def voicevoxRequest(text):

    # 22:00（夜10時）と 3:00（朝3時）の基準時刻を定義
    global start_night
    global end_night

    # 現在の時刻を取得
    current_time = datetime.now().time()

    metanSannSpeaker = "2"
    zundamonSpeaker = "1"

    bunkatu = splitTextBySpeaker(text)

    files = []

    for i, line in enumerate(bunkatu):
        print(line['Speaker'])
        print(line['value'])

        connector = aiohttp.TCPConnector(ssl=False)

        speaker = zundamonSpeaker

        if line['Speaker'] == "A":
            speaker = zundamonSpeaker
        else:
            speaker = metanSannSpeaker

        async with aiohttp.ClientSession(connector=connector) as session:

            encoded_text = urllib.parse.quote(line['value'], encoding="utf-8")
            query_url = f"{VOICE_VOX_API_URL}/audio_query?text={encoded_text}&speaker=" + speaker


            try:
                async with session.post(query_url, timeout=10) as query_response:
                    query_data = await query_response.json()
            except Exception as e:
                print(f"⚠️ ERROR: Query failed - {e}")
                return

            synthesis_url = f"{VOICE_VOX_API_URL}/synthesis?speaker=" + speaker
            try:
                async with session.post(synthesis_url, json=query_data, timeout=20) as audio_response:
                    audio_data = await audio_response.read()
                    current_date = datetime.now().strftime("%Y%m%d%H%M%S") + f"{datetime.now().microsecond // 1000:03d}"
                    file_name = f"output_{current_date}.wav"

                    with open(WAV_DIR + file_name, "wb") as f:
                        f.write(audio_data)

            except Exception as e:
                print(f"⚠️ ERROR: Synthesis failed - {e}")
                return



            files.append(file_name)

    current_date = datetime.now().strftime("%Y%m%d%H%M%S") + f"{datetime.now().microsecond // 1000:03d}"
    file_list = f"file_list{current_date}.txt"
    with open(WAV_DIR + file_list, "w") as f:
        for file in files:
            f.write(f"file '{file}'\n")

    filename = merge_wav_to_mp3(files, file_list)

    print("ファイル名", filename)



    # VoiceVox に100文字ずつ分割リクエストを送り、音声ファイルを生成する (文字列が長いとエラーになる)
    # text_chunks = [text[i:i+100] for i in range(0, len(text), 100)]
    # files = []

    # connector = aiohttp.TCPConnector(ssl=False)

    # async with aiohttp.ClientSession(connector=connector) as session:

    #     for idx, chunk in enumerate(text_chunks):
    #         encoded_text = urllib.parse.quote(chunk, encoding="utf-8")
    #         query_url = f"{VOICE_VOX_API_URL}/audio_query?text={encoded_text}&speaker=" + speaker


    #         try:
    #             async with session.post(query_url, timeout=10) as query_response:
    #                 query_data = await query_response.json()
    #         except Exception as e:
    #             print(f"⚠️ ERROR: Query failed - {e}")
    #             return

    #         synthesis_url = f"{VOICE_VOX_API_URL}/synthesis?speaker=" + speaker
    #         try:
    #             async with session.post(synthesis_url, json=query_data, timeout=20) as audio_response:
    #                 audio_data = await audio_response.read()
    #                 current_date = datetime.now().strftime("%Y%m%d%H%M%S") + f"{datetime.now().microsecond // 1000:03d}"
    #                 file_name = f"output_{current_date}_{idx}.wav"

    #                 with open(WAV_DIR + file_name, "wb") as f:
    #                     f.write(audio_data)

    #         except Exception as e:
    #             print(f"⚠️ ERROR: Synthesis failed - {e}")
    #             return



    #         files.append(file_name)

    # current_date = datetime.now().strftime("%Y%m%d%H%M%S") + f"{datetime.now().microsecond // 1000:03d}"
    # file_list = f"file_list{current_date}.txt"
    # with open(WAV_DIR + file_list, "w") as f:
    #     for file in files:
    #         f.write(f"file '{file}'\n")

    # filename = merge_wav_to_mp3(files, file_list)

    # # クライアントへ通知
    # data = {"action": "fileCreate", "value": filename.replace("wav/", "")}
    # await broadcast(filename)


async def main():
    await voicevoxRequest("A「それでは、リスナーの皆さんからいただいたお便りをご紹介しますね。ペンネーム\"おくら\"さんからのお便りです。『今日は休日出勤です。涼しいです。明日は休みなので頑張ろうと思います。』というお便りをいただきました。おくらさん、休日出勤お疲れ様です。涼しい中でのお仕事、気持ちよさそうですね。明日はしっかり休んでくださいね。」 B「そうですね、涼しいと仕事もはかどりますよね。おくらさん、明日の休みの予定は何かありますか？リラックスして楽しむといいですね。」")


if __name__ == "__main__":
    asyncio.run(main())