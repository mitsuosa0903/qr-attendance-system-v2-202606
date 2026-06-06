import pytest
import sqlite3
from pathlib import Path
import multiprocessing
import time
import sys
import os

# アプリケーションのパスを通す
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import in_app
import admin_app

TEST_DB_PATH = Path(__file__).resolve().parent / "test_attendance.db"

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """
    テスト全体で1回だけ実行される初期設定。
    本番のDBを汚さないように、テスト用の「test_attendance.db」を作成して
    アプリの接続先をすり替えます。
    """
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    
    conn = sqlite3.connect(TEST_DB_PATH)
    # 本番同様のテーブルを作成
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            user_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS scan_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            scan_type TEXT NOT NULL,
            scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'success',
            error_message TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS attendances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            work_date DATE NOT NULL,
            check_in_time TIMESTAMP,
            check_out_time TIMESTAMP,
            status TEXT DEFAULT 'working',
            UNIQUE(user_id, work_date)
        )
    ''')
    conn.commit()
    conn.close()

    # == ここが重要 ==
    # in_app.py と admin_app.py の DB_PATH をテスト用DBに書き換える (Monkeypatch)
    original_in_db = in_app.DB_PATH
    original_admin_db = admin_app.DB_PATH
    
    in_app.DB_PATH = TEST_DB_PATH
    admin_app.DB_PATH = TEST_DB_PATH

    yield # テスト実行

    # テスト終了後に元に戻す
    in_app.DB_PATH = original_in_db
    admin_app.DB_PATH = original_admin_db


@pytest.fixture
def in_client():
    """バックエンドテスト用の仮想クライアント（出勤アプリ用）"""
    in_app.app.config['TESTING'] = True
    with in_app.app.test_client() as client:
        yield client


@pytest.fixture
def admin_client():
    """バックエンドテスト用の仮想クライアント（管理アプリ用）"""
    admin_app.app.config['TESTING'] = True
    with admin_app.app.test_client() as client:
        yield client


import threading
from werkzeug.serving import make_server

class TestServerThread(threading.Thread):
    def __init__(self, app, host='127.0.0.1', port=5005):
        threading.Thread.__init__(self)
        self.server = make_server(host, port, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()

@pytest.fixture(scope="session")
def live_server_in_app():
    """Playwright(E2E)が裏でアクセスするためのFlaskサーバーをスレッドで起動する"""
    server_thread = TestServerThread(in_app.app)
    server_thread.start()
    time.sleep(1) # サーバーが立ち上がるのを少し待つ
    
    yield "http://127.0.0.1:5005"
    
    server_thread.shutdown()
    server_thread.join()
