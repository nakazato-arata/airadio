import debugpy

# デバッグ用のポートを開放（VSCode から接続可能） VScodeでデバッグを行う。　本番稼働時はコメントアウト
debugpy.listen(("0.0.0.0", 5001))
print("Waiting for debugger to attach...")  # デバッガが接続されるまで待機
debugpy.wait_for_client()

import asyncio
import websockets
from rcev import listenRcev
from fileDownload import listenFileDownload
from notif import listenNotif


async def main():
    """ WebSocket サーバーを3つ並行実行 """
    await asyncio.gather(
        listenRcev(),          # メッセージ受信
        listenFileDownload(),  # ファイルダウンロード
        listenNotif()          # 通知送信
    )

if __name__ == "__main__":
    asyncio.run(main())