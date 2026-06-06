import sqlite3
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "db"
DB_PATH = DB_DIR / "attendance.db"

def init_db():
    if not DB_DIR.exists():
        DB_DIR.mkdir(parents=True)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # ユーザーテーブル
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        user_name TEXT NOT NULL,
        created_at DATETIME DEFAULT (datetime('now', 'localtime'))
    )
    """)
    
    # 勤怠テーブル
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendances (
        attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        work_date TEXT NOT NULL,
        check_in_time DATETIME NOT NULL,
        check_out_time DATETIME,
        status TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)
    
    # カメラログ
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS camera_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        detected_qr TEXT NOT NULL,
        detected_time DATETIME DEFAULT (datetime('now', 'localtime'))
    )
    """)
    
    # スキャンログ (入退館の生データ)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scan_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        scan_time DATETIME DEFAULT (datetime('now', 'localtime')),
        scan_type TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ データベースの初期化が完了しました: {DB_PATH}")

if __name__ == "__main__":
    init_db()
