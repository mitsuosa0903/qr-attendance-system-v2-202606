import sqlite3
from pathlib import Path

# =========================
# DBパス設定
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "attendance.db"

def insert_test_user(user_id: str, user_name: str):
    """
    テストユーザーを登録する
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO users (user_id, user_name)
        VALUES (?, ?)
        """, (user_id, user_name))

        conn.commit()
        print("✅ テストユーザー登録完了")
        print(f"ユーザーID: {user_id}")
        print(f"ユーザー名: {user_name}")

    except sqlite3.IntegrityError as e:
        print("⚠️ 登録失敗（すでに存在する可能性あり）")
        print(e)

    finally:
        conn.close()

if __name__ == "__main__":
    # -------------------------
    # テスト用ユーザー
    # -------------------------
    insert_test_user(
        user_id="EMP001",
        user_name="テストユーザー"
    )
    
    insert_test_user(
        user_id="EMP002",
        user_name="鈴木一郎"
    )
