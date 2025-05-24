FROM python:3.11


WORKDIR /work

# openai モジュールのインストール
RUN pip install openai pip fastapi uvicorn websockets pydub ffmpeg-python aiohttp

COPY ./requirements.txt /work/requirements.txt
RUN pip install --no-cache-dir -r /work/requirements.txt

RUN apt update && apt install -y ffmpeg