import socket
import threading
# クライアントの処理を行う関数
def handle_client(client_socket, address):
    print(f"[接続] クライアント {address} から接続されました。")
    while True:
        try:
            data = client_socket.recv(1024)  # データを受信
            if not data:
                break  # クライアントが切断した場合
            print(f"[受信] {address} : {data.decode('utf-8')}")
            client_socket.sendall(f"受信: {data.decode('utf-8')}".encode('utf-8'))  # クライアントに返信
        except ConnectionResetError:
            break  # クライアントが強制切断した場合
    print(f"[切断] クライアント {address} が切断しました。")
    client_socket.close()  # 接続を閉じる
    
def start_server(host="0.0.0.0", port=12345):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)  # 最大接続数
    print(f"[開始] サーバーが {host}:{port} で待機中...")
    while True:
        client_socket, addr = server.accept()  # 新しいクライアントを受け入れる
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()  # 新しいスレッドでクライアント処理を開始
if __name__ == "__main__":
    start_server()











