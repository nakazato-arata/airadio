import debugpy

# デバッグ用のポートを開放（VSCode から接続可能） VScodeでデバッグを行う。　本番稼働時はコメントアウト
debugpy.listen(("0.0.0.0", 5001))
print("Waiting for debugger to attach...")  # デバッガが接続されるまで待機
debugpy.wait_for_client()

import socket
import threading
from rcev import listenRcev
from fileDownload import listenFileDownload
from notif import listenNotif
import notif


kokokara_message_dousa = False

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

    listenRcevT = threading.Thread(target=listenRcev)
    listenRcevT.start()

    listenFileDownloadT = threading.Thread(target=listenFileDownload)
    listenFileDownloadT.start()
    
    listenSendT = threading.Thread(target=listenNotif)
    listenSendT.start()

    