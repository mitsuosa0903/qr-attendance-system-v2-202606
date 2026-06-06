import subprocess
import sys
import time
import signal
import os

def main():
    print("🚀 QR Attendance System - 一括起動スクリプト")
    print("------------------------------------------")

    processes = []

    # 起動するアプリの設定
    apps = [
        {"name": "入館アプリ", "cmd": [sys.executable, "in_app.py"], "url": "http://127.0.0.1:5001"},
        {"name": "退館アプリ", "cmd": [sys.executable, "out_app.py"], "url": "http://127.0.0.1:5002"},
        {"name": "管理アプリ", "cmd": [sys.executable, "admin_app.py"], "url": "http://127.0.0.1:5003"},
    ]

    try:
        for app in apps:
            print(f"📦 {app['name']} を起動中...")
            # stdout/stderrを継承させつつ、バックグラウンドで実行
            proc = subprocess.Popen(app['cmd'])
            processes.append(proc)
            time.sleep(1)  # 起動の感覚を少し開ける

        print("\n✅ すべてのシステムが起動しました！")
        print("------------------------------------------")
        for app in apps:
            print(f"🔗 {app['name']}: {app['url']}")
        print("------------------------------------------")
        print("💡 終了するには Ctrl+C を押してください。")

        # プロセスが動いている間待機
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n🛑 システムを終了しています...")
        for proc in processes:
            proc.terminate()
        print("👋 お疲れ様でした！")

if __name__ == "__main__":
    main()
