from flask import Flask, render_template, send_file, redirect, url_for, flash
import sqlite3
from pathlib import Path
from process_attendance import process_attendance
import datetime
import os
from generate_qr import generate_qr
app = Flask(__name__)
app.secret_key = "secret_key_for_flash_messages"

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "db" / "attendance.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    # アクセスされるたびに、最新のログをattendancesテーブルにペアとして集計し直す
    process_attendance()

    conn = get_db_connection()
    
    # === 1. 登録済みユーザー一覧 (最新順) ===
    users = conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
    
    # === 2. 本日の出退勤一覧 (ペア集計済みデータ) ===
    attendances = conn.execute("""
        SELECT a.work_date, a.check_in_time, a.check_out_time, a.status, u.user_id, u.user_name
        FROM attendances a
        JOIN users u ON a.user_id = u.user_id
        ORDER BY a.check_in_time DESC
    """).fetchall()
    
    # === 3. 生の打刻ログ (最新50件) ===
    logs = conn.execute("""
        SELECT s.scan_time, s.scan_type, u.user_id, u.user_name
        FROM scan_logs s
        JOIN users u ON s.user_id = u.user_id
        ORDER BY s.scan_time DESC
        LIMIT 50
    """).fetchall()

    conn.close()

    return render_template("admin.html", users=users, attendances=attendances, logs=logs)

@app.route("/qr_download/<user_id>")
def qr_download(user_id):
    qr_dir = BASE_DIR / "qrcodes"
    if not qr_dir.exists():
        qr_dir.mkdir(parents=True)
        
    qr_path = qr_dir / f"user_{user_id}.png"
    
    # QRコードファイルが存在しない場合は、ここで再生成する
    if not qr_path.exists():
        generate_qr(user_id, output_dir=str(qr_dir))
        
    if qr_path.exists():
        return send_file(str(qr_path), as_attachment=True, download_name=f"QR_{user_id}.png")
    return "QRコードが見つかりません", 404

@app.route("/delete_user/<user_id>", methods=["POST"])
def delete_user(user_id):
    conn = get_db_connection()
    try:
        # ユーザー削除 (カスケード設定がない場合は、関連ログも考慮する必要があるが、
        # 今回はシンプルにユーザーのみ削除。必要に応じてログも消す設計にする)
        conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        # 関連する打刻ログや勤怠データも削除する場合：
        conn.execute("DELETE FROM scan_logs WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM attendances WHERE user_id = ?", (user_id,))
        conn.commit()
        
        # QRコードファイルの削除
        qr_path = BASE_DIR / "qrcodes" / f"user_{user_id}.png"
        if qr_path.exists():
            os.remove(qr_path)
            
        flash(f"ユーザー {user_id} を削除しました。")
    except Exception as e:
        flash(f"エラーが発生しました: {str(e)}")
    finally:
        conn.close()
        
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5003, debug=False, threaded=True)
