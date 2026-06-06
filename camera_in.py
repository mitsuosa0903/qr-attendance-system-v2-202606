import cv2
import sqlite3
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "db" / "attendance.db"

latest_status = {
    "message": "入館カメラ起動準備中...",
    "type": "info",
    "updated_at": datetime.now().isoformat()
}

last_scan = {
    "qr_data": None,
    "time": datetime.min
}
COOLDOWN_SECONDS = 5

def update_status(message, msg_type="info"):
    global latest_status
    latest_status = {
        "message": message,
        "type": msg_type,
        "updated_at": datetime.now().isoformat()
    }
    print(f"[{msg_type.upper()}] {message}")

def get_latest_status():
    global latest_status
    return latest_status

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def process_qr_data(qr_data):
    global last_scan
    
    now = datetime.now()
    if last_scan["qr_data"] == qr_data and (now - last_scan["time"]).total_seconds() < COOLDOWN_SECONDS:
        return

    last_scan["qr_data"] = qr_data
    last_scan["time"] = now

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # デファルトのカメラログ
        cursor.execute("INSERT INTO camera_logs (detected_qr) VALUES (?)", (qr_data,))

        # ユーザー存在チェック
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (qr_data,))
        user = cursor.fetchone()

        if not user:
            conn.commit()
            update_status(f"未登録のQRコードです (ID: {qr_data[:10]}...)", "error")
            return

        user_name = user["user_name"]
        
        # scan_logsに記録 ('IN')
        cursor.execute("""
            INSERT INTO scan_logs (user_id, scan_time, scan_type)
            VALUES (?, ?, 'IN')
        """, (qr_data, now.strftime('%Y-%m-%d %H:%M:%S')))
        
        conn.commit()
        update_status(f"【入館】{user_name}さん 入館しました", "success")

    except Exception as e:
        print(f"Error processing QR data: {e}")
        update_status("システムエラーが発生しました", "error")
    finally:
        conn.close()

def generate_frames():
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        update_status("カメラの起動に失敗しました。接続を確認してください。", "error")
        return

    qr_decoder = cv2.QRCodeDetector()
    update_status("入館用端末です。QRコードをかざしてください", "info")

    while True:
        success, frame = camera.read()
        if not success:
            break
        
        frame = cv2.flip(frame, 1)

        try:
            data, bbox, straight_qrcode = qr_decoder.detectAndDecode(frame)
            if bbox is not None:
                n = len(bbox)
                for j in range(n):
                    pt1 = tuple(map(int, bbox[j][0]))
                    pt2 = tuple(map(int, bbox[(j+1) % n][0]))
                    cv2.line(frame, pt1, pt2, (0, 255, 0), 3)

                if data:
                    pt1 = tuple(map(int, bbox[0][0]))
                    cv2.putText(frame, data, (pt1[0], pt1[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    process_qr_data(data)
        except Exception as e:
            pass 

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    camera.release()
