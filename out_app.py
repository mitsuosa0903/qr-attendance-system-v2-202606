from flask import Flask, render_template, jsonify, Response, request, send_file
import sqlite3
import os
from pathlib import Path
from camera_out import generate_frames, get_latest_status
from generate_qr import generate_qr

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "db" / "attendance.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return render_template("index_out.html")

@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/api/status")
def status_api():
    return jsonify(get_latest_status())

@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    message = ""
    status_type = "info"
    qr_user_id = None

    if request.method == "POST":
        user_id = request.form.get("user_id")
        user_name = request.form.get("user_name")

        if user_id and user_name:
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO users (user_id, user_name) VALUES (?, ?)",
                    (user_id, user_name)
                )
                conn.commit()

                qr_dir = BASE_DIR / "qrcodes"
                generate_qr(user_id, output_dir=str(qr_dir))

                message = f"✅ 登録完了: {user_name} さん (ID: {user_id})　QRコードを生成しました！"
                status_type = "success"
                qr_user_id = user_id

            except sqlite3.IntegrityError:
                message = f"⚠️ エラー: 社員ID「{user_id}」はすでに登録されています。"
                status_type = "error"
            except Exception as e:
                message = f"⚠️ エラーが発生しました: {str(e)}"
                status_type = "error"
            finally:
                conn.close()
        else:
            message = "⚠️ エラー: 社員IDと名前を両方入力してください。"
            status_type = "error"

    return render_template("add_user.html", message=message, status_type=status_type, qr_user_id=qr_user_id)

@app.route("/qr_download/<user_id>")
def qr_download(user_id):
    qr_path = BASE_DIR / "qrcodes" / f"user_{user_id}.png"
    if qr_path.exists():
        return send_file(str(qr_path), as_attachment=True, download_name=f"QR_{user_id}.png")
    return "QRコードが見つかりません", 404

@app.route("/qr_preview/<user_id>")
def qr_preview(user_id):
    qr_path = BASE_DIR / "qrcodes" / f"user_{user_id}.png"
    if qr_path.exists():
        return send_file(str(qr_path), mimetype="image/png")
    return "QRコードが見つかりません", 404

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002, debug=False, threaded=True)
