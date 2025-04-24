workフォルダが最新  
work05フォルダはソケット通信(クライアントUnity)、workフォルダWebSocket通信(クライアントWebブラウザ)  

本番環境実行  
app.pyの以下をコメントアウト
```
import debugpy

# デバッグ用のポートを開放（VSCode から接続可能） VScodeでデバッグを行う。　本番稼働時はコメントアウト
debugpy.listen(("0.0.0.0", 5001))
print("Waiting for debugger to attach...")  # デバッガが接続されるまで待機
debugpy.wait_for_client()
```

デバッグ時
VSCodeで行う。python実行後、デバッグ実行を行う。(ロジックで5001ポートを待ち受けを行っていてlistenしないと後続が動かない)  