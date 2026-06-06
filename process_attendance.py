import sqlite3
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "db" / "attendance.db"

def process_attendance():
    print("--- 勤怠集計処理を開始します ---")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 一旦 attendances テーブルをクリアして scan_logs から完全再計算を行う
    cursor.execute("DELETE FROM attendances")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='attendances'")
    
    # scan_logs を取得
    cursor.execute("""
        SELECT log_id, user_id, scan_time, scan_type 
        FROM scan_logs 
        ORDER BY user_id, scan_time
    """)
    logs = cursor.fetchall()
    
    # ユーザーごとにログを分類
    user_logs = {}
    for log in logs:
        uid = log["user_id"]
        if uid not in user_logs:
            user_logs[uid] = []
        user_logs[uid].append(log)
        
    inserted_count = 0
    
    # IN -> 次の OUT をペアとして attendances にインサート
    for user_id, u_logs in user_logs.items():
        current_in = None
        
        for log in u_logs:
            if log["scan_type"] == "IN":
                # すでにINがある状態での2回目のINは無視する（最初のINを採用）
                if current_in is None:
                    current_in = log
            
            elif log["scan_type"] == "OUT":
                # INが存在する場合のみ、OUTと結びつけてペアにする
                if current_in is not None:
                    work_date = current_in["scan_time"].split(" ")[0] # YYYY-MM-DD
                    check_in_time = current_in["scan_time"]
                    check_out_time = log["scan_time"]
                    
                    cursor.execute("""
                        INSERT INTO attendances (user_id, work_date, check_in_time, check_out_time, status)
                        VALUES (?, ?, ?, ?, 'FINISHED')
                    """, (user_id, work_date, check_in_time, check_out_time))
                    
                    inserted_count += 1
                    print(f"✅ {user_id} の勤怠作成: IN {check_in_time} -> OUT {check_out_time}")
                    
                    # ペア成立後は状態をリセットし、次のINを待つ
                    current_in = None

    conn.commit()
    conn.close()
    print(f"--- 処理完了: 計 {inserted_count} 件の出退勤データが作成されました ---")

if __name__ == "__main__":
    process_attendance()
